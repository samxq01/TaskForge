'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Plus,
  ArrowRight,
  Clock,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Play,
  Layers,
  Sparkles,
  X,
  ChevronRight,
  RotateCcw,
} from 'lucide-react';
import { api, Overview, Task, SmartScheduleResult } from '@/lib/api-client';

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [schedule, setSchedule] = useState<SmartScheduleResult | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newPriority, setNewPriority] = useState<number>(2);
  const [newDuration, setNewDuration] = useState<number>(30);
  const [newDueDate, setNewDueDate] = useState<string>('');
  const [newDescription, setNewDescription] = useState<string>('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [ovData, schedData, taskList] = await Promise.all([
        api.getOverview(),
        api.getSchedulingRecommendations(),
        api.getTasks(),
      ]);
      setOverview(ovData);
      setSchedule(schedData);
      setTasks(taskList);
    } catch (err) {
      console.error('Error loading dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      await api.createTask({
        title: newTitle.trim(),
        priority: newPriority,
        duration: newDuration,
        status: 'Pending',
        description: newDescription.trim(),
        due_date: newDueDate ? new Date(newDueDate).toISOString() : null,
      });
      setIsModalOpen(false);
      setNewTitle('');
      setNewDescription('');
      setNewDueDate('');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Error creating task');
    }
  };

  const handleProcessQueue = async () => {
    try {
      const res = await api.processNextQueue();
      if (res.success) {
        loadData();
      } else {
        alert(res.message);
      }
    } catch (err: any) {
      alert(err.message || 'Error processing queue');
    }
  };

  const topRec = schedule?.recommendation;

  // Filter useful dashboard slices
  const upcomingTasks = tasks
    .filter((t) => t.due_date && t.status !== 'Completed')
    .sort((a, b) => new Date(a.due_date!).getTime() - new Date(b.due_date!).getTime())
    .slice(0, 4);

  const blockedTasks = tasks
    .filter((t) => !t.is_ready && t.status !== 'Completed' && t.prerequisites_count > 0)
    .slice(0, 4);

  const inProgressTasks = tasks
    .filter((t) => t.status === 'In Progress')
    .slice(0, 3);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* ------------------------------------------------------------- */}
      {/* 1. DASHBOARD HEADER & QUICK ACTIONS (Phase 4.1 & 4.7) */}
      {/* ------------------------------------------------------------- */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-sans font-extrabold text-slate-900 tracking-tight">
            Good to see you.
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Your tasks, deadlines, and project progress — all in one place.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Link
            href="/tasks"
            className="inline-flex items-center gap-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-3.5 py-2 rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <span>View All Tasks</span>
          </Link>

          <Link
            href="/scheduling"
            className="inline-flex items-center gap-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-3.5 py-2 rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <span>Open Schedule</span>
          </Link>

          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-1.5 bg-brand hover:bg-brand-hover text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-xs transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Task</span>
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 2. FIVE SUMMARY METRICS (Phase 4.2) */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <div className="pt-card p-4">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-400">Total Tasks</span>
          <div className="text-2xl font-sans font-extrabold text-slate-900 mt-1 tabular-nums">
            {overview?.total_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-slate-500 mt-1 block">In project registry</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-amber-500">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-amber-600">In Progress</span>
          <div className="text-2xl font-sans font-extrabold text-slate-900 mt-1 tabular-nums">
            {overview?.in_progress_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-amber-600 mt-1 block">Active work</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-emerald-500">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-emerald-600">Completed</span>
          <div className="text-2xl font-sans font-extrabold text-slate-900 mt-1 tabular-nums">
            {overview?.completed_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-emerald-600 mt-1 block">Finished items</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-rose-500">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-rose-600">Overdue</span>
          <div className="text-2xl font-sans font-extrabold text-slate-900 mt-1 tabular-nums">
            {overview?.overdue_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-rose-600 mt-1 block">Past deadline</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-slate-400">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-600">Blocked</span>
          <div className="text-2xl font-sans font-extrabold text-slate-900 mt-1 tabular-nums">
            {overview?.blocked_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-slate-500 mt-1 block">Waiting on prerequisites</span>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 3. RECOMMENDED NEXT TASK (Phase 4.3) */}
      {/* ------------------------------------------------------------- */}
      <div className="bg-white rounded-xl border border-blue-200 shadow-sm p-6 relative overflow-hidden">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <span className="pt-pill pt-pill-blue">
              <span className="pt-dot pt-dot-blue" />
              RECOMMENDED NEXT TASK
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleProcessQueue}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors"
            >
              <Play className="w-3 h-3 text-brand" />
              <span>Process Next ({overview?.queue_size ?? 0})</span>
            </button>
            <Link
              href="/scheduling"
              className="text-xs font-semibold text-brand hover:text-brand-hover inline-flex items-center gap-1"
            >
              <span>Full Schedule</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {topRec ? (
          <div className="mt-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="space-y-2 max-w-3xl">
              <div className="flex items-center gap-2">
                <span className="text-xs font-sans font-bold text-brand bg-blue-50 px-2.5 py-0.5 rounded border border-blue-100">
                  {topRec.task.priority_label}
                </span>
                <span className="text-xs text-slate-500">
                  Task #{topRec.task.id}
                </span>
              </div>

              <h2 className="text-xl sm:text-2xl font-sans font-bold text-slate-900">
                {topRec.task.title}
              </h2>

              <p className="text-xs sm:text-sm text-slate-600">
                {topRec.explanation}
              </p>

              <div className="flex flex-wrap gap-4 text-xs font-sans text-slate-500 pt-1">
                <span>⏱️ {topRec.task.duration_formatted}</span>
                <span>🗓️ Due {topRec.task.due_date_formatted}</span>
                <span className="text-emerald-600 font-semibold">✓ Prerequisites Complete</span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Link
                href="/tasks"
                className="inline-flex items-center gap-1.5 bg-slate-900 hover:bg-brand text-white px-4 py-2.5 rounded-lg text-xs font-semibold shadow-xs transition-all"
              >
                <span>Open Task Details</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="py-6 text-center space-y-2">
            <p className="text-sm font-semibold text-slate-800">All caught up!</p>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              No pending tasks are awaiting dispatch or all pending items are currently blocked by uncompleted prerequisites.
            </p>
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 4. TWO-COLUMN OPERATIONAL SUMMARY: DEADLINES & BLOCKED TASKS */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Upcoming Deadlines (Phase 4.4) */}
        <div className="pt-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="font-sans font-bold text-slate-900 text-sm">Upcoming Deadlines</h3>
              <p className="text-xs text-slate-500">Tasks with approaching due dates</p>
            </div>
            <Link
              href="/scheduling"
              className="text-xs font-semibold text-brand hover:underline inline-flex items-center gap-1"
            >
              <span>View schedule</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {upcomingTasks.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">
              No pending deadlines scheduled. Set due dates on tasks to monitor schedule risk.
            </p>
          ) : (
            <div className="divide-y divide-slate-100">
              {upcomingTasks.map((t) => (
                <div key={t.id} className="py-3 flex items-center justify-between gap-4">
                  <div className="space-y-0.5 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-brand">#{t.id}</span>
                      <h4 className="text-xs font-semibold text-slate-900 truncate">{t.title}</h4>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-slate-500">
                      <span>⏱️ {t.duration_formatted}</span>
                      <span>🗓️ {t.due_date_formatted}</span>
                    </div>
                  </div>

                  <span className="text-[11px] font-sans font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 shrink-0">
                    {t.priority_label}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Blocked Tasks (Phase 4.5) */}
        <div className="pt-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="font-sans font-bold text-slate-900 text-sm">Blocked Tasks</h3>
              <p className="text-xs text-slate-500">Waiting on incomplete prerequisites</p>
            </div>
            <Link
              href="/dependencies"
              className="text-xs font-semibold text-brand hover:underline inline-flex items-center gap-1"
            >
              <span>View dependencies</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {blockedTasks.length === 0 ? (
            <div className="py-6 text-center text-xs text-emerald-600 font-medium">
              ✓ No tasks are currently blocked. All prerequisites are satisfied.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {blockedTasks.map((t) => (
                <div key={t.id} className="py-3 flex items-center justify-between gap-4">
                  <div className="space-y-0.5 min-w-0">
                    <div className="flex items-center gap-2">
                      <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="text-xs font-semibold text-brand">#{t.id}</span>
                      <h4 className="text-xs font-semibold text-slate-900 truncate">{t.title}</h4>
                    </div>
                    <p className="text-[11px] text-rose-600">
                      Waiting for {t.prerequisites_count} prerequisite task{t.prerequisites_count > 1 ? 's' : ''} to complete
                    </p>
                  </div>

                  <Link
                    href="/dependencies"
                    className="text-[11px] font-medium text-slate-600 hover:text-brand bg-slate-50 border border-slate-200 px-2.5 py-1 rounded shrink-0 transition-colors"
                  >
                    Inspect
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 5. IN-PROGRESS WORK & PROJECT SHORTCUTS (Phase 4.6 & 4.7) */}
      {/* ------------------------------------------------------------- */}
      <div className="pt-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-sans font-bold text-slate-900 text-sm">Active &amp; In-Progress Work</h3>
            <p className="text-xs text-slate-500">Tasks currently being executed</p>
          </div>
          <Link
            href="/planning"
            className="text-xs font-semibold text-brand hover:underline inline-flex items-center gap-1"
          >
            <span>Project timeline</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {inProgressTasks.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">
            No tasks currently marked &quot;In Progress&quot;. Move tasks to in-progress when work begins.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {inProgressTasks.map((t) => (
              <div key={t.id} className="p-4 rounded-lg bg-amber-50/50 border border-amber-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-amber-700">#{t.id}</span>
                  <span className="text-[11px] font-medium text-amber-800 bg-amber-100/80 px-2 py-0.5 rounded">
                    {t.priority_label}
                  </span>
                </div>
                <h4 className="text-xs font-semibold text-slate-900 truncate">{t.title}</h4>
                <div className="text-[11px] text-slate-500">⏱️ {t.duration_formatted}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 6. CREATE TASK MODAL */}
      {/* ------------------------------------------------------------- */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="font-sans font-bold text-slate-900 text-base">Add New Task</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Task Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Design authentication workflow"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-sans"
                  >
                    <option value={1}>Low</option>
                    <option value={2}>Medium</option>
                    <option value={3}>High</option>
                    <option value={4}>Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Duration (minutes)</label>
                  <input
                    type="number"
                    min={5}
                    max={1440}
                    value={newDuration}
                    onChange={(e) => setNewDuration(parseInt(e.target.value, 10) || 30)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-sans"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Deadline (Optional)</label>
                <input
                  type="datetime-local"
                  value={newDueDate}
                  onChange={(e) => setNewDueDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-sans"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description (Optional)</label>
                <textarea
                  rows={3}
                  placeholder="Brief notes or context..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-sans"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-100 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand hover:bg-brand-hover text-white font-semibold transition-colors shadow-xs"
                >
                  Save Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
