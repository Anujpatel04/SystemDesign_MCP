import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  flowchart: { useMaxWidth: true, htmlLabels: true },
});

interface MermaidDiagramProps {
  code: string;
  className?: string;
  title?: string;
}

export function MermaidDiagram({ code, className = '', title }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!code?.trim()) {
      setSvg(null);
      setError(null);
      return;
    }
    setError(null);
    const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
    mermaid
      .render(id, code.trim())
      .then(({ svg: result }) => {
        setSvg(result);
      })
      .catch((err) => {
        setError(err.message || 'Failed to render diagram');
        setSvg(null);
      });
  }, [code]);

  if (!code?.trim()) {
    return (
      <div className={`rounded-lg border border-slate-700 bg-slate-800/50 p-6 text-slate-400 ${className}`}>
        No diagram generated.
      </div>
    );
  }

  if (error) {
    return (
      <div className={`rounded-lg border border-amber-900/50 bg-amber-950/20 p-4 ${className}`}>
        <p className="text-amber-400 text-sm mb-2">Diagram could not be rendered</p>
        <pre className="text-slate-400 text-xs overflow-auto max-h-48 font-mono whitespace-pre-wrap">{code}</pre>
      </div>
    );
  }

  return (
    <div className={className}>
      {title && (
        <h4 className="text-sm font-semibold text-slate-300 mb-2">{title}</h4>
      )}
      <div
        className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 overflow-auto flex items-center justify-center min-h-[200px]"
        ref={containerRef}
        dangerouslySetInnerHTML={svg ? { __html: svg } : undefined}
      />
    </div>
  );
}
