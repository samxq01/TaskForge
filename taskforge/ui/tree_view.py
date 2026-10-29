"""Binary Search Tree Task Index UI module for Course Outcome 4 (CO4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_index import TaskIndexService, make_deadline_key, make_search_key
from taskforge.storage import TaskStorage
from taskforge.structures.bst import BinarySearchTree, TreeNode
from taskforge.ui.theme import render_metric_strip, render_pill, render_section_header


def _format_node_key(key: tuple[int, datetime, int]) -> str:
    """Format composite key for display."""
    has_no_dl, dl_val, task_id = key
    if has_no_dl == 1:
        return f"[No Deadline, ID: #{task_id}]"
    return f"[{dl_val.strftime('%Y-%m-%d %H:%M')}, ID: #{task_id}]"


def _generate_tree_text_diagram(node: Optional[TreeNode[Any, Task]], prefix: str = "", is_left: bool = True) -> list[str]:
    """Generate a clean depth-indented ASCII tree representation."""
    if node is None:
        return []

    lines: list[str] = []
    connector = "├── (L) " if is_left else "└── (R) "
    if not prefix:
        connector = "● [ROOT] "

    key_str = _format_node_key(node.key)
    task_str = f"Task #{node.value.id}: '{node.value.title}' ({node.value.priority_label})"
    lines.append(f"{prefix}{connector}{key_str} -> {task_str}")

    new_prefix = prefix + ("│   " if is_left else "    ")
    if node.left or node.right:
        if node.left:
            lines.extend(_generate_tree_text_diagram(node.left, new_prefix, is_left=True))
        else:
            lines.append(f"{new_prefix}├── (L) <empty>")

        if node.right:
            lines.extend(_generate_tree_text_diagram(node.right, new_prefix, is_left=False))
        else:
            lines.append(f"{new_prefix}└── (R) <empty>")

    return lines


def render_tree_view(storage: TaskStorage, index_service: TaskIndexService) -> None:
    """Render the full BST Task Index interface for CO4."""
    render_section_header(
        eyebrow="COURSE OUTCOME 4 (CO4) • TREE STRUCTURES",
        title="Binary Search Tree Task Index",
        subtitle="Indexes tasks in-memory by deadline using a composite key (has_deadline, normalized_timestamp, id). Demonstrates logarithmic search, tree traversals, and chronological ordering.",
    )

    # Rebuild index from current database records
    index_service.rebuild()
    raw_bst = index_service.get_raw_bst()

    # Overview Metric Strip
    root_key = _format_node_key(raw_bst.root.key) if raw_bst.root else "None"
    render_metric_strip([
        {"label": "Total Indexed Nodes", "value": f"{index_service.get_tree_size()} tasks", "caption": "In-Memory Tree"},
        {"label": "Tree Height (Depth)", "value": str(index_service.get_tree_height()), "caption": "Subtree Max Depth"},
        {"label": "Root Node Key", "value": root_key, "caption": "BST Anchor Node"},
        {"label": "Search Complexity", "value": "O(log n) avg", "caption": "O(n) worst if skewed"},
    ])

    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if st.button("🔄 Rebuild / Refresh Index", use_container_width=True):
            index_service.rebuild()
            st.success("BST index rebuilt from SQLite.")
            st.rerun()

    st.markdown("<hr style='margin: 1.2rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    if index_service.is_empty():
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 2rem; text-align: center; color: #64748B;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; color: #0F172A; margin-bottom: 0.35rem;">The Binary Search Tree is currently empty.</div>
                <div>Create tasks with deadlines in the Dashboard or click 'Load Sample Tasks' in the sidebar to populate the tree index.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    tab_inorder, tab_search, tab_traversals, tab_diagram = st.tabs(
        [
            "📋 Inorder Traversal (Deadline Order)",
            "🔍 BST Key Search",
            "🔄 Traversal Laboratory",
            "🌳 Visual Tree Structure",
        ]
    )

    # ---------------- TAB 1: INORDER DEADLINE RETRIEVAL ----------------
    with tab_inorder:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Inorder Traversal — Sorted Chronological Retrieval
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                An Inorder traversal (<code>Left ➔ Root ➔ Right</code>) guarantees extraction of tasks in strictly ascending chronological order in <code>O(n)</code> linear time.
            </div>
            """,
            unsafe_allow_html=True,
        )

        ordered_tasks = index_service.get_deadline_ordered_tasks()
        st.markdown(
            f"""
            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 0.8rem 1.2rem; margin-bottom: 1rem; font-size: 0.88rem; color: #2563EB;">
                ● Extracted <strong>{len(ordered_tasks)}</strong> task(s) in sorted deadline sequence directly from BST Inorder Traversal.
            </div>
            """,
            unsafe_allow_html=True,
        )

        inorder_table = [
            {
                "Seq": f"#{idx}",
                "ID": f"#{task.id}",
                "Title": task.title,
                "Deadline": task.formatted_deadline,
                "Priority": task.priority_label,
                "Duration": f"{task.duration}m",
                "Status": task.status,
            }
            for idx, task in enumerate(ordered_tasks, start=1)
        ]
        st.dataframe(inorder_table, use_container_width=True, hide_index=True)

    # ---------------- TAB 2: BST KEY SEARCH ----------------
    with tab_search:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Exact Key Search in Binary Search Tree
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Search invokes <code>bst.search(composite_key)</code> with <code>O(log n)</code> average time complexity.
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_tasks = storage.list_tasks()
        selected_task_label = st.selectbox(
            "Select target task to locate in the BST index:",
            options=all_tasks,
            format_func=lambda t: f"Task #{t.id}: '{t.title}' | Deadline: {t.formatted_deadline}",
        )

        if st.button("🔎 Execute BST Search", type="primary", use_container_width=True):
            if selected_task_label:
                search_key = make_deadline_key(selected_task_label)
                found_task = raw_bst.search(search_key)

                if found_task:
                    st.markdown(
                        f"""
                        <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 8px; padding: 1.2rem 1.4rem; margin-top: 1rem; box-shadow: 0 1px 3px rgba(37,99,235,0.06);">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #2563EB; font-weight: 700; margin-bottom: 0.3rem;">
                                ● Match Found in BST Index
                            </div>
                            <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem;">
                                Task #{found_task.id}: {found_task.title}
                            </div>
                            <div style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
                                Composite Key: <code style="color: #2563EB;">{_format_node_key(search_key)}</code><br>
                                Deadline: <strong style="color: #0F172A;">{found_task.formatted_deadline}</strong> &bull; Priority: <strong style="color: #0F172A;">{found_task.priority_label}</strong> &bull; Duration: <strong style="color: #0F172A;">{found_task.duration}m</strong> &bull; Status: <strong style="color: #0F172A;">{found_task.status}</strong>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("Key not found in BST index.")

        st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem;">Test Non-Existent Key Search</div>', unsafe_allow_html=True)
        col_ne1, col_ne2 = st.columns([3, 1])
        with col_ne1:
            dummy_id = st.number_input("Enter Non-Existent Task ID", min_value=9000, value=9999)
        with col_ne2:
            st.write("")
            st.write("")
            if st.button("Search Missing Key", use_container_width=True):
                dummy_key = make_search_key(datetime(2030, 1, 1), dummy_id)
                res = raw_bst.search(dummy_key)
                if res is None:
                    st.info(f"ℹ️ As expected, `search({_format_node_key(dummy_key)})` returned `None` safely without error.")

    # ---------------- TAB 3: TRAVERSAL LABORATORY ----------------
    with tab_traversals:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Tree Traversal Laboratory
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Compare recursive tree exploration strategies in <code>O(n)</code> linear time.
            </div>
            """,
            unsafe_allow_html=True,
        )

        trav_mode = st.radio(
            "Select Traversal Strategy:",
            ["Inorder Traversal", "Preorder Traversal", "Postorder Traversal"],
            horizontal=True,
        )

        if trav_mode == "Inorder Traversal":
            entries = index_service.get_inorder_entries()
            order_name = "Inorder (Sorted Ascending Keys)"
        elif trav_mode == "Preorder Traversal":
            entries = index_service.get_preorder_entries()
            order_name = "Preorder (Root First, Tree Cloning Order)"
        else:
            entries = index_service.get_postorder_entries()
            order_name = "Postorder (Leaves First, Subtree Deletion Order)"

        st.markdown(f"#### Traversal Sequence: **{order_name}**")
        seq_items = [f"#{t.id} ('{t.title}')" for _, t in entries]
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.9rem 1.1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #2563EB; margin-bottom: 1rem;">
                {' ➔ '.join(seq_items)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        trav_rows = [
            {
                "Step": f"#{step}",
                "Composite Key": _format_node_key(key),
                "Task": f"#{task.id} {task.title}",
                "Priority": task.priority_label,
            }
            for step, (key, task) in enumerate(entries, start=1)
        ]
        st.dataframe(trav_rows, use_container_width=True, hide_index=True)

    # ---------------- TAB 4: TREE STRUCTURE VISUALIZATION ----------------
    with tab_diagram:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Hierarchical Branching Structure
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Tree topology displaying Root, Left subtrees (<code>&lt; parent</code>), and Right subtrees (<code>&gt; parent</code>).
            </div>
            """,
            unsafe_allow_html=True,
        )

        tree_lines = _generate_tree_text_diagram(raw_bst.root)
        if not tree_lines:
            st.info("Tree is empty.")
        else:
            tree_text = "\n".join(tree_lines)
            st.code(tree_text, language="text")

        st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.6rem;">Structural Properties & Balance Analysis</div>', unsafe_allow_html=True)
        col_prop1, col_prop2 = st.columns(2)
        with col_prop1:
            st.markdown(f"- **Total Nodes ($N$):** `{index_service.get_tree_size()}`")
            st.markdown(f"- **Actual Tree Height:** `{index_service.get_tree_height()}`")
        with col_prop2:
            min_possible_height = (index_service.get_tree_size() - 1).bit_length() - 1 if index_service.get_tree_size() > 0 else 0
            st.markdown(f"- **Optimal Balanced Height ($\\lfloor \\log_2 N \\rfloor$):** `{min_possible_height}`")
            is_skewed = index_service.get_tree_height() > (min_possible_height + 2)
            skew_status = "⚠️ Skewed Tree" if is_skewed else "✅ Balanced Tree"
            st.markdown(f"- **Balance Assessment:** `{skew_status}`")
