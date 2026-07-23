'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, MessageSquare, Network, Cpu, Eye, FileText, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();

  const features = [
    { title: 'Vector RAG Pipeline', desc: 'Ingest manuals, schematics, and logs. Scan using semantic embeddings.', icon: Cpu },
    { title: 'Explainability Sidebar', desc: 'View vector confidence scoring indices and reasoning timesteps.', icon: Eye },
    { title: 'Interactive Graph', desc: 'Explore physical entities and equipment link schemas visually.', icon: Network },
    { title: 'Audit Trace Loggers', desc: 'Enterprise transaction ledgers equipped with severity triggers.', icon: ShieldCheck },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground animate-in fade-in duration-300">
      
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-border bg-card/75 backdrop-blur-md px-6 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-xl">⚙️</span>
          <span className="font-extrabold text-sm tracking-tight text-primary">Sangrahalayamu</span>
        </div>
        <button
          onClick={() => router.push('/login')}
          className="rounded-lg bg-primary hover:bg-primary/95 text-xs font-bold text-primary-foreground px-4 py-2 transition-all cursor-pointer shadow-sm"
        >
          Go to Workspace
        </button>
      </header>

      {/* Main Hero Section */}
      <section className="py-30 px-6 max-w-5xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 border border-primary/20 px-3 py-1 text-[10px] font-bold text-primary uppercase tracking-wide">
          <ShieldCheck className="h-3.5 w-3.5" />
          Enterprise Document Intelligence
        </div>
        
        <h1 className="text-6xl sm:text-5xl font-black tracking-tight leading-none bg-gradient-to-b from-foreground to-foreground/80 bg-clip-text text-transparent">
          Sangrahalayamu
        </h1>
        <p className="text-sm sm:text-md text-muted-foreground max-w-2xl mx-auto leading-relaxed font-medium">
          Secure, AI-powered industrial repository. Trace safety compliance manuals, OEM blueprint schematics, and downtime maintenance checklists using data-driven transparency dashboards.
        </p>

        <div className="flex justify-center pt-2">
          <button
            onClick={() => router.push('/login')}
            className="inline-flex items-center gap-2 rounded-xl bg-primary hover:bg-primary/95 text-sm font-bold text-primary-foreground px-6 py-3.5 transition-all cursor-pointer shadow-md hover:scale-[1.01]"
          >
            Access Ingestion Workspace
            <ArrowRight className="h-4.5 w-4.5" />
          </button>
        </div>
      </section>

      {/* Product Overview Features */}
      <section className="py-12 bg-secondary/10 border-y border-border/40 px-6">
        <div className="max-w-5xl mx-auto space-y-8">
          <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest text-center">
            System Capabilities
          </h2>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  className="rounded-xl border border-border bg-card p-5 space-y-3 shadow-sm hover:border-primary/20 transition-all"
                >
                  <div className="rounded-lg bg-primary/10 border border-primary/20 p-2.5 text-primary w-fit">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-xs font-bold text-foreground">{feat.title}</h3>
                  <p className="text-[10px] text-muted-foreground leading-relaxed">{feat.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Personas Supported */}
      <section className="py-16 px-6 max-w-5xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-xl font-bold tracking-tight text-foreground">Role-Based Operations</h2>
          <p className="text-xs text-muted-foreground">
            Sangrahalayamu resolves user roles on authentication and tailors clearance scopes.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-5 text-center text-xs">
          {[
            { role: 'Field Technician', desc: 'Safety Checklists & Repairs' },
            { role: 'Maintenance Engineer', desc: 'OEM Manuals & Failures' },
            { role: 'Project Manager', desc: 'Task Timelines & Resource Risks' },
            { role: 'Compliance Officer', desc: 'OSHA Regulations & Audits' },
            { role: 'Executive Board', desc: 'Organization KPIs & Downtimes' },
          ].map((item, idx) => (
            <div key={idx} className="rounded-xl border border-border bg-card/60 p-4 space-y-1.5 shadow-sm">
              <div className="text-md">👤</div>
              <h3 className="font-bold text-foreground leading-normal">{item.role}</h3>
              <p className="text-[9px] text-muted-foreground">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card py-6 text-center text-[10px] text-muted-foreground px-6 flex justify-between items-center max-w-5xl mx-auto">
        <span>© 2026 economic times</span>
        <div className="flex gap-4">
          <span className="hover:underline cursor-pointer">Security Clearance Policies</span>
          <span className="hover:underline cursor-pointer">Platform Guidelines</span>
        </div>
      </footer>

    </div>
  );
}
