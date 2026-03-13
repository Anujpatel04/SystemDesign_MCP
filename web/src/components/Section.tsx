import { ReactNode } from 'react';

interface SectionProps {
  title: string;
  id?: string;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function Section({ title, id, children, defaultOpen = true }: SectionProps) {
  return (
    <section id={id} className="border-b border-slate-700/80 last:border-b-0">
      <details open={defaultOpen} className="group">
        <summary className="list-none cursor-pointer py-4 px-1 font-semibold text-slate-200 text-lg flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0 group-open:bg-emerald-500 transition-colors" />
          {title}
        </summary>
        <div className="pb-6 pl-5 text-slate-300 text-sm leading-relaxed space-y-3">
          {children}
        </div>
      </details>
    </section>
  );
}
