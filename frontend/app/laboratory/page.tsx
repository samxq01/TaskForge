'use client';

import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Play,
  RotateCcw,
  RotateCw,
  Search,
  ArrowUpDown,
  Binary,
  Layers,
  Database,
  CheckCircle2,
  HelpCircle,
  BarChart2,
} from 'lucide-react';
import {
  api,
  QueueStatus,
  SearchBenchmarkResult,
  SortBenchmarkResult,
  TreeOverview,
  HashStats,
  HashLookupResult,
  StructureResult,
} from '@/lib/api-client';

export default function LaboratoryPage() {
  const [activeTab, setActiveTab] = useState<'queue' | 'search-sort' | 'bst' | 'hash' | 'eval'>('queue');

  // Queue state
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [queueMessage, setQueueMessage] = useState<string>('');

  // Search/Sort Benchmark state
  const [searchSize, setSearchSize] = useState<number>(1000);
  const [searchScenario, setSearchScenario] = useState<string>('middle');
  const [searchResult, setSearchResult] = useState<SearchBenchmarkResult | null>(null);
  const [searchLoading, setSearchLoading] = useState<boolean>(false);

  const [sortSize, setSortSize] = useState<number>(500);
  const [sortDist, setSortDist] = useState<string>('random');
  const [sortResult, setSortResult] = useState<SortBenchmarkResult | null>(null);
  const [sortLoading, setSortLoading] = useState<boolean>(false);

  // BST state
  const [treeOverview, setTreeOverview] = useState<TreeOverview | null>(null);
  const [treeTab, setTreeTab] = useState<'inorder' | 'preorder' | 'postorder'>('inorder');

  // Hash Table state
  const [hashStats, setHashStats] = useState<HashStats | null>(null);
  const [lookupId, setLookupId] = useState<string>('1');
  const [lookupResult, setLookupResult] = useState<HashLookupResult | null>(null);

  // Evaluation state
  const [evalSize, setEvalSize] = useState<number>(100);
  const [evalScenario, setEvalScenario] = useState<string>('middle');
  const [evalResults, setEvalResults] = useState<StructureResult[]>([]);
  const [evalLoading, setEvalLoading] = useState<boolean>(false);

  // Initial loads
  const loadQueue = async () => {
    try {
      const qs = await api.getQueue();
      setQueueStatus(qs);
    } catch (e) {
      console.error(e);
    }
  };

  const loadTree = async () => {
    try {
      const to = await api.getTreeOverview();
      setTreeOverview(to);
    } catch (e) {
      console.error(e);
    }
  };

  const loadHash = async () => {
    try {
      const hs = await api.getHashTableStats();
      setHashStats(hs);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadQueue();
    loadTree();
    loadHash();
  }, []);

  // Queue handlers
  const handleProcessQueue = async () => {
    try {
      const res = await api.processNextQueue();
      setQueueMessage(res.message);
      loadQueue();
    } catch (err: any) {
      alert(err.message || 'Processing failed');
    }
  };

  const handleUndo = async () => {
    try {
      const res = await api.undo();
      setQueueMessage(`Undo: ${res.summary}`);
      loadQueue();
    } catch (err: any) {
      alert(err.message || 'No action to undo');
    }
  };

  const handleRedo = async () => {
    try {
      const res = await api.redo();
      setQueueMessage(`Redo: ${res.summary}`);
      loadQueue();
    } catch (err: any) {
      alert(err.message || 'No action to redo');
    }
  };

  // Search runner
  const runSearch = async () => {
    setSearchLoading(true);
    try {
      const res = await api.runSearchBenchmark(searchSize, searchScenario);
      setSearchResult(res);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  // Sort runner
  const runSort = async () => {
    setSortLoading(true);
    try {
      const res = await api.runSortBenchmark(sortSize, sortDist);
      setSortResult(res);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSortLoading(false);
    }
  };

  // Hash lookup
  const runHashLookup = async () => {
    const id = parseInt(lookupId, 10);
    if (isNaN(id)) return;
    try {
      const res = await api.lookupHashTask(id);
      setLookupResult(res);
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Evaluation runner
  const runEval = async () => {
    setEvalLoading(true);
    try {
      const res = await api.evaluateDataStructures(evalSize, evalScenario);
      setEvalResults(res.results);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="pt-pill pt-pill-blue">ACADEMIC &amp; TECHNICAL LABS</span>
            <span className="text-xs font-sans font-medium text-slate-500">Course Outcomes CO1 &ndash; CO5</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-sans font-extrabold text-slate-900 tracking-tight mt-1">
            Technical Labs &amp; Benchmarks
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Empirical runtime measurements, structural inspection, and viva preparation demos.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 text-xs font-semibold flex-wrap">
          {[
            { id: 'queue', label: 'Queue & Stack' },
            { id: 'search-sort', label: 'Search & Sort Lab' },
            { id: 'bst', label: 'BST Deadline Index' },
            { id: 'hash', label: 'Custom Hash Table' },
            { id: 'eval', label: 'Structure Evaluation' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-md transition-colors ${
                activeTab === tab.id ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* TAB 1: FIFO QUEUE & LIFO STACK */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'queue' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Left 2 Cols: FIFO Queue visualization */}
            <div className="md:col-span-2 pt-card p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <span className="pt-pill pt-pill-blue">FIFO ORDER</span>
                  <h3 className="font-display font-bold text-slate-900">Task Processing Queue</h3>
                </div>
                <button
                  onClick={handleProcessQueue}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-semibold shadow-xs"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Process Next (FIFO)</span>
                </button>
              </div>

              {queueMessage && (
                <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-xs font-mono text-brand">
                  {queueMessage}
                </div>
              )}

              {/* Head of Queue Spotlight */}
              {queueStatus?.head_task ? (
                <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-brand uppercase">★ Next to Execute (Head)</span>
                    <span className="bg-white px-2 py-0.5 rounded border border-blue-200 text-blue-700 font-semibold">
                      {queueStatus.head_task.priority_label}
                    </span>
                  </div>
                  <h4 className="font-display font-bold text-slate-900 text-base">
                    #{queueStatus.head_task.id}: {queueStatus.head_task.title}
                  </h4>
                  <div className="flex gap-4 text-xs font-mono text-slate-500">
                    <span>⏱️ {queueStatus.head_task.duration_formatted}</span>
                    <span>🗓️ {queueStatus.head_task.due_date_formatted}</span>
                  </div>
                </div>
              ) : (
                <div className="p-6 text-center text-xs text-slate-400 font-mono bg-slate-50 rounded-lg">
                  No eligible Pending tasks in FIFO queue.
                </div>
              )}

              {/* Sequence Table */}
              <div className="space-y-2">
                <h4 className="font-mono text-xs text-slate-500 uppercase tracking-wider">
                  Upcoming Queue Sequence ({queueStatus?.queue_size ?? 0} items)
                </h4>
                <div className="divide-y divide-slate-100 max-h-64 overflow-y-auto">
                  {queueStatus?.queue_tasks.map((task, idx) => (
                    <div key={task.id} className="py-2.5 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-3">
                        <span className="w-6 text-center font-mono text-slate-400 font-semibold">
                          #{idx + 1}
                        </span>
                        <div>
                          <span className="font-semibold text-slate-800">#{task.id} {task.title}</span>
                          <span className="text-[0.7rem] text-slate-500 font-mono block">
                            {task.duration_formatted} &bull; {task.due_date_formatted}
                          </span>
                        </div>
                      </div>
                      <span className="font-mono text-[0.7rem] px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        {task.priority_label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Col: Dual-Stack Undo/Redo */}
            <div className="pt-card p-6 space-y-4">
              <span className="pt-pill pt-pill-green">LIFO STACK DUALITY</span>
              <h3 className="font-display font-bold text-slate-900">Undo &amp; Redo Stacks</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Reversible operations push snapshots onto the Undo stack. Popping an action executes the inverse mutation and pushes it onto Redo.
              </p>

              <div className="space-y-3 pt-2">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-bold text-slate-800 block">Undo Stack</span>
                    <span className="text-[0.7rem] text-slate-500 font-mono">
                      {queueStatus?.undo_history_count ?? 0} actions recorded
                    </span>
                  </div>
                  <button
                    onClick={handleUndo}
                    disabled={!queueStatus?.can_undo}
                    className="px-3 py-1.5 rounded bg-white border border-slate-200 text-slate-700 hover:text-brand font-semibold shadow-xs disabled:opacity-40"
                  >
                    Undo
                  </button>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-bold text-slate-800 block">Redo Stack</span>
                    <span className="text-[0.7rem] text-slate-500 font-mono">
                      {queueStatus?.redo_history_count ?? 0} actions stored
                    </span>
                  </div>
                  <button
                    onClick={handleRedo}
                    disabled={!queueStatus?.can_redo}
                    className="px-3 py-1.5 rounded bg-white border border-slate-200 text-slate-700 hover:text-brand font-semibold shadow-xs disabled:opacity-40"
                  >
                    Redo
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 text-[0.72rem] font-mono text-slate-500 space-y-1">
                <div>&bull; Session-Local in-memory history</div>
                <div>&bull; Mutations durably persisted in SQLite</div>
                <div>&bull; New action clears Redo stack</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 2: SEARCHING & SORTING LAB */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'search-sort' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Searching Lab */}
          <div className="pt-card p-6 space-y-5">
            <div>
              <span className="pt-pill pt-pill-blue">CO4 &bull; SEARCH BENCHMARK</span>
              <h3 className="font-display font-bold text-slate-900 text-lg mt-1">
                Linear Search vs. Binary Search
              </h3>
              <p className="text-xs text-slate-600 mt-1">
                Compares sequential $O(N)$ scan against divide-and-conquer $O(\log N)$ on identical datasets.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Dataset Size (N)</label>
                <select
                  value={searchSize}
                  onChange={(e) => setSearchSize(parseInt(e.target.value, 10))}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 font-mono"
                >
                  <option value={100}>N = 100</option>
                  <option value={1000}>N = 1,000</option>
                  <option value={5000}>N = 5,000</option>
                  <option value={20000}>N = 20,000</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Scenario</label>
                <select
                  value={searchScenario}
                  onChange={(e) => setSearchScenario(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 font-mono"
                >
                  <option value="first">First Item (Best Case)</option>
                  <option value="middle">Middle Item (Average)</option>
                  <option value="last">Last Item (Worst Case)</option>
                  <option value="absent">Target Absent (Worst Case)</option>
                </select>
              </div>
            </div>

            <button
              onClick={runSearch}
              disabled={searchLoading}
              className="w-full py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-semibold transition-colors shadow-xs"
            >
              {searchLoading ? 'Executing Python Benchmark...' : 'Run Search Benchmark'}
            </button>

            {searchResult && (
              <div className="space-y-3 pt-3 border-t border-slate-100">
                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                    <div className="text-[0.68rem] text-slate-400 uppercase">Linear Search O(N)</div>
                    <div className="text-base font-bold text-slate-900">{searchResult.linear_time_ms} ms</div>
                    <div className="text-[0.7rem] text-slate-600">
                      Comparisons: <strong className="text-brand">{searchResult.linear_comparisons}</strong>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-blue-50/70 border border-blue-200 space-y-1">
                    <div className="text-[0.68rem] text-blue-600 uppercase">Binary Search O(log N)</div>
                    <div className="text-base font-bold text-brand">{searchResult.binary_time_ms} ms</div>
                    <div className="text-[0.7rem] text-slate-600">
                      Comparisons: <strong className="text-brand">{searchResult.binary_comparisons}</strong>
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-mono flex items-center justify-between">
                  <span>Speedup Factor:</span>
                  <strong className="text-sm">{searchResult.speedup_factor}x faster</strong>
                </div>
              </div>
            )}
          </div>

          {/* Sorting Lab */}
          <div className="pt-card p-6 space-y-5">
            <div>
              <span className="pt-pill pt-pill-amber">CO4 &bull; SORT BENCHMARK</span>
              <h3 className="font-display font-bold text-slate-900 text-lg mt-1">
                Insertion Sort vs. Merge Sort
              </h3>
              <p className="text-xs text-slate-600 mt-1">
                Compares in-place adaptive $O(N^2)$ against divide-and-conquer $O(N \log N)$ sorting.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Dataset Size (N)</label>
                <select
                  value={sortSize}
                  onChange={(e) => setSortSize(parseInt(e.target.value, 10))}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 font-mono"
                >
                  <option value={100}>N = 100</option>
                  <option value={500}>N = 500</option>
                  <option value={1000}>N = 1,000</option>
                  <option value={2000}>N = 2,000</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Distribution</label>
                <select
                  value={sortDist}
                  onChange={(e) => setSortDist(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 font-mono"
                >
                  <option value="random">Random Order</option>
                  <option value="sorted">Already Sorted (Adaptive)</option>
                  <option value="reversed">Reverse Sorted (Worst Case)</option>
                </select>
              </div>
            </div>

            <button
              onClick={runSort}
              disabled={sortLoading}
              className="w-full py-2.5 rounded-lg bg-slate-900 hover:bg-brand text-white text-xs font-semibold transition-colors shadow-xs"
            >
              {sortLoading ? 'Executing Python Benchmark...' : 'Run Sorting Benchmark'}
            </button>

            {sortResult && (
              <div className="space-y-3 pt-3 border-t border-slate-100">
                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                    <div className="text-[0.68rem] text-slate-400 uppercase">Insertion Sort O(N²)</div>
                    <div className="text-base font-bold text-slate-900">{sortResult.insertion_time_ms} ms</div>
                    <div className="text-[0.7rem] text-slate-600">
                      Comparisons: <strong className="text-amber-600">{sortResult.insertion_comparisons}</strong>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-blue-50/70 border border-blue-200 space-y-1">
                    <div className="text-[0.68rem] text-blue-600 uppercase">Merge Sort O(N log N)</div>
                    <div className="text-base font-bold text-brand">{sortResult.merge_time_ms} ms</div>
                    <div className="text-[0.7rem] text-slate-600">
                      Comparisons: <strong className="text-brand">{sortResult.merge_comparisons}</strong>
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-mono flex items-center justify-between">
                  <span>Speedup Factor:</span>
                  <strong className="text-sm">{sortResult.speedup_factor}x faster</strong>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 3: BST DEADLINE INDEX */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'bst' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="pt-card p-4">
              <span className="text-[0.68rem] font-mono uppercase text-slate-400">Total Tree Nodes</span>
              <div className="text-2xl font-display font-bold text-slate-900 mt-1">
                {treeOverview?.total_nodes ?? 0}
              </div>
            </div>
            <div className="pt-card p-4">
              <span className="text-[0.68rem] font-mono uppercase text-slate-400">Tree Height</span>
              <div className="text-2xl font-display font-bold text-brand mt-1">
                {treeOverview?.height ?? 0}
              </div>
            </div>
            <div className="pt-card p-4">
              <span className="text-[0.68rem] font-mono uppercase text-slate-400">Tree Balance</span>
              <div className="text-2xl font-display font-bold text-emerald-600 mt-1">
                {treeOverview?.is_balanced ? 'Well Balanced' : 'Normal Skew'}
              </div>
            </div>
          </div>

          <div className="pt-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className="pt-pill pt-pill-blue">TREE TRAVERSALS</span>
                <h3 className="font-display font-bold text-slate-900">Ordered Deadline Sequence</h3>
              </div>
              <div className="flex gap-1 text-xs font-mono">
                {(['inorder', 'preorder', 'postorder'] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setTreeTab(mode)}
                    className={`px-3 py-1 rounded-md capitalize transition-colors ${
                      treeTab === mode ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>

            {/* Traversal Output Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[0.7rem]">
                  <tr>
                    <th className="py-2.5 px-4">Visit #</th>
                    <th className="py-2.5 px-4">Task ID</th>
                    <th className="py-2.5 px-4">Title</th>
                    <th className="py-2.5 px-4">Priority</th>
                    <th className="py-2.5 px-4">Deadline</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(treeTab === 'inorder'
                    ? treeOverview?.inorder_tasks
                    : treeTab === 'preorder'
                    ? treeOverview?.preorder_tasks
                    : treeOverview?.postorder_tasks
                  )?.map((t, idx) => (
                    <tr key={t.id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-4 text-slate-400">#{idx + 1}</td>
                      <td className="py-2.5 px-4 text-brand font-bold">#{t.id}</td>
                      <td className="py-2.5 px-4 font-sans font-semibold text-slate-800">{t.title}</td>
                      <td className="py-2.5 px-4 text-slate-600">{t.priority_label}</td>
                      <td className="py-2.5 px-4 text-slate-500">{t.due_date_formatted}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 4: CUSTOM HASH TABLE */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'hash' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 font-mono">
            <div className="pt-card p-3">
              <span className="text-[0.68rem] uppercase text-slate-400">Buckets (m)</span>
              <div className="text-xl font-bold text-slate-900 mt-0.5">{hashStats?.capacity ?? 0}</div>
            </div>
            <div className="pt-card p-3">
              <span className="text-[0.68rem] uppercase text-slate-400">Size (n)</span>
              <div className="text-xl font-bold text-brand mt-0.5">{hashStats?.size ?? 0}</div>
            </div>
            <div className="pt-card p-3">
              <span className="text-[0.68rem] uppercase text-slate-400">Load Factor</span>
              <div className="text-xl font-bold text-slate-800 mt-0.5">{hashStats?.load_factor ?? 0}</div>
            </div>
            <div className="pt-card p-3">
              <span className="text-[0.68rem] uppercase text-slate-400">Occupied</span>
              <div className="text-xl font-bold text-emerald-600 mt-0.5">{hashStats?.occupied_buckets ?? 0}</div>
            </div>
            <div className="pt-card p-3">
              <span className="text-[0.68rem] uppercase text-slate-400">Collisions</span>
              <div className="text-xl font-bold text-amber-600 mt-0.5">{hashStats?.collision_count ?? 0}</div>
            </div>
            <div className="pt-card p-3">
              <span className="text-[0.68rem] uppercase text-slate-400">Max Chain</span>
              <div className="text-xl font-bold text-rose-600 mt-0.5">{hashStats?.max_chain_length ?? 0}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Interactive Key Lookup */}
            <div className="pt-card p-6 space-y-4">
              <span className="pt-pill pt-pill-blue">O(1) AVERAGE RETRIEVAL</span>
              <h3 className="font-display font-bold text-slate-900">Task ID Direct Lookup</h3>
              <p className="text-xs text-slate-600">
                Retrieves record directly by hashing the Task ID and traversing the bucket linked chain.
              </p>

              <div className="flex gap-2 text-xs">
                <input
                  type="number"
                  placeholder="Enter Task ID"
                  value={lookupId}
                  onChange={(e) => setLookupId(e.target.value)}
                  className="px-3 py-2 rounded-lg border border-slate-200 font-mono w-40"
                />
                <button
                  onClick={runHashLookup}
                  className="px-4 py-2 rounded-lg bg-brand hover:bg-brand-hover text-white font-semibold shadow-xs"
                >
                  Lookup Task
                </button>
              </div>

              {lookupResult && (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs font-mono">
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <strong className={lookupResult.found ? 'text-emerald-600' : 'text-rose-600'}>
                      {lookupResult.found ? 'Found in Bucket' : 'Key Absent'}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Key Comparisons:</span>
                    <strong className="text-brand">{lookupResult.comparisons}</strong>
                  </div>
                  {lookupResult.task && (
                    <div className="pt-2 border-t border-slate-200">
                      <div className="font-sans font-bold text-slate-900 text-sm">
                        #{lookupResult.task.id}: {lookupResult.task.title}
                      </div>
                      <div className="text-slate-500 text-[0.72rem]">
                        {lookupResult.task.priority_label} &bull; {lookupResult.task.duration_formatted}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Bucket Distribution Histogram */}
            <div className="pt-card p-6 space-y-4">
              <span className="pt-pill pt-pill-green">SEPARATE CHAINING</span>
              <h3 className="font-display font-bold text-slate-900">Bucket Chain Lengths</h3>
              <div className="flex items-end gap-1.5 h-36 pt-4 border-b border-slate-200">
                {hashStats?.bucket_distribution.map((len, idx) => {
                  const maxChain = hashStats.max_chain_length || 1;
                  const heightPct = Math.max(8, (len / maxChain) * 100);
                  return (
                    <div
                      key={idx}
                      title={`Bucket ${idx}: ${len} items`}
                      className="flex-1 rounded-t transition-all hover:bg-brand"
                      style={{
                        height: `${heightPct}%`,
                        backgroundColor: len === 0 ? '#E2E8F0' : len > 1 ? '#F59E0B' : '#2563EB',
                      }}
                    />
                  );
                })}
              </div>
              <div className="flex justify-between text-[0.7rem] font-mono text-slate-400">
                <span>Bucket #0</span>
                <span>Bucket #{Math.max(0, (hashStats?.capacity ?? 1) - 1)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 5: CO2 STRUCTURE EVALUATION */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'eval' && (
        <div className="pt-card p-6 space-y-5">
          <div>
            <span className="pt-pill pt-pill-blue">CO2 RIGOROUS EVALUATION</span>
            <h3 className="font-display font-bold text-slate-900 text-lg mt-1">
              Empirical Comparison: List vs. Hash Table vs. BST
            </h3>
            <p className="text-xs text-slate-600 mt-1">
              Directly addresses Course Outcome 2: Evaluate the suitability of data structures for efficient storage and retrieval.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Dataset Size</label>
              <select
                value={evalSize}
                onChange={(e) => setEvalSize(parseInt(e.target.value, 10))}
                className="px-3 py-1.5 rounded-lg border border-slate-200 font-mono"
              >
                <option value={50}>N = 50</option>
                <option value={100}>N = 100</option>
                <option value={500}>N = 500</option>
                <option value={1000}>N = 1,000</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Scenario</label>
              <select
                value={evalScenario}
                onChange={(e) => setEvalScenario(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 font-mono"
              >
                <option value="early">Early Index (Best Case for List)</option>
                <option value="middle">Middle Index (Typical Average)</option>
                <option value="late">Late Index (Near Worst Case for List)</option>
                <option value="absent">Key Absent (Full Search Scan)</option>
              </select>
            </div>

            <div className="self-end">
              <button
                onClick={runEval}
                disabled={evalLoading}
                className="px-5 py-2 rounded-lg bg-brand hover:bg-brand-hover text-white font-semibold transition-colors shadow-xs"
              >
                {evalLoading ? 'Running Evaluation...' : 'Run Comparative Evaluation'}
              </button>
            </div>
          </div>

          {evalResults.length > 0 && (
            <div className="overflow-x-auto pt-2">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[0.7rem]">
                  <tr>
                    <th className="py-3 px-4">Data Structure</th>
                    <th className="py-3 px-4">Theoretical Complexity</th>
                    <th className="py-3 px-4">Build Time</th>
                    <th className="py-3 px-4">Lookup Time (avg)</th>
                    <th className="py-3 px-4">Key Comparisons</th>
                    <th className="py-3 px-4">Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {evalResults.map((r) => (
                    <tr key={r.structure_name} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-bold text-slate-900">{r.structure_name}</td>
                      <td className="py-3 px-4 text-brand">
                        {r.structure_name.includes('Hash')
                          ? 'O(1) avg / O(n) worst'
                          : r.structure_name.includes('BST')
                          ? 'O(log n) avg / O(n) worst'
                          : 'O(n) linear scan'}
                      </td>
                      <td className="py-3 px-4 text-slate-600">{r.construction_time_ms} ms</td>
                      <td className="py-3 px-4 text-slate-900 font-bold">{r.lookup_time_avg_us} μs</td>
                      <td className="py-3 px-4 text-emerald-600 font-bold">{r.comparisons_count}</td>
                      <td className="py-3 px-4 text-[0.72rem] text-slate-600">
                        {r.structure_name.includes('Hash')
                          ? 'Optimal for exact ID lookups'
                          : r.structure_name.includes('BST')
                          ? 'Optimal for ordered deadline ranges'
                          : 'Poor scalability for frequent lookups'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

