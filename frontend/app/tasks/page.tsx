'use client';

import React, { useEffect, useState } from 'react';
import {
  Plus,
  Search,
  Filter,
  Edit2,
  Trash2,
  RotateCcw,
  RotateCw,
  Clock,
  Calendar,
  AlertCircle,
  CheckCircle2,
  X,
  Play,
  ArrowRight,
} from 'lucide-react';
import { api, Task, Overview } from '@/lib/api-client';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Filter state
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  // Edit / Create Modal state
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Form Fields
  const [formTitle, setFormTitle] = useState<string>('');
  const [formPriority, setFormPriority] = useState<number>(2);
  const [formDuration, setFormDuration] = useState<number>(30);
  const [formStatus, setFormStatus] = useState<string>('Pending');
  const [formDueDate, setFormDueDate] = useState<string>('');
  const [formDescription, setFormDescription] = useState<string>('');

  const loadTasks = async () => {
    try {
      setLoading(true);
      const [taskList, ov] = await Promise.all([
        api.getTasks({
          status: statusFilter || undefined,
          priority: priorityFilter ? parseInt(priorityFilter, 10) : undefined,
          search: search || undefined,
        }),
        api.getOverview(),
      ]);
      setTasks(taskList);
      setOverview(ov);
    } catch (err) {
      console.error('Error fetching tasks', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [statusFilter, priorityFilter]);

  const handleOpenCreate = () => {
    setModalMode('create');
    setSelectedTask(null);
    setFormTitle('');
    setFormPriority(2);
    setFormDuration(30);
    setFormStatus('Pending');
    setFormDueDate('');
    setFormDescription('');
    setIsModalOpen(true);
  };

  const handleOpenEdit = (task: Task) => {
    setModalMode('edit');
    setSelectedTask(task);
    setFormTitle(task.title);
    setFormPriority(task.priority);
    setFormDuration(task.duration);
    setFormStatus(task.status);
    setFormDueDate(task.due_date ? task.due_date.slice(0, 16) : '');
    setFormDescription(task.description);
    setIsModalOpen(true);
  };

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formTitle.trim()) return;

    try {
      if (modalMode === 'create') {
        await api.createTask({
          title: formTitle.trim(),
          priority: formPriority,
          duration: formDuration,
          status: formStatus,
          description: formDescription.trim(),
          due_date: formDueDate ? new Date(formDueDate).toISOString() : null,
        });
      } else if (modalMode === 'edit' && selectedTask) {
        await api.updateTask(selectedTask.id, {
          title: formTitle.trim(),
          priority: formPriority,
          duration: formDuration,
          status: formStatus as any,
          description: formDescription.trim(),
          due_date: formDueDate ? new Date(formDueDate).toISOString() : null,
        });
      }
      setIsModalOpen(false);
      loadTasks();
    } catch (err: any) {
      alert(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(`Are you sure you want to delete task #${id}? This action can be undone via Undo.`)) return;
    try {
      await api.deleteTask(id);
      loadTasks();
    } catch (err: any) {
      alert(err.message || 'Could not delete task');
    }
  };

  const handleStatusChange = async (task: Task, nextStatus: 'Pending' | 'In Progress' | 'Completed') => {
    try {
      await api.updateTask(task.id, { status: nextStatus });
      loadTasks();
    } catch (err: any) {
      alert(err.message || 'Status update failed');
    }
  };

  const handleUndo = async () => {
    try {
      await api.undo();
      loadTasks();
    } catch (err: any) {
      alert(err.message || 'No actions to undo');
    }
  };

  const handleRedo = async () => {
    try {
      await api.redo();
      loadTasks();
    } catch (err: any) {
      alert(err.message || 'No actions to redo');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <span className="pt-pill pt-pill-blue">TASK REGISTRY</span>
          <h1 className="text-2xl sm:text-3xl font-display font-extrabold text-slate-900 mt-1">
            Task Workspace &amp; Lifecycle
          </h1>
        </div>

        <div className="flex items-center gap-2">
          {/* Dual-Stack Undo / Redo */}
          <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 text-xs">
            <button
              onClick={handleUndo}
              disabled={!overview?.can_undo}
              className={`px-3 py-1.5 rounded flex items-center gap-1 font-medium transition-colors ${
                overview?.can_undo
                  ? 'hover:bg-slate-100 text-slate-700 cursor-pointer'
                  : 'text-slate-300 cursor-not-allowed'
              }`}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Undo</span>
            </button>
            <button
              onClick={handleRedo}
              disabled={!overview?.can_redo}
              className={`px-3 py-1.5 rounded flex items-center gap-1 font-medium transition-colors ${
                overview?.can_redo
                  ? 'hover:bg-slate-100 text-slate-700 cursor-pointer'
                  : 'text-slate-300 cursor-not-allowed'
              }`}
            >
              <RotateCw className="w-3.5 h-3.5" />
              <span>Redo</span>
            </button>
          </div>

          <button
            onClick={handleOpenCreate}
            className="inline-flex items-center gap-1.5 bg-brand hover:bg-brand-hover text-white px-4 py-2 rounded-lg text-xs font-semibold transition-all shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>New Task</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadTasks()}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="Pending">Pending</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700"
          >
            <option value="">All Priorities</option>
            <option value="4">Urgent (P4)</option>
            <option value="3">High (P3)</option>
            <option value="2">Medium (P2)</option>
            <option value="1">Low (P1)</option>
          </select>
        </div>
      </div>

      {/* Task Table */}
      <div className="pt-card overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-slate-400">Loading task records...</div>
        ) : tasks.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">No tasks found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[0.7rem] uppercase">
                <tr>
                  <th className="py-3 px-4">Task</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Deadline</th>
                  <th className="py-3 px-4">Status &amp; Transition</th>
                  <th className="py-3 px-4">Pre / Dep</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 max-w-xs">
                      <div className="font-mono text-brand font-bold text-[0.7rem]">#{task.id}</div>
                      <div className="text-slate-900 font-semibold truncate">{task.title}</div>
                      {task.description && (
                        <div className="text-slate-500 text-[0.72rem] truncate">{task.description}</div>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono">{task.priority_label}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{task.duration_formatted}</td>
                    <td className="py-3 px-4 text-slate-600 font-mono text-[0.72rem]">{task.due_date_formatted}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5">
                        <select
                          value={task.status}
                          onChange={(e) => handleStatusChange(task, e.target.value as any)}
                          className={`text-[0.72rem] font-mono px-2 py-1 rounded font-semibold border ${
                            task.status === 'Completed'
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : task.status === 'In Progress'
                              ? 'bg-amber-50 text-amber-700 border-amber-200'
                              : 'bg-blue-50 text-blue-700 border-blue-200'
                          }`}
                        >
                          <option value="Pending">Pending</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-[0.72rem] text-slate-500">
                      <span>{task.prerequisites_count} prereq / {task.dependents_count} dep</span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleOpenEdit(task)}
                          title="Edit Task"
                          className="p-1.5 rounded hover:bg-slate-100 text-slate-600 hover:text-brand transition-colors"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(task.id)}
                          title="Delete Task"
                          className="p-1.5 rounded hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="font-display font-bold text-slate-900 text-lg">
                {modalMode === 'create' ? 'Create Task' : `Edit Task #${selectedTask?.id}`}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitForm} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Priority</label>
                  <select
                    value={formPriority}
                    onChange={(e) => setFormPriority(parseInt(e.target.value, 10))}
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
                    value={formDuration}
                    onChange={(e) => setFormDuration(parseInt(e.target.value, 10) || 30)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Status</label>
                  <select
                    value={formStatus}
                    onChange={(e) => setFormStatus(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand"
                  >
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Deadline</label>
                  <input
                    type="datetime-local"
                    value={formDueDate}
                    onChange={(e) => setFormDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
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
                  {modalMode === 'create' ? 'Create Task' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

