'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Layers,
  CheckSquare,
  FlaskConical,
  GitBranch,
  CalendarClock,
  Sparkles,
  RotateCcw,
  RotateCw,
  Workflow,
  ArrowRight,
} from 'lucide-react';
import { api, Overview } from '@/lib/api-client';

export function Navbar() {
  const pathname = usePathname();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [isApiOnline, setIsApiOnline] = useState<boolean>(true);

  const fetchStatus = async () => {
    try {
      const data = await api.getOverview();
      setOverview(data);
      setIsApiOnline(true);
    } catch {
      setIsApiOnline(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleUndo = async () => {
    try {
      await api.undo();
      fetchStatus();
    } catch (err: any) {
      alert(err.message || 'Cannot undo');
    }
  };

  const handleRedo = async () => {
    try {
      await api.redo();
      fetchStatus();
    } catch (err: any) {
      alert(err.message || 'Cannot redo');
    }
  };

  const navLinks = [
    { href: '/', label: 'Product' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/tasks', label: 'Tasks' },
    { href: '/laboratory', label: 'DSA Labs' },
    { href: '/dependencies', label: 'Dependencies' },
    { href: '/scheduling', label: 'Smart Scheduler' },
    { href: '/planning', label: 'Critical Path & What-If' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-surface/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Lockup */}
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 group">
              <span className="font-display text-xl font-extrabold tracking-tight text-slate-900 group-hover:text-brand transition-colors">
                TaskForge
              </span>
              <span className="w-2 h-2 rounded-full bg-brand group-hover:scale-125 transition-transform" />
              <span className="hidden sm:inline-block text-[0.7rem] font-mono font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                DSA 2.0
              </span>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden lg:flex items-center gap-1">
              {navLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                      isActive
                        ? 'bg-brand text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Actions: Undo/Redo & Live Status */}
          <div className="flex items-center gap-3">
            {/* Live API Heartbeat */}
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200 text-[0.72rem] font-mono">
              <span
                className={`w-2 h-2 rounded-full ${
                  isApiOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
                }`}
              />
              <span className="hidden sm:inline text-slate-600">
                {isApiOnline ? 'FastAPI 8000' : 'Backend Offline'}
              </span>
            </div>

            {/* Undo / Redo Global Buttons */}
            {overview && (
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200">
                <button
                  onClick={handleUndo}
                  disabled={!overview.can_undo}
                  title="Undo last database action"
                  className={`p-1.5 rounded text-xs transition-colors ${
                    overview.can_undo
                      ? 'text-slate-700 hover:bg-white hover:text-brand cursor-pointer shadow-xs'
                      : 'text-slate-400 cursor-not-allowed opacity-50'
                  }`}
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={handleRedo}
                  disabled={!overview.can_redo}
                  title="Redo previous action"
                  className={`p-1.5 rounded text-xs transition-colors ${
                    overview.can_redo
                      ? 'text-slate-700 hover:bg-white hover:text-brand cursor-pointer shadow-xs'
                      : 'text-slate-400 cursor-not-allowed opacity-50'
                  }`}
                >
                  <RotateCw className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Action CTA */}
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 bg-slate-900 hover:bg-brand text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shadow-xs"
            >
              <span>Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Mobile Navigation Row */}
        <div className="lg:hidden flex items-center gap-1 overflow-x-auto py-2 border-t border-slate-100 text-xs no-scrollbar">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`whitespace-nowrap px-2.5 py-1 rounded-md text-[0.75rem] font-medium transition-colors ${
                  isActive ? 'bg-brand text-white' : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </header>
  );
}
