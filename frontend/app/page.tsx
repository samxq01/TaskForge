'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  CheckCircle2,
  Clock,
  GitBranch,
  Layers,
  Sparkles,
  Zap,
  Cpu,
  BarChart3,
  Calendar,
  AlertTriangle,
  Flame,
  Check,
  ChevronRight,
} from 'lucide-react';
import { api, Overview, Task } from '@/lib/api-client';

export default function LandingPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [topTask, setTopTask] = useState<Task | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const ov = await api.getOverview();
        setOverview(ov);
        if (ov.recommended_task_id) {
          const t = await api.getTask(ov.recommended_task_id);
          setTopTask(t);
        }
      } catch (err) {
        console.error('Could not load live preview data', err);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-24 py-12 md:py-20">
      {/* ------------------------------------------------------------- */}
      {/* 1. HERO SECTION */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Headline & Calls to Action */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-blue-50/90 border border-blue-200 text-[11px] font-sans font-bold tracking-wider text-brand uppercase">
              <span className="w-2 h-2 rounded-full bg-brand animate-pulse" />
              INTELLIGENT TASK SCHEDULING SYSTEM
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-sans font-extrabold text-slate-900 leading-[1.12] tracking-tight">
              Plan smarter.<br />
              <span className="text-brand">Work in the right order.</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
              Manage tasks, understand dependencies, evaluate data structures, and explore project schedules in one intelligent, algorithmically driven workspace.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 bg-brand hover:bg-brand-hover text-white px-6 py-3.5 rounded-xl font-semibold text-sm shadow-md transition-all hover:shadow-lg hover:-translate-y-0.5"
              >
                <span>Open Task Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/laboratory"
                className="inline-flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 px-6 py-3.5 rounded-xl font-semibold text-sm transition-all hover:border-slate-300"
              >
                <span>Explore DSA Labs</span>
                <Cpu className="w-4 h-4 text-slate-500" />
              </Link>
            </div>

            {/* Quick Proof Pills */}
            <div className="pt-4 flex flex-wrap gap-2 text-xs font-sans text-slate-600">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 font-medium text-slate-700 shadow-xs">
                <Check className="w-3.5 h-3.5 text-emerald-600" /> 213 Pytest Tests Verified
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 font-medium text-slate-700 shadow-xs">
                <Check className="w-3.5 h-3.5 text-emerald-600" /> Zero 3rd-Party DSA Libs
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 font-medium text-slate-700 shadow-xs">
                <Check className="w-3.5 h-3.5 text-emerald-600" /> Non-Persistent What-If
              </span>
            </div>
          </div>

          {/* Right Column: Live Interactive Workspace Preview */}
          <div className="lg:col-span-5">
            <div className="pt-card p-6 shadow-xl border-slate-200 relative overflow-hidden bg-white">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-2xl pointer-events-none" />

              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-400" />
                  <span className="w-3 h-3 rounded-full bg-amber-400" />
                  <span className="w-3 h-3 rounded-full bg-emerald-400" />
                  <span className="text-xs font-mono text-slate-400 pl-2">live-engine.py</span>
                </div>
                <span className="pt-pill pt-pill-blue">
                  <span className="pt-dot pt-dot-blue" />
                  MIN-HEAP TOP RANK
                </span>
              </div>

              <div className="mt-4 space-y-4">
                {topTask ? (
                  <div className="p-4 rounded-lg bg-blue-50/60 border border-blue-200/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-brand">
                        TASK #{topTask.id}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white border border-blue-200 text-blue-700">
                        {topTask.priority_label}
                      </span>
                    </div>
                    <h3 className="font-display font-bold text-slate-900 text-base">
                      {topTask.title}
                    </h3>
                    <p className="text-xs text-slate-600 line-clamp-2">
                      {topTask.description || 'Prerequisites satisfied. Eligible for execution.'}
                    </p>
                    <div className="pt-2 flex items-center justify-between text-[0.72rem] font-mono text-slate-500 border-t border-blue-200/50">
                      <span>⏱️ {topTask.duration_formatted}</span>
                      <span>🗓️ {topTask.due_date_formatted}</span>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                    <span className="text-xs font-mono text-slate-500">ENGINE STATUS</span>
                    <h3 className="font-display font-bold text-slate-800 text-base">
                      Ready for Task Dispatch
                    </h3>
                    <p className="text-xs text-slate-500">
                      Connect to local FastAPI or add tasks to see automated min-heap ranking.
                    </p>
                  </div>
                )}

                {/* Micro Metric Preview */}
                <div className="grid grid-cols-3 gap-2 text-center pt-2">
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                    <div className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-400">Total</div>
                    <div className="font-sans font-extrabold text-2xl text-slate-900 tracking-tight tabular-nums mt-0.5">
                      {overview?.total_tasks ?? 0}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-100">
                    <div className="text-[11px] font-sans font-bold uppercase tracking-wider text-emerald-600">Pending</div>
                    <div className="font-sans font-extrabold text-2xl text-emerald-700 tracking-tight tabular-nums mt-0.5">
                      {overview?.pending_tasks ?? 0}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-blue-50/70 border border-blue-100">
                    <div className="text-[11px] font-sans font-bold uppercase tracking-wider text-brand">BST Nodes</div>
                    <div className="font-sans font-extrabold text-2xl text-brand tracking-tight tabular-nums mt-0.5">
                      {overview?.bst_nodes ?? 0}
                    </div>
                  </div>
                </div>

                <Link
                  href="/dashboard"
                  className="block w-full py-2.5 text-center rounded-lg bg-slate-900 hover:bg-brand text-white text-xs font-semibold transition-colors"
                >
                  Enter Workspace &rarr;
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------- */}
      {/* 2. FIVE CORE CAPABILITY MODULES */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="pt-pill pt-pill-blue">PRODUCT MODULES</span>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-slate-900">
            Engineered from fundamental computer science.
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Every feature in TaskForge is built on custom-crafted algorithms and data structures without relying on third-party libraries.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Task Management */}
          <Link href="/tasks" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-brand mb-4 group-hover:scale-110 transition-transform">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <span className="text-[0.7rem] font-mono font-semibold text-brand uppercase tracking-wider">
              Module 01 &bull; CO1
            </span>
            <h3 className="text-lg font-display font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Task Operations &amp; History
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Full CRUD management with session-local dual-stack Undo/Redo (LIFO) and FIFO pending queue processing.
            </p>
          </Link>

          {/* Card 2: Algorithm Lab */}
          <Link href="/laboratory" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 mb-4 group-hover:scale-110 transition-transform">
              <Cpu className="w-5 h-5" />
            </div>
            <span className="text-[0.7rem] font-mono font-semibold text-amber-600 uppercase tracking-wider">
              Module 02 &bull; CO2 / CO3 / CO4
            </span>
            <h3 className="text-lg font-display font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              DSA Performance Laboratory
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              High-precision microsecond benchmarks comparing Linear vs. Binary search, Insertion vs. Merge sort, and Custom Hash Table bucket inspection.
            </p>
          </Link>

          {/* Card 3: Dependency Planning */}
          <Link href="/dependencies" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 mb-4 group-hover:scale-110 transition-transform">
              <GitBranch className="w-5 h-5" />
            </div>
            <span className="text-[0.7rem] font-mono font-semibold text-indigo-600 uppercase tracking-wider">
              Module 03 &bull; CO5
            </span>
            <h3 className="text-lg font-display font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Dependency Graph &amp; Cycles
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Interactive directed acyclic graph visualizer. Pre-validates relationships to reject circular dependencies with topological sorting.
            </p>
          </Link>

          {/* Card 4: Intelligent Scheduling */}
          <Link href="/scheduling" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mb-4 group-hover:scale-110 transition-transform">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="text-[0.7rem] font-mono font-semibold text-emerald-600 uppercase tracking-wider">
              Module 04 &bull; CO1 / CO5
            </span>
            <h3 className="text-lg font-display font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Smart Auto-Scheduler
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Binary Min-Heap priority queue evaluating only eligible pending tasks. Accompanied by a rule-based Deadline Risk Analyzer.
            </p>
          </Link>

          {/* Card 5: Critical Path Planning */}
          <Link href="/planning" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 mb-4 group-hover:scale-110 transition-transform">
              <Calendar className="w-5 h-5" />
            </div>
            <span className="text-[0.7rem] font-mono font-semibold text-rose-600 uppercase tracking-wider">
              Module 05 &bull; CO5
            </span>
            <h3 className="text-lg font-display font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Critical Path &amp; What-If
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Dynamic programming across DAG topological order to compute earliest finish times and project duration, with non-persistent delay simulations.
            </p>
          </Link>

          {/* Card 6: Fallback Streamlit */}
          <div className="pt-card p-6 bg-slate-900 text-white flex flex-col justify-between">
            <div>
              <span className="text-[0.7rem] font-mono font-semibold text-blue-400 uppercase tracking-wider">
                System Integration
              </span>
              <h3 className="text-lg font-display font-bold mt-1 mb-2">
                Dual Frontend Architecture
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Enjoy this modern Next.js frontend or launch the original Streamlit application at any time with complete data synchronization.
              </p>
            </div>
            <div className="pt-4 font-mono text-[0.75rem] text-slate-400 bg-slate-800/80 p-2.5 rounded border border-slate-700">
              streamlit run app.py
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------- */}
      {/* 3. INTERACTIVE 5-STEP WORKFLOW */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="pt-pill pt-pill-blue">HOW IT WORKS</span>
          <h2 className="text-3xl font-display font-bold text-slate-900">
            From creation to execution.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { step: '01', title: 'Create Tasks', desc: 'Define title, duration, deadline, and priority.', link: '/tasks' },
            { step: '02', title: 'Map Precedence', desc: 'Enforce DAG dependencies with cycle protection.', link: '/dependencies' },
            { step: '03', title: 'Heap Ranking', desc: 'Min-Heap extracts the optimal next action item.', link: '/scheduling' },
            { step: '04', title: 'Analyze Risks', desc: 'Classify tasks by deadline slack and blocking status.', link: '/scheduling' },
            { step: '05', title: 'What-If Simulation', desc: 'Simulate delay impact in-memory with zero persistence.', link: '/planning' },
          ].map((item, idx) => (
            <Link
              key={item.step}
              href={item.link}
              className="pt-card p-5 group hover:border-brand transition-all block"
            >
              <div className="text-2xl font-display font-extrabold text-slate-300 group-hover:text-brand transition-colors mb-2">
                {item.step}
              </div>
              <h4 className="font-display font-bold text-slate-900 text-sm mb-1 group-hover:text-brand transition-colors">
                {item.title}
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                {item.desc}
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* ------------------------------------------------------------- */}
      {/* 4. PRODUCT PROOF */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-12 shadow-sm space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <span className="pt-pill pt-pill-green">
                <span className="pt-dot pt-dot-green" />
                VERIFIED ACADEMIC RIGOR
              </span>
              <h2 className="text-2xl sm:text-3xl font-display font-bold text-slate-900">
                100% Custom Implementation
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                TaskForge was built from first principles for Data Structures &amp; Algorithms course outcomes. No black-box frameworks, no fabricated benchmark graphs.
              </p>
              <ul className="space-y-2 text-xs font-mono text-slate-700">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand" /> Custom Stack &amp; Queue with pointer-based nodes
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand" /> Separate chaining Hash Table with dynamic rehashing
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand" /> Binary Search Tree with Inorder, Preorder, Postorder
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand" /> Directed Graph with Kahn's topological sort and DFS cycle check
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand" /> Binary Min-Heap Priority Queue for deterministic ranking
                </li>
              </ul>
            </div>

            <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 space-y-4 font-mono text-xs">
              <div className="text-slate-400 uppercase tracking-widest text-[0.68rem] border-b border-slate-200 pb-2">
                Course Outcome Mapping
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-800">CO1 Stacks &amp; Queues</span>
                  <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">100%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-800">CO2 Storage &amp; Hash Table</span>
                  <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">100%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-800">CO3 Binary Search Trees</span>
                  <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">100%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-800">CO4 Searching &amp; Sorting</span>
                  <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">100%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-800">CO5 Graphs &amp; Critical Path</span>
                  <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">100%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

