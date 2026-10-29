'use client';

import React, { useEffect, useState } from 'react';
import {
  GitBranch,
  Plus,
  Trash2,
  AlertOctagon,
  CheckCircle2,
  Play,
  ArrowRight,
  RefreshCw,
  Layers,
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

  // Traversal State
  const [startTaskId, setStartTaskId] = useState<string>('');
  const [traversalResult, setTraversalResult] = useState<{
    algorithm: string;
    sequence: number[];
  } | null>(null);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const [g, t] = await Promise.all([api.getDependencies(), api.getTasks()]);
      setGraph(g);
      setTasks(t);
      if (t.length > 0 && !prereqId) {
        setPrereqId(t[0].id.toString());
        if (t.length > 1) {
          setDependentId(t[1].id.toString());
          setStartTaskId(t[0].id.toString());
        }
      }
    } catch (err) {
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

    const p = parseInt(prereqId, 10);
    const d = parseInt(dependentId, 10);
    if (isNaN(p) || isNaN(d)) return;

    try {
      const res = await api.addDependency(p, d);
      setSuccessMessage(res.message);
      loadGraph();
    } catch (err: any) {
      setErrorMessage(err.message || 'Could not add dependency');
    }
  };

  const handleRemove = async (p: number, d: number) => {
    try {
      await api.removeDependency(p, d);
      loadGraph();
    } catch (err: any) {
      alert(err.message || 'Error removing dependency');
    }
  };

  const handleRunBFS = async () => {
    const id = parseInt(startTaskId, 10);
    if (isNaN(id)) return;
    try {
      const res = await api.runBFS(id);
      setTraversalResult({ algorithm: res.algorithm, sequence: res.visited_sequence });
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRunDFS = async () => {
    const id = parseInt(startTaskId, 10);
    if (isNaN(id)) return;
    try {
      const res = await api.runDFS(id);
      setTraversalResult({ algorithm: res.algorithm, sequence: res.visited_sequence });
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="pt-pill pt-pill-blue">CO5 DIRECTED GRAPH</span>
            <span className="text-xs font-sans font-medium text-slate-500">DAG Cycle Prevention Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-extrabold text-slate-900 mt-1">
            Dependency Map &amp; Topological Order
          </h1>
        </div>

        <button
          onClick={loadGraph}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Graph</span>
        </button>
      </div>

      {/* Cycle Detection Banner */}
      {graph?.is_cyclic ? (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-300 flex items-center gap-3 text-rose-800 text-xs">
          <AlertOctagon className="w-5 h-5 text-rose-600 shrink-0" />
          <div>
            <strong>Cycle Detected in Dependency Relationships!</strong> Topological sort is blocked. Cycle nodes: {graph.cycle_nodes.join(' → ')}.
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-3 text-emerald-800 text-xs">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <strong>Graph is Acyclic (Valid DAG):</strong> Precedence relationships are well-ordered with zero circular deadlocks.
          </div>
        </div>
      )}

      {/* Main Grid: Add Dependency + Topological Order */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Form & Traversal */}
        <div className="space-y-6">
          {/* Add Dependency Form */}
          <div className="pt-card p-6 space-y-4">
            <span className="pt-pill pt-pill-blue">DEFINE RELATIONSHIP</span>
            <h3 className="font-display font-bold text-slate-900">Add Precedence Edge</h3>
            <p className="text-xs text-slate-600">
              Enforce: <strong>Task A must complete before Task B can start</strong> (A &rarr; B).
            </p>

            {errorMessage && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs font-mono text-rose-700">
                {errorMessage}
              </div>
            )}
            {successMessage && (
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs font-mono text-emerald-700">
                {successMessage}
              </div>
            )}

            <form onSubmit={handleAddDependency} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Prerequisite Task (A)</label>
                <select
                  value={prereqId}
                  onChange={(e) => setPrereqId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 font-mono"
                >
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      #{t.id}: {t.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Dependent Task (B)</label>
                <select
                  value={dependentId}
                  onChange={(e) => setDependentId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 font-mono"
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
                Add Directed Dependency
              </button>
            </form>
          </div>

          {/* Graph Traversals (BFS / DFS) */}
          <div className="pt-card p-6 space-y-4">
            <span className="pt-pill pt-pill-amber">GRAPH EXPLORATION</span>
            <h3 className="font-display font-bold text-slate-900">Run BFS &amp; DFS Traversals</h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Starting Node</label>
                <select
                  value={startTaskId}
                  onChange={(e) => setStartTaskId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 font-mono"
                >
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      #{t.id}: {t.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleRunBFS}
                  className="py-2 rounded-lg bg-slate-900 hover:bg-brand text-white font-semibold transition-colors"
                >
                  Run BFS
                </button>
                <button
                  onClick={handleRunDFS}
                  className="py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition-colors"
                >
                  Run DFS
                </button>
              </div>

              {traversalResult && (
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 font-mono text-xs space-y-1">
                  <div className="text-[0.68rem] text-slate-400 uppercase">{traversalResult.algorithm}</div>
                  <div className="text-brand font-bold">
                    {traversalResult.sequence.length > 0
                      ? traversalResult.sequence.map((id) => `#${id}`).join(' → ')
                      : 'No connected reachable nodes'}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right 2 Columns: Topological Order & Edge Registry */}
        <div className="lg:col-span-2 space-y-6">
          {/* Kahn's Topological Order Sequence */}
          <div className="pt-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <span className="pt-pill pt-pill-blue">KAHN'S ALGORITHM</span>
              <span className="text-xs font-mono text-slate-500">In-Degree Resolution</span>
            </div>
            <h3 className="font-display font-bold text-slate-900">
              Topological Execution Sequence
            </h3>
            <p className="text-xs text-slate-600">
              A valid linear ordering of tasks where every prerequisite appears before its dependent tasks.
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-2">
              {graph?.topological_order && graph.topological_order.length > 0 ? (
                graph.topological_order.map((taskId, idx) => {
                  const t = tasks.find((item) => item.id === taskId);
                  return (
                    <React.Fragment key={taskId}>
                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-mono text-[0.68rem] flex items-center justify-center font-bold">
                          {idx + 1}
                        </span>
                        <div>
                          <div className="font-mono text-brand font-bold text-xs">#{taskId}</div>
                          <div className="font-semibold text-slate-800 text-xs truncate max-w-[120px]">
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
                <div className="text-xs font-mono text-slate-400 p-4">
                  No topological ordering available.
                </div>
              )}
            </div>
          </div>

          {/* Active Directed Edges Table */}
          <div className="pt-card p-6 space-y-4">
            <span className="pt-pill pt-pill-slate">PERSISTED RELATIONSHIPS</span>
            <h3 className="font-display font-bold text-slate-900">Active Dependency Edges</h3>

            {graph?.edges.length === 0 ? (
              <div className="text-center p-8 text-xs font-mono text-slate-400">
                No dependency relationships registered. All tasks are currently independent.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[0.7rem]">
                    <tr>
                      <th className="py-2.5 px-4">Prerequisite (Must Finish First)</th>
                      <th className="py-2.5 px-4">Direction</th>
                      <th className="py-2.5 px-4">Dependent (Blocked Until Prereq Finishes)</th>
                      <th className="py-2.5 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {graph?.edges.map((edge) => {
                      const prereq = tasks.find((t) => t.id === edge.source);
                      const dep = tasks.find((t) => t.id === edge.target);
                      return (
                        <tr key={`${edge.source}-${edge.target}`} className="hover:bg-slate-50">
                          <td className="py-2.5 px-4">
                            <span className="font-bold text-brand">#{edge.source}</span> {prereq?.title}
                          </td>
                          <td className="py-2.5 px-4 text-slate-400">&rarr;</td>
                          <td className="py-2.5 px-4">
                            <span className="font-bold text-brand">#{edge.target}</span> {dep?.title}
                          </td>
                          <td className="py-2.5 px-4 text-right">
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

