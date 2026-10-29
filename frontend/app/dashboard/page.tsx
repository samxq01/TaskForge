'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Plus,
  Search,
  Filter,
  ArrowUpDown,
  Sparkles,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ListFilter,
  Check,
  ChevronRight,
  Flame,
  X,
  Play,
  RotateCcw,
} from 'lucide-react';
import { api, Overview, Task, SmartScheduleResult } from '@/lib/api-client';

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [schedule, setSchedule] = useState<SmartScheduleResult | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters & Sorting state
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('deadline');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');

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
        api.getTasks({
          status: statusFilter || undefined,
          priority: priorityFilter ? parseInt(priorityFilter, 10) : undefined,
          search: search || undefined,
          sort_by: sortBy || undefined,
        }),
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
  }, [statusFilter, priorityFilter, sortBy]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* ------------------------------------------------------------- */}
      {/* 1. DASHBOARD HEADER & QUICK ACTIONS */}
      {/* ------------------------------------------------------------- */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="pt-pill pt-pill-blue">OPERATIONAL WORKSPACE</span>
            <span className="text-xs text-slate-500 font-mono">SQLite Persistent</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-extrabold text-slate-900 mt-1">
            Task Operations &amp; Intelligence
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleProcessQueue}
            className="inline-flex items-center gap-1.5 bg-white border border-slate-200 hover:border-slate-300 px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-700 transition-colors shadow-xs"
          >
            <Play className="w-3.5 h-3.5 text-brand" />
            <span>Process FIFO Queue ({overview?.queue_size ?? 0})</span>
          </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-1.5 bg-brand hover:bg-brand-hover text-white px-4 py-2 rounded-lg text-xs font-semibold transition-all shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Create Task</span>
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 2. FIVE-METRIC KPI OVERVIEW STRIP */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="pt-card p-4">
          <span className="text-[0.68rem] font-mono uppercase text-slate-400">Total Work</span>
          <div className="text-2xl font-display font-bold text-slate-900 mt-1">
            {overview?.total_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-slate-500 mt-1 block">In SQLite registry</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-blue-500">
          <span className="text-[0.68rem] font-mono uppercase text-blue-600">Pending</span>
          <div className="text-2xl font-display font-bold text-slate-900 mt-1">
            {overview?.pending_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-blue-600 mt-1 block">Ready in queue</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-amber-500">
          <span className="text-[0.68rem] font-mono uppercase text-amber-600">In Progress</span>
          <div className="text-2xl font-display font-bold text-slate-900 mt-1">
            {overview?.in_progress_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-amber-600 mt-1 block">Active work</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-emerald-500">
          <span className="text-[0.68rem] font-mono uppercase text-emerald-600">Completed</span>
          <div className="text-2xl font-display font-bold text-slate-900 mt-1">
            {overview?.completed_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-emerald-600 mt-1 block">Satisfied prerequisites</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-rose-500">
          <span className="text-[0.68rem] font-mono uppercase text-rose-600">Overdue</span>
          <div className="text-2xl font-display font-bold text-slate-900 mt-1">
            {overview?.overdue_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-rose-600 mt-1 block">Past deadline</span>
        </div>

        <div className="pt-card p-4 border-l-4 border-l-slate-400">
          <span className="text-[0.68rem] font-mono uppercase text-slate-600">Blocked</span>
          <div className="text-2xl font-display font-bold text-slate-900 mt-1">
            {overview?.blocked_tasks ?? 0}
          </div>
          <span className="text-[0.7rem] text-slate-500 mt-1 block">Awaiting prereqs</span>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 3. MIN-HEAP TOP RECOMMENDATION BANNER */}
      {/* ------------------------------------------------------------- */}
      {topRec && (
        <div className="bg-white rounded-xl border border-blue-200 shadow-sm p-6 relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-2 max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="pt-pill pt-pill-blue">
                  <span className="pt-dot pt-dot-blue" />
                  SMART AUTO-SCHEDULER &bull; TOP RANK #{topRec.rank}
                </span>
                <span className="text-xs font-mono font-bold text-brand bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                  {topRec.task.priority_label}
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-display font-bold text-slate-900">
                #{topRec.task.id}: {topRec.task.title}
              </h2>
              <p className="text-xs sm:text-sm text-slate-600">
                {topRec.explanation}
              </p>
              <div className="flex flex-wrap gap-4 text-xs font-mono text-slate-500 pt-1">
                <span>⏱️ {topRec.task.duration_formatted}</span>
                <span>🗓️ {topRec.task.due_date_formatted}</span>
                <span className="text-emerald-600 font-semibold">✓ Prereqs Completed</span>
              </div>
            </div>

            <div className="flex items-center gap-2 self-end md:self-center">
              <Link
                href="/scheduling"
                className="px-4 py-2.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
              >
                View All {schedule?.ranked_tasks.length} Rankings &rarr;
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 4. TASK REGISTRY CONTROLS & TABLE */}
      {/* ------------------------------------------------------------- */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          {/* Search Bar */}
          <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search tasks by title or notes..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent"
            />
          </form>

          {/* Filters & View Toggles */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand"
            >
              <option value="">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
            </select>

            {/* Priority Filter */}
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand"
            >
              <option value="">All Priorities</option>
              <option value="4">Urgent (P4)</option>
              <option value="3">High (P3)</option>
              <option value="2">Medium (P2)</option>
              <option value="1">Low (P1)</option>
            </select>

            {/* Sorting Algorithm */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 font-mono text-[0.72rem] focus:outline-none focus:ring-2 focus:ring-brand"
            >
              <option value="deadline">Sort: Deadline (Earliest)</option>
              <option value="priority">Sort: Priority (Urgent First)</option>
              <option value="duration">Sort: Duration (Shortest)</option>
              <option value="id">Sort: Task ID</option>
            </select>

            {/* View Mode Toggle */}
            <div className="flex rounded-lg border border-slate-200 bg-white p-0.5">
              <button
                onClick={() => setViewMode('cards')}
                className={`px-2.5 py-1 rounded text-xs transition-colors ${
                  viewMode === 'cards' ? 'bg-slate-900 text-white font-medium' : 'text-slate-600'
                }`}
              >
                Cards
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-2.5 py-1 rounded text-xs transition-colors ${
                  viewMode === 'table' ? 'bg-slate-900 text-white font-medium' : 'text-slate-600'
                }`}
              >
                Table
              </button>
            </div>
          </div>
        </div>

        {/* Task List Rendering */}
        {loading ? (
          <div className="pt-card p-12 text-center text-slate-400 text-xs font-mono">
            Loading tasks from SQLite...
          </div>
        ) : tasks.length === 0 ? (
          <div className="pt-card p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
              <ListFilter className="w-6 h-6" />
            </div>
            <h3 className="font-display font-bold text-slate-800 text-base">No tasks match your filter</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Clear your search or create a new task to populate the registry.
            </p>
          </div>
        ) : viewMode === 'cards' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map((task) => (
              <div key={task.id} className="pt-card pt-card-hover p-5 space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-brand">
                      #{task.id}
                    </span>
                    <span
                      className={`text-[0.68rem] font-mono px-2 py-0.5 rounded font-semibold ${
                        task.status === 'Completed'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : task.status === 'In Progress'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}
                    >
                      {task.status}
                    </span>
                  </div>

                  <h3 className="font-display font-bold text-slate-900 text-base">
                    {task.title}
                  </h3>

                  <p className="text-xs text-slate-600 line-clamp-2">
                    {task.description || 'No additional description.'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-mono text-slate-500">
                  <span className="font-semibold text-slate-700">{task.priority_label}</span>
                  <span>⏱️ {task.duration_formatted}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="pt-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[0.7rem] uppercase">
                  <tr>
                    <th className="py-3 px-4">ID</th>
                    <th className="py-3 px-4">Title</th>
                    <th className="py-3 px-4">Priority</th>
                    <th className="py-3 px-4">Duration</th>
                    <th className="py-3 px-4">Deadline</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Ready</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {tasks.map((task) => (
                    <tr key={task.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-mono text-brand font-bold">#{task.id}</td>
                      <td className="py-3 px-4 text-slate-900">{task.title}</td>
                      <td className="py-3 px-4 font-mono">{task.priority_label}</td>
                      <td className="py-3 px-4 font-mono text-slate-500">{task.duration_formatted}</td>
                      <td className="py-3 px-4 text-slate-600">{task.due_date_formatted}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-[0.68rem] font-mono px-2 py-0.5 rounded font-semibold ${
                            task.status === 'Completed'
                              ? 'bg-emerald-50 text-emerald-700'
                              : task.status === 'In Progress'
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-blue-50 text-blue-700'
                          }`}
                        >
                          {task.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {task.is_ready ? (
                          <span className="text-emerald-600 font-mono text-[0.7rem]">✓ Ready</span>
                        ) : (
                          <span className="text-slate-400 font-mono text-[0.7rem]">Blocked ({task.prerequisites_count})</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 5. CREATE TASK MODAL */}
      {/* ------------------------------------------------------------- */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="font-display font-bold text-slate-900 text-lg">Create New Task</h3>
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
                  placeholder="e.g. Design relational schema"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
                  >
                    <option value={1}>Low (P1)</option>
                    <option value={2}>Medium (P2)</option>
                    <option value={3}>High (P3)</option>
                    <option value={4}>Urgent (P4)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Duration (min)</label>
                  <input
                    type="number"
                    min={5}
                    max={1440}
                    value={newDuration}
                    onChange={(e) => setNewDuration(parseInt(e.target.value, 10) || 30)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Deadline (Optional)</label>
                <input
                  type="datetime-local"
                  value={newDueDate}
                  onChange={(e) => setNewDueDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-mono"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={3}
                  placeholder="Additional context or requirements..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
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
