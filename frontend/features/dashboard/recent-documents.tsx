import React from 'react';
import Link from 'next/link';
import { FileText, ArrowRight } from 'lucide-react';

const DOCUMENTS = [
  {
    name: 'P-102A_Schematics_v3.pdf',
    category: 'P&ID Blueprint',
    date: 'July 21, 2026',
    status: 'Processed',
    statusClass: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  },
  {
    name: 'SOP_HighPressure_Boiler.docx',
    category: 'Safety Procedure',
    date: 'July 21, 2026',
    status: 'In Progress',
    statusClass: 'bg-amber-500/10 text-amber-500 border-amber-500/20 animate-pulse',
  },
  {
    name: 'Maintenance_Log_2026_07.xlsx',
    category: 'Log Sheet',
    date: 'July 20, 2026',
    status: 'Processed',
    statusClass: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  },
  {
    name: 'Texas_Refinery_Audit_Report.pdf',
    category: 'Audit File',
    date: 'July 18, 2026',
    status: 'Failed',
    statusClass: 'bg-destructive/10 text-destructive border-destructive/20',
  },
];

export default function RecentDocuments() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Recent Documents Ingested
        </h2>
        <Link
          href="/upload"
          className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-semibold"
        >
          View Ingestion Manager
          <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      <div className="flex-1 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border/80 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
              <th className="pb-2">Document Details</th>
              <th className="pb-2">Category</th>
              <th className="pb-2">Uploaded</th>
              <th className="pb-2 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40 text-xs">
            {DOCUMENTS.map((doc, i) => (
              <tr key={i} className="hover:bg-secondary/25 transition-colors">
                <td className="py-3 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span className="font-semibold text-foreground truncate max-w-[180px] sm:max-w-xs">
                    {doc.name}
                  </span>
                </td>
                <td className="py-3 text-muted-foreground">{doc.category}</td>
                <td className="py-3 text-muted-foreground">{doc.date}</td>
                <td className="py-3 text-right">
                  <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase ${doc.statusClass}`}>
                    {doc.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
