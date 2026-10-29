'use client';

import React, { useEffect, useState } from 'react';
import {
  CalendarClock,
  Clock,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Layers,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { api, CriticalPathResult, WhatIfResult, Task } from '@/lib/api-client';

export default function PlanningPage() {
  const [criticalPath, setCriticalPath] = useState<CriticalPathResult | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // What-If Simulation State
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
        // default to first non-completed task or first task
        const pending = taskList.find((t) => t.status !== 'Completed');
        setSelectedTaskId(pending ? pending.id.toString() : taskList[0].id.toString());
      }
    } catch (err: any) {
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
      alert(err.message || 'Error simulating delay');
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-sans font-extrabold text-slate-900 tracking-tight">
            Project Timeline
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Track estimated project duration, identify critical tasks, and simulate delay impacts.
          </p>
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
            Total project completion time governed by the longest dependency path.
          </p>
        </div>

        <div className="pt-card p-6 space-y-1">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-400">Tasks Determining Finish Date</span>
          <div className="text-3xl font-sans font-extrabold text-slate-900 tracking-tight tabular-nums">
            {criticalPath?.critical_path_ids.length ?? 0} <span className="text-sm font-normal text-slate-500">of {tasks.length} tasks</span>
          </div>
          <p className="text-xs text-slate-500">
            Delays to these specific tasks will directly delay the overall project finish.
          </p>
        </div>

        <div className="pt-card p-6 space-y-1">
          <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-400">Critical Sequence</span>
          <div className="text-base font-sans font-bold text-brand truncate pt-1">
            {criticalPath?.critical_path_ids.length ? (
              criticalPath.critical_path_ids.map((id) => `#${id}`).join(' → ')
            ) : (
              'No dependencies'
            )}
          </div>
          <p className="text-xs text-slate-500">
            Tasks with zero schedule float governing project velocity.
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 2: SCHEDULE BREAKDOWN TABLE */}
      {/* ------------------------------------------------------------- */}
      <div className="pt-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 className="font-sans font-bold text-slate-900 text-sm">Schedule Breakdown</h3>
            <p className="text-xs text-slate-500">Earliest start and finish schedule in minutes from project kick-off</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[11px] font-bold tracking-wider">
              <tr>
                <th className="py-2.5 px-4">Task</th>
                <th className="py-2.5 px-4">Duration</th>
                <th className="py-2.5 px-4">Estimated Start</th>
                <th className="py-2.5 px-4">Estimated Finish</th>
                <th className="py-2.5 px-4">Sequence Predecessor</th>
                <th className="py-2.5 px-4">Critical to Finish?</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {criticalPath?.schedule_details.map((item) => (
                <tr
                  key={item.task_id}
                  className={`hover:bg-slate-50 ${item.is_on_critical_path ? 'bg-blue-50/30' : ''}`}
                >
                  <td className="py-2.5 px-4 font-semibold text-slate-800">
                    <span className="text-brand font-bold">#{item.task_id}</span> {item.task_title}
                  </td>
                  <td className="py-2.5 px-4">{item.duration_minutes} min</td>
                  <td className="py-2.5 px-4 text-slate-600">t = {item.earliest_start} min</td>
                  <td className="py-2.5 px-4 text-slate-900 font-bold">t = {item.earliest_finish} min</td>
                  <td className="py-2.5 px-4 text-slate-600">
                    {item.predecessor_id ? `Follows #${item.predecessor_id}` : 'Root Task'}
                  </td>
                  <td className="py-2.5 px-4">
                    {item.is_on_critical_path ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        Critical
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600">
                        Flexible
                      </span>
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
            <h3 className="font-sans font-bold text-slate-900 text-base">
              What-If Schedule Simulator
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Simulate how delaying an individual task ripples through the overall project completion time.
            </p>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Simulation only — saved task data will not change.</span>
          </div>
        </div>

        {/* Simulator Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Select Task to Delay</label>
            <select
              value={selectedTaskId}
              onChange={(e) => setSelectedTaskId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 font-sans text-xs"
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
              Hypothetical Delay: <strong className="text-brand">{delayMinutes} minutes</strong>
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
              {simLoading ? 'Calculating Impact...' : 'Run What-If Simulation'}
            </button>
          </div>
        </div>

        {/* Simulation Output */}
        {whatIfResult && (
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Baseline Project Time</span>
                <div className="text-xl font-bold text-slate-800 tabular-nums">
                  {whatIfResult.baseline_project_duration} min
                </div>
              </div>

              <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 space-y-1">
                <span className="text-[11px] text-brand font-bold uppercase tracking-wider">Simulated Project Time</span>
                <div className="text-xl font-bold text-brand tabular-nums">
                  {whatIfResult.simulated_project_duration} min
                </div>
              </div>

              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-1">
                <span className="text-[11px] text-amber-700 font-bold uppercase tracking-wider">Project Delay Increase</span>
                <div className="text-xl font-bold text-amber-800 tabular-nums">
                  +{whatIfResult.project_delay_increase} min
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed font-sans">
              {whatIfResult.explanation}
            </p>

            {/* Impact Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-sans">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[11px] font-bold tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Task</th>
                    <th className="py-2.5 px-4">Baseline Finish</th>
                    <th className="py-2.5 px-4">Simulated Finish</th>
                    <th className="py-2.5 px-4">Delay Impact</th>
                    <th className="py-2.5 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {whatIfResult.impacts.map((imp) => (
                    <tr key={imp.task_id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-4 font-semibold text-slate-800">
                        <span className="text-brand font-bold">#{imp.task_id}</span> {imp.task_title}
                      </td>
                      <td className="py-2.5 px-4 text-slate-500">t = {imp.baseline_finish} min</td>
                      <td className="py-2.5 px-4 text-slate-900 font-bold">t = {imp.simulated_finish} min</td>
                      <td className="py-2.5 px-4 text-amber-700 font-semibold">
                        {imp.finish_delay_minutes > 0 ? `+${imp.finish_delay_minutes} min` : '0 min'}
                      </td>
                      <td className="py-2.5 px-4">
                        {imp.is_affected ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                            Delayed
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600">
                            Unaffected
                          </span>
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
