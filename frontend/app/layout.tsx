import type { Metadata } from 'next';
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
            <div className="flex items-center gap-2 font-sans text-xs flex-wrap justify-center">
              <span className="px-2.5 py-0.5 rounded-full bg-slate-100 font-medium text-slate-600 border border-slate-200">CO1 Stacks &amp; Queues</span>
              <span className="px-2.5 py-0.5 rounded-full bg-slate-100 font-medium text-slate-600 border border-slate-200">CO2 Hash Table</span>
              <span className="px-2.5 py-0.5 rounded-full bg-slate-100 font-medium text-slate-600 border border-slate-200">CO3 BST Index</span>
              <span className="px-2.5 py-0.5 rounded-full bg-slate-100 font-medium text-slate-600 border border-slate-200">CO4 Search &amp; Sort</span>
              <span className="px-2.5 py-0.5 rounded-full bg-slate-100 font-medium text-slate-600 border border-slate-200">CO5 Graph &amp; Critical Path</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}

