import type { DesignResponse } from '../types';
import { MermaidDiagram } from './MermaidDiagram';
import { Section } from './Section';

interface ResultViewProps {
  data: DesignResponse;
  onExportMarkdown: () => void;
}

export function ResultView({ data, onExportMarkdown }: ResultViewProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-2">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-slate-100">System Design Result</h2>
        <button
          type="button"
          onClick={onExportMarkdown}
          className="px-4 py-2 rounded-lg border border-slate-600 hover:border-sky-500 hover:bg-sky-500/10 text-slate-300 text-sm font-medium transition-colors"
        >
          Export Markdown
        </button>
      </div>

      <Section title="System Overview">
        <p className="whitespace-pre-wrap">{data.system_overview || '—'}</p>
      </Section>

      <Section title="Functional Requirements">
        {data.functional_requirements?.length ? (
          <ul className="list-disc list-inside space-y-1">
            {data.functional_requirements.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-500">None listed.</p>
        )}
      </Section>

      <Section title="Non-Functional Requirements">
        {data.non_functional_requirements?.length ? (
          <ul className="list-disc list-inside space-y-1">
            {data.non_functional_requirements.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-500">None listed.</p>
        )}
      </Section>

      <Section title="Architecture Components">
        {data.architecture_components?.length ? (
          <ul className="space-y-4">
            {data.architecture_components.map((c, i) => (
              <li key={i} className="border-l-2 border-slate-600 pl-4">
                <strong className="text-slate-100">{c.name}</strong>
                <p className="mt-1">{c.description}</p>
                {c.responsibilities?.length ? (
                  <ul className="mt-2 list-disc list-inside text-slate-400">
                    {c.responsibilities.map((r, j) => (
                      <li key={j}>{r}</li>
                    ))}
                  </ul>
                ) : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-500">None listed.</p>
        )}
      </Section>

      <Section title="Infrastructure Stack">
        {data.infrastructure_stack?.length ? (
          <ul className="space-y-2">
            {data.infrastructure_stack.map((i, idx) => (
              <li key={idx}>
                <span className="font-medium text-slate-200">{i.name}</span>
                <span className="text-slate-500"> ({i.category})</span>
                <span className="text-slate-400"> — {i.description}</span>
                {i.use_case ? (
                  <span className="block text-slate-500 text-xs mt-0.5">Use: {i.use_case}</span>
                ) : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-500">None listed.</p>
        )}
      </Section>

      <Section title="API Endpoints">
        {data.api_design?.length ? (
          <ul className="space-y-3">
            {data.api_design.map((e, i) => (
              <li key={i} className="font-mono text-sm">
                <span className="text-emerald-400">{e.method}</span>{' '}
                <span className="text-sky-300">{e.path}</span>
                <p className="text-slate-400 font-sans mt-1">{e.description}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-500">None listed.</p>
        )}
      </Section>

      <Section title="Architecture Diagram">
        <MermaidDiagram code={data.architecture_diagram_mermaid} title="Flowchart" />
      </Section>

      <Section title="Workflow Diagram">
        <MermaidDiagram code={data.workflow_diagram_mermaid} title="Sequence" />
      </Section>

      <Section title="Scaling Strategy">
        {data.scaling_strategy?.length ? (
          <ul className="list-disc list-inside space-y-1">
            {data.scaling_strategy.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-500">None listed.</p>
        )}
      </Section>

      {data.load_estimate && (
        <Section title="Load Estimate" defaultOpen={false}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            {data.load_estimate.qps_estimate != null && (
              <div className="rounded-lg bg-slate-800/80 p-3">
                <div className="text-slate-500 text-xs uppercase tracking-wider">QPS</div>
                <div className="text-slate-200 font-mono">{data.load_estimate.qps_estimate}</div>
                {data.load_estimate.qps_note && (
                  <div className="text-slate-500 text-xs mt-1">{data.load_estimate.qps_note}</div>
                )}
              </div>
            )}
            {data.load_estimate.storage_gb_estimate != null && (
              <div className="rounded-lg bg-slate-800/80 p-3">
                <div className="text-slate-500 text-xs uppercase tracking-wider">Storage</div>
                <div className="text-slate-200 font-mono">{data.load_estimate.storage_gb_estimate} GB</div>
                {data.load_estimate.storage_note && (
                  <div className="text-slate-500 text-xs mt-1">{data.load_estimate.storage_note}</div>
                )}
              </div>
            )}
            {data.load_estimate.bandwidth_mbps_estimate != null && (
              <div className="rounded-lg bg-slate-800/80 p-3">
                <div className="text-slate-500 text-xs uppercase tracking-wider">Bandwidth</div>
                <div className="text-slate-200 font-mono">{data.load_estimate.bandwidth_mbps_estimate} Mbps</div>
                {data.load_estimate.bandwidth_note && (
                  <div className="text-slate-500 text-xs mt-1">{data.load_estimate.bandwidth_note}</div>
                )}
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  );
}
