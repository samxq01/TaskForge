"""Binary Search Tree Task Index UI module for Course Outcome 4 (CO4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_index import TaskIndexService, make_deadline_key, make_search_key
from taskforge.storage import TaskStorage
from taskforge.structures.bst import BinarySearchTree, TreeNode


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
        connector = "🌟 [ROOT] "

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
    st.markdown("## 🌲 Binary Search Tree (BST) Task Index (CO4)")
    st.markdown(
        """
        > **Course Outcome 4 (CO4):** *Develop tree structure for solving engineering problems.*
        
        This module implements a **custom Binary Search Tree** that indexes tasks by deadline using a composite key:
        `key = (has_no_deadline_flag, normalized_deadline, task_id)`
        - **Inorder Traversal ($O(n)$):** Guarantees retrieval of all tasks in strictly ascending deadline order.
        - **Logarithmic Search ($O(\\log n)$ avg):** Fast task lookup by deadline key.
        - **Zero Database Modification:** The BST is an in-memory index built dynamically from persistent SQLite records.
        """
    )

    # Rebuild index from current database records
    index_service.rebuild()
    raw_bst = index_service.get_raw_bst()

    # Overview Metrics & Controls
    col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 2, 2])
    with col_m1:
        st.metric("Total Indexed Nodes", f"{index_service.get_tree_size()} tasks")
    with col_m2:
        st.metric("Tree Height (Depth)", f"{index_service.get_tree_height()}")
    with col_m3:
        root_key = _format_node_key(raw_bst.root.key) if raw_bst.root else "None"
        st.metric("Root Node Key", root_key)
    with col_m4:
        st.write("")
        st.write("")
        if st.button("🔄 Rebuild / Refresh Index", use_container_width=True):
            index_service.rebuild()
            st.success("BST index rebuilt from SQLite.")
            st.rerun()

    st.markdown("---")

    if index_service.is_empty():
        st.info("ℹ️ The Binary Search Tree is currently empty. Create tasks in the Dashboard or click 'Load Sample Tasks' in the sidebar.")
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
        st.markdown("### 📋 Inorder Traversal — Deadline-Ordered Retrieval")
        st.caption(
            "An Inorder traversal (Left $\\to$ Root $\\to$ Right) on a Binary Search Tree produces elements in strictly sorted order ($O(n)$ time)."
        )

        ordered_tasks = index_service.get_deadline_ordered_tasks()
        st.success(f"Extracted **{len(ordered_tasks)}** task(s) in sorted deadline order directly from BST Inorder Traversal.")

        header_cols = st.columns([1, 1, 4, 3, 2, 2, 2])
        header_cols[0].markdown("**Seq**")
        header_cols[1].markdown("**ID**")
        header_cols[2].markdown("**Title**")
        header_cols[3].markdown("**Deadline**")
        header_cols[4].markdown("**Priority**")
        header_cols[5].markdown("**Duration**")
        header_cols[6].markdown("**Status**")
        st.markdown("<hr style='margin: 0.3rem 0;'>", unsafe_allow_html=True)

        for idx, task in enumerate(ordered_tasks, start=1):
            cols = st.columns([1, 1, 4, 3, 2, 2, 2])
            cols[0].write(f"#{idx}")
            cols[1].write(f"#{task.id}")
            cols[2].write(task.title)
            cols[3].write(task.formatted_deadline)
            cols[4].write(task.priority_label)
            cols[5].write(f"{task.duration}m")
            cols[6].write(task.status)
            st.markdown("<hr style='margin: 0.2rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # ---------------- TAB 2: BST KEY SEARCH ----------------
    with tab_search:
        st.markdown("### 🔍 Exact Key Search in Binary Search Tree")
        st.markdown(
            """
            Search invokes `bst.search(composite_key)`.
            At each node $N$:
            - If target key equals $N.key$: Match found ($O(1)$)
            - If target key $< N.key$: Traverses left subtree
            - If target key $> N.key$: Traverses right subtree
            - Average search complexity: $O(\\log n)$.
            """
        )

        all_tasks = storage.list_tasks()
        selected_task_label = st.selectbox(
            "Select a target task to locate in the BST:",
            options=all_tasks,
            format_func=lambda t: f"Task #{t.id}: '{t.title}' | Deadline: {t.formatted_deadline}",
        )

        if st.button("🔎 Execute BST Search", type="primary", use_container_width=True):
            if selected_task_label:
                search_key = make_deadline_key(selected_task_label)
                found_task = raw_bst.search(search_key)

                if found_task:
                    st.success(f"✅ Found in BST via `search({_format_node_key(search_key)})`!")
                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        st.markdown(f"**Task ID:** #{found_task.id}")
                        st.markdown(f"**Title:** {found_task.title}")
                        st.markdown(f"**Description:** {found_task.description or 'None'}")
                    with res_col2:
                        st.markdown(f"**Deadline:** {found_task.formatted_deadline}")
                        st.markdown(f"**Priority:** {found_task.priority_label}")
                        st.markdown(f"**Duration:** {found_task.duration} minutes")
                        st.markdown(f"**Status:** {found_task.status}")
                else:
                    st.error("❌ Key not found in BST.")

        st.markdown("---")
        st.markdown("#### Test Non-Existent Key")
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
                    st.info(f"ℹ️ As expected, `search({_format_node_key(dummy_key)})` returned `None` without error.")

    # ---------------- TAB 3: TRAVERSAL LABORATORY ----------------
    with tab_traversals:
        st.markdown("### 🔄 Traversal Laboratory (Inorder vs. Preorder vs. Postorder)")
        st.markdown(
            """
            Tree traversals systematically visit every node in the BST ($O(n)$ time):
            - **Inorder (Left $\\to$ Root $\\to$ Right):** Produces keys in ascending sorted order.
            - **Preorder (Root $\\to$ Left $\\to$ Right):** Visits parent before children (used for tree serialization).
            - **Postorder (Left $\\to$ Right $\\to$ Root):** Visits children before parent (used for subtree evaluation and deletion).
            """
        )

        trav_mode = st.radio(
            "Select Traversal Strategy:",
            ["Inorder Traversal", "Preorder Traversal", "Postorder Traversal"],
            horizontal=True,
        )

        if trav_mode == "Inorder Traversal":
            entries = index_service.get_inorder_entries()
            order_name = "Inorder (Sorted Keys)"
        elif trav_mode == "Preorder Traversal":
            entries = index_service.get_preorder_entries()
            order_name = "Preorder (Root First)"
        else:
            entries = index_service.get_postorder_entries()
            order_name = "Postorder (Leaves First)"

        st.markdown(f"#### Traversal Sequence: **{order_name}**")
        seq_items = [f"#{t.id} ('{t.title}')" for _, t in entries]
        st.write(" ➔ ".join(seq_items))

        # Table of entries
        t_cols = st.columns([1, 4, 3, 2])
        t_cols[0].markdown("**Step**")
        t_cols[1].markdown("**Composite Key**")
        t_cols[2].markdown("**Task Title**")
        t_cols[3].markdown("**Priority**")
        st.markdown("<hr style='margin: 0.2rem 0;'>", unsafe_allow_html=True)

        for step, (key, task) in enumerate(entries, start=1):
            cols = st.columns([1, 4, 3, 2])
            cols[0].write(f"Step {step}")
            cols[1].code(_format_node_key(key))
            cols[2].write(f"#{task.id} {task.title}")
            cols[3].write(task.priority_label)

    # ---------------- TAB 4: TREE STRUCTURE VISUALIZATION ----------------
    with tab_diagram:
        st.markdown("### 🌳 Visual Hierarchy & Branching Structure")
        st.caption(
            "Hierarchical structural view showing the root node, left subtrees (< parent key), and right subtrees (> parent key)."
        )

        tree_lines = _generate_tree_text_diagram(raw_bst.root)
        if not tree_lines:
            st.info("Tree is empty.")
        else:
            tree_text = "\n".join(tree_lines)
            st.code(tree_text, language="text")

        st.markdown("---")
        st.markdown("#### 💡 Structural Properties & Skewness Analysis")
        col_prop1, col_prop2 = st.columns(2)
        with col_prop1:
            st.markdown(f"- **Total Nodes:** {index_service.get_tree_size()}")
            st.markdown(f"- **Tree Height:** {index_service.get_tree_height()}")
        with col_prop2:
            min_possible_height = (index_service.get_tree_size() - 1).bit_length() - 1 if index_service.get_tree_size() > 0 else 0
            st.markdown(f"- **Minimum Possible Height (if perfectly balanced):** {min_possible_height}")
            is_skewed = index_service.get_tree_height() > (min_possible_height + 2)
            st.markdown(f"- **Skewness Warning:** {'⚠️ Skewed Tree' if is_skewed else '✅ Reasonably Balanced'}")
