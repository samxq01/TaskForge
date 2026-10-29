'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  GitBranch,
  Plus,
  Trash2,
  AlertOctagon,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
  FlaskConical,
} from 'lucide-react';
import { api, DependencyGraph, Task } from '@/lib/api-client';

export default function DependenciesPage() {
  const [graph, setGraph] = useState<DependencyGraph | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Form State
  const [prereqId, setPrereqId] = useState<string>('');
  const [dependentId, setDependentId] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  const loadGraph = async () => {
    try {
      setLoading(true);
      const [gData, tData] = await Promise.all([
        api.getDependencies(),
        api.getTasks(),
      ]);
      setGraph(gData);
      setTasks(tData);
      if (tData.length >= 2) {
        if (!prereqId) setPrereqId(tData[0].id.toString());
        if (!dependentId) setDependentId(tData[1].id.toString());
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  const handleAddDependency = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    const source = parseInt(prereqId, 10);
    const target = parseInt(dependentId, 10);

    if (source === target) {
      setErrorMessage('A task cannot depend on itself.');
      return;
    }

    try {
      const res = await api.addDependency(source, target);
      if (res.success) {
        setSuccessMessage('Dependency relationship saved successfully.');
        loadGraph();
      } else {
        setErrorMessage(res.message || 'This dependency would create a cycle. The task relationship was not saved.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'This dependency would create a cycle. The task relationship was not saved.');
    }
  };

  const handleRemove = async (source: number, target: number) => {
    try {
      await api.removeDependency(source, target);
      loadGraph();
    } catch (err: any) {
      alert(err.message || 'Failed to remove dependency');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-sans font-extrabold text-slate-900 tracking-tight">
            Dependencies
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage task prerequisites, detect blockers, and track recommended execution order.
          </p>
        </div>

        <button
          onClick={loadGraph}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Map</span>
        </button>
      </div>

      {/* Cycle Detection Status */}
      {graph?.is_cyclic ? (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-300 flex items-center gap-3 text-rose-800 text-xs font-sans">
          <AlertOctagon className="w-5 h-5 text-rose-600 shrink-0" />
          <div>
            <strong>Circular Dependency Detected!</strong> Tasks cannot be scheduled because of a circular dependency loop: {graph.cycle_nodes.join(' → ')}. Remove the circular relationship to resolve.
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-3 text-emerald-800 text-xs font-sans">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <strong>Valid Execution Graph:</strong> All task relationships are well-ordered with zero circular deadlocks.
          </div>
        </div>
      )}

      {/* Main Grid: Add Dependency + Execution Sequence */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Form */}
        <div className="space-y-6">
          <div className="pt-card p-6 space-y-4">
            <h3 className="font-sans font-bold text-slate-900 text-sm">Add Dependency</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Define which task must complete before another task can begin.
            </p>

            {errorMessage && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 font-sans">
                {errorMessage}
              </div>
            )}
            {successMessage && (
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 font-sans">
                {successMessage}
              </div>
            )}

            <form onSubmit={handleAddDependency} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Prerequisite Task (Must finish first)</label>
                <select
                  value={prereqId}
                  onChange={(e) => setPrereqId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 font-sans text-xs"
                >
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      #{t.id}: {t.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Dependent Task (Waiting on prerequisite)</label>
                <select
                  value={dependentId}
                  onChange={(e) => setDependentId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 font-sans text-xs"
                >
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      #{t.id}: {t.title}
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white font-semibold transition-colors shadow-xs"
              >
                Add Dependency
              </button>
            </form>
          </div>

          {/* Quick link to Technical Labs for BFS/DFS */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
            <h4 className="font-sans font-bold text-slate-800 flex items-center gap-1.5">
              <FlaskConical className="w-3.5 h-3.5 text-brand" />
              <span>Looking for Graph Traversals?</span>
            </h4>
            <p className="text-slate-500 leading-relaxed">
              Step-by-step BFS/DFS traversals, topological sort traces, and complexity analysis are accessible inside Technical Labs.
            </p>
            <Link
              href="/laboratory"
              className="text-brand hover:underline font-semibold inline-flex items-center gap-1"
            >
              <span>Open Technical Labs</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>

        {/* Right 2 Columns: Execution Sequence & Relationships Table */}
        <div className="lg:col-span-2 space-y-6">
          {/* Execution Sequence */}
          <div className="pt-card p-6 space-y-4">
            <div>
              <h3 className="font-sans font-bold text-slate-900 text-sm">
                Recommended Execution Sequence
              </h3>
              <p className="text-xs text-slate-500">
                A valid linear ordering where every task is scheduled only after all its prerequisites are completed.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2 pt-2">
              {graph?.topological_order && graph.topological_order.length > 0 ? (
                graph.topological_order.map((taskId, idx) => {
                  const t = tasks.find((item) => item.id === taskId);
                  return (
                    <React.Fragment key={taskId}>
                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-sans text-[11px] flex items-center justify-center font-bold">
                          {idx + 1}
                        </span>
                        <div>
                          <div className="text-brand font-bold text-xs">#{taskId}</div>
                          <div className="font-semibold text-slate-800 text-xs truncate max-w-[130px]">
                            {t?.title || `Task #${taskId}`}
                          </div>
                        </div>
                      </div>
                      {idx < graph.topological_order.length - 1 && (
                        <ArrowRight className="w-4 h-4 text-slate-300" />
                      )}
                    </React.Fragment>
                  );
                })
              ) : (
                <div className="text-xs text-slate-400 p-4">
                  No dependency sequence available.
                </div>
              )}
            </div>
          </div>

          {/* Active Dependencies Table */}
          <div className="pt-card p-6 space-y-4">
            <div>
              <h3 className="font-sans font-bold text-slate-900 text-sm">Active Dependencies</h3>
              <p className="text-xs text-slate-500">Existing prerequisite and dependent relationships</p>
            </div>

            {graph?.edges.length === 0 ? (
              <div className="text-center p-8 text-xs text-slate-400">
                No dependency relationships registered. All tasks are currently independent.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-sans">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[11px] font-bold tracking-wider">
                    <tr>
                      <th className="py-2.5 px-4">Relationship</th>
                      <th className="py-2.5 px-4">Status</th>
                      <th className="py-2.5 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {graph?.edges.map((edge) => {
                      const prereq = tasks.find((t) => t.id === edge.source);
                      const dep = tasks.find((t) => t.id === edge.target);
                      const prereqDone = prereq?.status === 'Completed';

                      return (
                        <tr key={`${edge.source}-${edge.target}`} className="hover:bg-slate-50">
                          <td className="py-3 px-4">
                            <span className="font-semibold text-slate-900">#{edge.target} {dep?.title}</span>
                            <span className="text-slate-500"> is waiting for </span>
                            <span className="font-semibold text-brand">#{edge.source} {prereq?.title}</span>
                          </td>
                          <td className="py-3 px-4">
                            {prereqDone ? (
                              <span className="text-emerald-600 font-semibold text-[11px]">Prerequisite Met</span>
                            ) : (
                              <span className="text-amber-700 font-semibold text-[11px]">Prerequisite Pending</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => handleRemove(edge.source, edge.target)}
                              className="p-1 rounded text-slate-400 hover:text-rose-600 transition-colors"
                              title="Remove dependency"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
