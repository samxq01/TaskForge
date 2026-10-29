'use client';

import React, { useEffect, useState } from 'react';
import {
  Calendar,
  AlertTriangle,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Sliders,
  Play,
  RotateCcw,
} from 'lucide-react';
import {
  api,
  CriticalPathResult,
  WhatIfResult,
  Task,
} from '@/lib/api-client';

export default function PlanningPage() {
  const [criticalPath, setCriticalPath] = useState<CriticalPathResult | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Simulation State
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [delayMinutes, setDelayMinutes] = useState<number>(30);
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResult | null>(null);
  const [simLoading, setSimLoading] = useState<boolean>(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cp, taskList] = await Promise.all([
        api.getCriticalPath(),
        api.getTasks(),
      ]);
      setCriticalPath(cp);
      setTasks(taskList);
      if (taskList.length > 0 && !selectedTaskId) {
        setSelectedTaskId(taskList[0].id.toString());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSimulate = async () => {
    const id = parseInt(selectedTaskId, 10);
    if (isNaN(id)) return;

    try {
      setSimLoading(true);
      const res = await api.simulateWhatIf(id, delayMinutes);
      setWhatIfResult(res);
    } catch (err: any) {
      alert(err.message || 'Simulation error');
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="pt-pill pt-pill-blue">CO5 PROJECT PLANNING</span>
            <span className="text-xs font-mono text-slate-500">Dynamic Programming over DAG</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-extrabold text-slate-900 mt-1">
            Critical Path &amp; What-If Schedule Simulator
          </h1>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 1: CRITICAL PATH METRIC OVERVIEW */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="pt-card p-6 border-l-4 border-l-brand space-y-1">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-brand">Estimated Project Duration</span>
          <div className="text-3xl font-sans font-extrabold text-slate-900 tracking-tight tabular-nums">
            {criticalPath?.total_duration_formatted ?? '0 min'}
          </div>
          <p className="text-xs text-slate-500">
            Longest cumulative dependency path across all project DAG branches.
          </p>
        </div>

        <div className="pt-card p-6 space-y-1">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-400">Critical Path Tasks</span>
          <div className="text-3xl font-sans font-extrabold text-slate-900 tracking-tight tabular-nums">
            {criticalPath?.critical_path_ids.length ?? 0} <span className="text-sm font-normal text-slate-500">of {tasks.length} tasks</span>
          </div>
          <p className="text-xs text-slate-500">
            Any delay on these specific tasks directly extends project completion time.
          </p>
        </div>

        <div className="pt-card p-6 space-y-1">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-400">Critical Chain Sequence</span>
          <div className="text-base font-sans font-bold text-brand truncate pt-1">
            {criticalPath?.critical_path_ids.length ? (
              criticalPath.critical_path_ids.map((id) => `#${id}`).join(' → ')
            ) : (
              'No dependencies'
            )}
          </div>
          <p className="text-xs text-slate-500">
            Zero slack tasks governing overall project velocity.
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 2: GANTT SCHEDULE BREAKDOWN TABLE */}
      {/* ------------------------------------------------------------- */}
      <div className="pt-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <span className="pt-pill pt-pill-blue">DYNAMIC PROGRAMMING TIMELINE</span>
            <h3 className="font-display font-bold text-slate-900 mt-1">Schedule &amp; Float Details</h3>
          </div>
          <span className="text-xs font-mono text-slate-500">
            ES: Earliest Start &bull; EF: Earliest Finish
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[0.7rem]">
              <tr>
                <th className="py-2.5 px-4">Task</th>
                <th className="py-2.5 px-4">Duration</th>
                <th className="py-2.5 px-4">Earliest Start (ES)</th>
                <th className="py-2.5 px-4">Earliest Finish (EF)</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Critical?</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {criticalPath?.schedule_details.map((item) => (
                <tr
                  key={item.task_id}
                  className={`hover:bg-slate-50 ${item.is_on_critical_path ? 'bg-blue-50/30' : ''}`}
                >
                  <td className="py-2.5 px-4 font-sans font-semibold text-slate-800">
                    <span className="font-mono text-brand font-bold">#{item.task_id}</span> {item.task_title}
                  </td>
                  <td className="py-2.5 px-4">{item.duration_minutes} min</td>
                  <td className="py-2.5 px-4 text-slate-600">t = {item.earliest_start} min</td>
                  <td className="py-2.5 px-4 text-slate-900 font-bold">t = {item.earliest_finish} min</td>
                  <td className="py-2.5 px-4">
                    {item.predecessor_id ? `Follows #${item.predecessor_id}` : 'Root'}
                  </td>
                  <td className="py-2.5 px-4">
                    {item.is_on_critical_path ? (
                      <span className="pt-pill pt-pill-red">CRITICAL</span>
                    ) : (
                      <span className="pt-pill pt-pill-slate">Has Float</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 3: WHAT-IF SCHEDULE SIMULATOR */}
      {/* ------------------------------------------------------------- */}
      <div className="pt-card p-6 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-3 border-b border-slate-100">
          <div>
            <span className="pt-pill pt-pill-amber">WHAT-IF SIMULATION ENGINE</span>
            <h3 className="font-display font-bold text-slate-900 text-lg mt-1">
              Simulate Delay Propagation
            </h3>
            <p className="text-xs text-slate-600">
              Test hypothetical delays without mutating persistent SQLite database records.
            </p>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[0.72rem] font-mono">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Strict In-Memory Guarantee: Zero DB Mutation</span>
          </div>
        </div>

        {/* Simulator Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Target Incomplete Task</label>
            <select
              value={selectedTaskId}
              onChange={(e) => setSelectedTaskId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 font-mono"
            >
              {tasks.filter((t) => t.status !== 'Completed').map((t) => (
                <option key={t.id} value={t.id}>
                  #{t.id}: {t.title} ({t.duration_formatted})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Simulated Delay: <strong className="text-brand">{delayMinutes} minutes</strong>
            </label>
            <input
              type="range"
              min={10}
              max={240}
              step={10}
              value={delayMinutes}
              onChange={(e) => setDelayMinutes(parseInt(e.target.value, 10))}
              className="w-full mt-2 accent-brand"
            />
          </div>

          <div className="self-end">
            <button
              onClick={handleSimulate}
              disabled={simLoading}
              className="w-full py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white font-semibold transition-colors shadow-xs"
            >
              {simLoading ? 'Simulating Schedule Impact...' : 'Run What-If Simulation'}
            </button>
          </div>
        </div>

        {/* Simulation Output */}
        {whatIfResult && (
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-[0.68rem] text-slate-400 uppercase">Baseline Duration</span>
                <div className="text-xl font-bold text-slate-800">
                  {whatIfResult.baseline_project_duration} min
                </div>
              </div>

              <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 space-y-1">
                <span className="text-[0.68rem] text-brand uppercase">Simulated Duration</span>
                <div className="text-xl font-bold text-brand">
                  {whatIfResult.simulated_project_duration} min
                </div>
              </div>

              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-1">
                <span className="text-[0.68rem] text-amber-700 uppercase">Project Slippage</span>
                <div className="text-xl font-bold text-amber-800">
                  +{whatIfResult.project_delay_increase} min
                </div>
              </div>
            </div>

            <p className="text-xs font-mono text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200">
              {whatIfResult.explanation}
            </p>

            {/* Impact Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[0.7rem]">
                  <tr>
                    <th className="py-2.5 px-4">Task</th>
                    <th className="py-2.5 px-4">Baseline Finish</th>
                    <th className="py-2.5 px-4">Simulated Finish</th>
                    <th className="py-2.5 px-4">Delay Delta</th>
                    <th className="py-2.5 px-4">Impact Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {whatIfResult.impacts.map((imp) => (
                    <tr key={imp.task_id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-4 font-sans font-semibold text-slate-800">
                        <span className="font-mono text-brand font-bold">#{imp.task_id}</span> {imp.task_title}
                      </td>
                      <td className="py-2.5 px-4 text-slate-500">t = {imp.baseline_finish} min</td>
                      <td className="py-2.5 px-4 text-slate-900 font-bold">t = {imp.simulated_finish} min</td>
                      <td className="py-2.5 px-4 text-amber-700 font-bold">
                        {imp.finish_delay_minutes > 0 ? `+${imp.finish_delay_minutes} min` : '0 min'}
                      </td>
                      <td className="py-2.5 px-4">
                        {imp.is_affected ? (
                          <span className="pt-pill pt-pill-amber">DELAYED</span>
                        ) : (
                          <span className="pt-pill pt-pill-slate">Unaffected</span>
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
    </div>
  );
}

