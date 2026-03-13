import { useState } from 'react';
import { generateDesign } from './api/client';
import type { DesignResponse } from './types';
import { PromptInput } from './components/PromptInput';
import { ResultView } from './components/ResultView';

function exportToMarkdown(data: DesignResponse) {
  const lines = [
    '# System Design Output',
    '',
    '## System Overview',
    data.system_overview || '',
    '',
    '## Functional Requirements',
    ...(data.functional_requirements || []).map((r) => `- ${r}`),
    '',
    '## Non-Functional Requirements',
    ...(data.non_functional_requirements || []).map((r) => `- ${r}`),
    '',
    '## Architecture Components',
    ...(data.architecture_components || []).map((c) => `- **${c.name}**: ${c.description}`),
    '',
    '## Infrastructure',
    ...(data.infrastructure_stack || []).map((i) => `- **${i.name}** (${i.category}): ${i.description}`),
    '',
    '## API Endpoints',
    ...(data.api_design || []).map((e) => `- \`${e.method} ${e.path}\`: ${e.description}`),
    '',
    '## Architecture Diagram',
    '```mermaid',
    data.architecture_diagram_mermaid || '',
    '```',
    '',
    '## Workflow Diagram',
    '```mermaid',
    data.workflow_diagram_mermaid || '',
    '```',
    '',
    '## Scaling Strategy',
    ...(data.scaling_strategy || []).map((s) => `- ${s}`),
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'system_design.md';
  a.click();
  URL.revokeObjectURL(url);
}

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DesignResponse | null>(null);

  const handleSubmit = async (prompt: string) => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await generateDesign(prompt);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-700/80 bg-slate-900/95 backdrop-blur sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-5">
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            System Design MCP
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Generate architecture, APIs, and diagrams from a prompt
          </p>
        </div>
      </header>

      <main className="flex-1 px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <PromptInput
            onSubmit={handleSubmit}
            disabled={loading}
            placeholder="e.g. Design a scalable chat system like WhatsApp"
          />

          {loading && (
            <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-8 text-center">
              <div className="inline-block w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mb-3" />
              <p className="text-slate-400">Generating system design…</p>
              <p className="text-slate-500 text-sm mt-1">This may take a minute.</p>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-4 text-red-400 text-sm">
              {error}
            </div>
          )}

          {result && !loading && (
            <ResultView data={result} onExportMarkdown={() => exportToMarkdown(result)} />
          )}
        </div>
      </main>

      <footer className="border-t border-slate-700/80 py-4 text-center text-slate-500 text-xs">
        System Design MCP Agent Platform · FastAPI + React
      </footer>
    </div>
  );
}
