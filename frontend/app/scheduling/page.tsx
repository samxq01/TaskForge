'use client';

import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  AlertTriangle,
  Clock,
  Calendar,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { api, SmartScheduleResult, RiskSummary } from '@/lib/api-client';

export default function SchedulingPage() {
  const [schedule, setSchedule] = useState<SmartScheduleResult | null>(null);
  const [risks, setRisks] = useState<RiskSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'scheduler' | 'risks'>('scheduler');

  const loadData = async () => {
    try {
      setLoading(true);
      const [s, r] = await Promise.all([
        api.getSchedulingRecommendations(),
        api.getDeadlineRisks(),
      ]);
      setSchedule(s);
      setRisks(r);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-sans font-extrabold text-slate-900 tracking-tight">
            Schedule
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Recommended tasks, priority order, and deadline risk assessment.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('scheduler')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              activeTab === 'scheduler' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Recommended Schedule
          </button>
          <button
            onClick={() => setActiveTab('risks')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              activeTab === 'risks' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Deadline Risks
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 1: AUTO-SCHEDULER VIEW */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'scheduler' && (
        <div className="space-y-6">
          {/* Top Recommendation Banner */}
          {schedule?.recommendation ? (
            <div className="bg-white rounded-xl border border-blue-200 p-6 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="pt-pill pt-pill-blue">
                  <span className="pt-dot pt-dot-blue" />
                  RECOMMENDED NEXT TASK
                </span>
                <span className="text-xs font-sans font-bold text-brand bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                  {schedule.recommendation.task.priority_label}
                </span>
              </div>

              <h2 className="text-xl sm:text-2xl font-sans font-bold text-slate-900">
                #{schedule.recommendation.task.id}: {schedule.recommendation.task.title}
              </h2>

              <p className="text-xs sm:text-sm text-slate-600 max-w-3xl">
                {schedule.recommendation.explanation}
              </p>

              <div className="pt-3 border-t border-slate-100 flex flex-wrap gap-4 text-xs font-sans text-slate-500">
                <span>⏱️ Duration: <strong className="text-slate-800">{schedule.recommendation.task.duration_formatted}</strong></span>
                <span>🗓️ Deadline: <strong className="text-slate-800">{schedule.recommendation.task.due_date_formatted}</strong></span>
                <span className="text-emerald-600 font-semibold">✓ All Prerequisites Satisfied</span>
              </div>
            </div>
          ) : (
            <div className="pt-card p-8 text-center text-xs text-slate-400">
              No eligible Pending tasks available for recommendation. All pending tasks may be blocked by prerequisites or completed.
            </div>
          )}

          {/* Ranked Eligible Tasks */}
          <div className="pt-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-sans font-bold text-slate-900 text-sm">
                  Recommended Execution Order ({schedule?.ranked_tasks.length ?? 0})
                </h3>
                <p className="text-xs text-slate-500">Ranked by priority, approaching deadlines, and shortest duration</p>
              </div>
            </div>

            <div className="divide-y divide-slate-100">
              {schedule?.ranked_tasks.map((item) => (
                <div key={item.task.id} className="py-3.5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
                  <div className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-bold flex items-center justify-center shrink-0 text-xs">
                      {item.rank}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-brand">#{item.task.id}</span>
                        <span className="font-semibold text-slate-900 text-sm">{item.task.title}</span>
                        <span className="text-[11px] font-sans px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium">
                          {item.task.priority_label}
                        </span>
                      </div>
                      <p className="text-slate-600 text-xs mt-0.5">{item.explanation}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-sans text-slate-500 self-end md:self-center">
                    <span>⏱️ {item.task.duration_formatted}</span>
                    <span>🗓️ {item.task.due_date_formatted}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Blocked Tasks */}
          {schedule?.blocked_tasks && schedule.blocked_tasks.length > 0 && (
            <div className="pt-card p-6 space-y-4">
              <div>
                <h3 className="font-sans font-bold text-slate-900 text-sm">
                  Tasks Waiting on Prerequisites ({schedule.blocked_tasks.length})
                </h3>
                <p className="text-xs text-slate-500">These tasks become eligible once their prerequisites are completed</p>
              </div>

              <div className="divide-y divide-slate-100 text-xs">
                {schedule.blocked_tasks.map(({ task, blocking_prerequisites }) => (
                  <div key={task.id} className="py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                    <div>
                      <span className="text-brand font-bold">#{task.id}</span>{' '}
                      <span className="font-semibold text-slate-800">{task.title}</span>
                    </div>
                    <div className="text-xs text-slate-500">
                      Waiting for:{' '}
                      <span className="text-amber-700 font-semibold">
                        {blocking_prerequisites.map((p) => `#${p.id} (${p.title})`).join(', ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SECTION 2: DEADLINE RISK ANALYZER */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'risks' && (
        <div className="space-y-6">
          {/* Risk Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="pt-card p-4 border-l-4 border-l-rose-500">
              <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-rose-600">Overdue Tasks</span>
              <div className="text-2xl font-sans font-extrabold text-rose-700 mt-1 tabular-nums">
                {risks?.overdue_count ?? 0}
              </div>
            </div>

            <div className="pt-card p-4 border-l-4 border-l-amber-500">
              <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-amber-600">At Risk</span>
              <div className="text-2xl font-sans font-extrabold text-amber-700 mt-1 tabular-nums">
                {risks?.at_risk_count ?? 0}
              </div>
            </div>

            <div className="pt-card p-4 border-l-4 border-l-emerald-500">
              <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-emerald-600">Safe Deadlines</span>
              <div className="text-2xl font-sans font-extrabold text-emerald-700 mt-1 tabular-nums">
                {risks?.safe_count ?? 0}
              </div>
            </div>

            <div className="pt-card p-4 border-l-4 border-l-slate-400">
              <span className="text-[11px] font-sans font-bold uppercase tracking-wider text-slate-500">Unscheduled</span>
              <div className="text-2xl font-sans font-extrabold text-slate-700 mt-1 tabular-nums">
                {risks?.unscheduled_count ?? 0}
              </div>
            </div>
          </div>

          {/* Assessment Table */}
          <div className="pt-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-sans">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[11px] tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Task</th>
                    <th className="py-3 px-4">Risk Category</th>
                    <th className="py-3 px-4">Deadline</th>
                    <th className="py-3 px-4">Remaining</th>
                    <th className="py-3 px-4">Slack</th>
                    <th className="py-3 px-4">Diagnostic Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {risks?.assessments.map((a) => (
                    <tr key={a.task_id} className="hover:bg-slate-50">
                      <td className="py-3 px-4">
                        <span className="font-bold text-brand">#{a.task_id}</span>{' '}
                        <span className="font-sans font-semibold text-slate-900">{a.task_title}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-[0.7rem] px-2 py-0.5 rounded font-semibold ${
                            a.risk_category === 'Overdue'
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : a.risk_category === 'At Risk'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : a.risk_category === 'Safe'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : a.risk_category === 'Completed'
                              ? 'bg-blue-50 text-blue-700 border border-blue-200'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {a.risk_category}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600">{a.deadline_formatted}</td>
                      <td className="py-3 px-4 text-slate-700">
                        {a.time_remaining_minutes !== null ? `${Math.round(a.time_remaining_minutes / 60)} hrs` : '—'}
                      </td>
                      <td className="py-3 px-4 text-slate-700">
                        {a.slack_minutes !== null ? `${Math.round(a.slack_minutes / 60)} hrs` : '—'}
                      </td>
                      <td className="py-3 px-4 text-[0.72rem] text-slate-600 font-sans">{a.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

