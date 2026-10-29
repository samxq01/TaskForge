'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  CheckCircle2,
  GitBranch,
  Calendar,
  Sparkles,
  Layers,
  Cpu,
  Clock,
  ShieldCheck,
  Check,
  FlaskConical,
} from 'lucide-react';
import { api, Overview, SmartScheduleResult, Task } from '@/lib/api-client';

export default function LandingPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [schedule, setSchedule] = useState<SmartScheduleResult | null>(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const [ov, sched] = await Promise.all([
          api.getOverview(),
          api.getSchedulingRecommendations(),
        ]);
        setOverview(ov);
        setSchedule(sched);
      } catch (err) {
        console.error('Failed to load live landing stats', err);
      }
    }
    loadStats();
  }, []);

  const topTask = schedule?.recommendation?.task;

  return (
    <div className="space-y-24 py-12 md:py-20">
      {/* ------------------------------------------------------------- */}
      {/* 1. HERO SECTION (Phase 2) */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Headline & Calls to Action */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-blue-50/90 border border-blue-200 text-[11px] font-sans font-bold tracking-wider text-brand uppercase">
              <span className="w-2 h-2 rounded-full bg-brand animate-pulse" />
              INTELLIGENT TASK MANAGEMENT SYSTEM
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-sans font-extrabold text-slate-900 leading-[1.12] tracking-tight">
              Plan work. Manage dependencies.<br />
              <span className="text-brand">Meet deadlines.</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
              An intelligent task management and project scheduling workspace. Understand what needs your attention now, which deadlines are approaching, and what is ready to be worked on.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 bg-brand hover:bg-brand-hover text-white px-6 py-3.5 rounded-xl font-semibold text-sm shadow-md transition-all hover:shadow-lg hover:-translate-y-0.5"
              >
                <span>Open Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/tasks"
                className="inline-flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 px-6 py-3.5 rounded-xl font-semibold text-sm transition-all hover:border-slate-300"
              >
                <span>View Tasks</span>
              </Link>
              <Link
                href="/laboratory"
                className="inline-flex items-center gap-2 text-slate-600 hover:text-brand px-3 py-3.5 font-semibold text-sm transition-colors"
              >
                <FlaskConical className="w-4 h-4" />
                <span>Technical Labs</span>
              </Link>
            </div>

            {/* Quick Proof Points */}
            <div className="pt-4 flex flex-wrap gap-2 text-xs font-sans text-slate-600">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 font-medium text-slate-700 shadow-xs">
                <Check className="w-3.5 h-3.5 text-emerald-600" /> Smart Priority Scheduling
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 font-medium text-slate-700 shadow-xs">
                <Check className="w-3.5 h-3.5 text-emerald-600" /> Cycle-Safe Dependencies
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 font-medium text-slate-700 shadow-xs">
                <Check className="w-3.5 h-3.5 text-emerald-600" /> Non-Persistent What-If Simulation
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
                  <span className="text-xs text-slate-400 pl-2 font-medium">TaskForge Dispatcher</span>
                </div>
                <span className="pt-pill pt-pill-blue">
                  <span className="pt-dot pt-dot-blue" />
                  RECOMMENDED NEXT TASK
                </span>
              </div>

              <div className="mt-4 space-y-4">
                {topTask ? (
                  <div className="p-4 rounded-lg bg-blue-50/60 border border-blue-200/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-brand">
                        TASK #{topTask.id}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white border border-blue-200 text-blue-700">
                        {topTask.priority_label}
                      </span>
                    </div>
                    <h3 className="font-sans font-bold text-slate-900 text-base">
                      {topTask.title}
                    </h3>
                    <p className="text-xs text-slate-600 line-clamp-2">
                      {topTask.description || 'All prerequisites satisfied. Eligible for execution.'}
                    </p>
                    <div className="pt-2 flex items-center justify-between text-xs text-slate-500 border-t border-blue-200/50">
                      <span>⏱️ {topTask.duration_formatted}</span>
                      <span>🗓️ {topTask.due_date_formatted}</span>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                    <span className="text-xs text-slate-500 font-medium">DISPATCH STATUS</span>
                    <h3 className="font-sans font-bold text-slate-800 text-base">
                      Ready for Task Dispatch
                    </h3>
                    <p className="text-xs text-slate-500">
                      Add tasks and assign priorities to receive automated scheduling recommendations.
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
                  <div className="p-2.5 rounded-lg bg-amber-50/70 border border-amber-100">
                    <div className="text-[11px] font-sans font-bold uppercase tracking-wider text-amber-700">Active</div>
                    <div className="font-sans font-extrabold text-2xl text-amber-800 tracking-tight tabular-nums mt-0.5">
                      {overview?.in_progress_tasks ?? 0}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-100">
                    <div className="text-[11px] font-sans font-bold uppercase tracking-wider text-emerald-600">Done</div>
                    <div className="font-sans font-extrabold text-2xl text-emerald-700 tracking-tight tabular-nums mt-0.5">
                      {overview?.completed_tasks ?? 0}
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
      {/* 2. CORE CAPABILITY MODULES */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="pt-pill pt-pill-blue">CORE CAPABILITIES</span>
          <h2 className="text-3xl sm:text-4xl font-sans font-bold text-slate-900 tracking-tight">
            Designed for clear, reliable project execution.
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Every feature in TaskForge helps you manage work, track dependencies, avoid delays, and meet critical deadlines.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Task Management */}
          <Link href="/tasks" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-brand mb-4 group-hover:scale-110 transition-transform">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-sans font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Task Workspace &amp; Organization
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Create, edit, search, and organize project tasks with priority classification, deadline tracking, and full Undo/Redo support.
            </p>
          </Link>

          {/* Card 2: Intelligent Scheduling */}
          <Link href="/scheduling" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mb-4 group-hover:scale-110 transition-transform">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-sans font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Smart Prioritization &amp; Risks
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Automated recommendation engine that surfaces the optimal next task based on deadline urgency, priority, and dependency readiness.
            </p>
          </Link>

          {/* Card 3: Dependency Planning */}
          <Link href="/dependencies" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 mb-4 group-hover:scale-110 transition-transform">
              <GitBranch className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-sans font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Task Dependencies &amp; Blockers
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Define which tasks must finish before others can begin. Automated cycle protection prevents impossible circular relationships.
            </p>
          </Link>

          {/* Card 4: Critical Path Planning */}
          <Link href="/planning" className="pt-card pt-card-hover p-6 group block">
            <div className="w-10 h-10 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 mb-4 group-hover:scale-110 transition-transform">
              <Calendar className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-sans font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Project Timeline &amp; Critical Path
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Identify the exact sequence of tasks that determine overall project completion date and test delay scenarios in What-If simulations.
            </p>
          </Link>

          {/* Card 5: Technical Labs */}
          <Link href="/laboratory" className="pt-card pt-card-hover p-6 group block border-blue-200 bg-blue-50/20">
            <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 mb-4 group-hover:scale-110 transition-transform">
              <FlaskConical className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-sans font-bold text-slate-900 mt-1 mb-2 group-hover:text-brand transition-colors">
              Technical &amp; Academic Labs
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Dedicated evaluation portal for faculty inspection: custom data structure benchmarks, BST traversals, hash tables, and structure comparisons.
            </p>
          </Link>

          {/* Card 6: Dual Architecture */}
          <div className="pt-card p-6 bg-slate-900 text-white flex flex-col justify-between">
            <div>
              <span className="text-[11px] font-sans font-bold text-blue-400 uppercase tracking-wider">
                System Integration
              </span>
              <h3 className="text-lg font-sans font-bold mt-1 mb-2">
                Dual Frontend Architecture
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Enjoy this modern Next.js frontend or launch the original Streamlit application at any time with synchronized SQLite storage.
              </p>
            </div>
            <div className="pt-4 font-mono text-xs text-slate-400 bg-slate-800/80 p-2.5 rounded border border-slate-700">
              streamlit run app.py
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------- */}
      {/* 3. WORKFLOW OVERVIEW */}
      {/* ------------------------------------------------------------- */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="pt-pill pt-pill-blue">WORKFLOW</span>
          <h2 className="text-3xl font-sans font-bold text-slate-900 tracking-tight">
            How TaskForge works.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { step: '01', title: 'Add Tasks', desc: 'Define title, estimated duration, deadline, and priority.', link: '/tasks' },
            { step: '02', title: 'Link Dependencies', desc: 'Connect prerequisite relationships with cycle protection.', link: '/dependencies' },
            { step: '03', title: 'Smart Dispatch', desc: 'Get automated recommendations on what work to start next.', link: '/scheduling' },
            { step: '04', title: 'Monitor Risks', desc: 'Identify overdue tasks and tasks at risk of slipping.', link: '/scheduling' },
            { step: '05', title: 'Simulate Delays', desc: 'Model delay impacts safely without altering project records.', link: '/planning' },
          ].map((item) => (
            <Link
              key={item.step}
              href={item.link}
              className="pt-card p-5 group hover:border-brand transition-all block"
            >
              <div className="text-2xl font-sans font-extrabold text-slate-300 group-hover:text-brand transition-colors mb-2">
                {item.step}
              </div>
              <h4 className="font-sans font-bold text-slate-900 text-sm mb-1 group-hover:text-brand transition-colors">
                {item.title}
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                {item.desc}
              </p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
