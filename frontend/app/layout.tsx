import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';
import { Navbar } from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'TaskForge — Intelligent Task Scheduling & Dependency Management',
  description:
    'Plan smarter. Work in the right order. Powered by custom data structures, graph algorithms, and dynamic programming.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-8 text-xs text-slate-500 text-center">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="font-sans font-extrabold text-slate-900">TaskForge</span>
              <span>&bull;</span>
              <span>Intelligent Task Scheduling &amp; Dependency Management System</span>
            </div>
            <div className="flex items-center gap-3 font-sans text-xs flex-wrap justify-center text-slate-500">
              <Link href="/dashboard" className="hover:text-slate-900 transition-colors">Overview</Link>
              <span>&bull;</span>
              <Link href="/tasks" className="hover:text-slate-900 transition-colors">Tasks</Link>
              <span>&bull;</span>
              <Link href="/scheduling" className="hover:text-slate-900 transition-colors">Schedule</Link>
              <span>&bull;</span>
              <Link href="/dependencies" className="hover:text-slate-900 transition-colors">Dependencies</Link>
              <span>&bull;</span>
              <Link href="/planning" className="hover:text-slate-900 transition-colors">Project Timeline</Link>
              <span>&bull;</span>
              <Link href="/laboratory" className="text-brand font-semibold hover:underline">Technical Labs</Link>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}

