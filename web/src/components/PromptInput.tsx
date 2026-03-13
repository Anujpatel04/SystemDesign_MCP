import { useState } from 'react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function PromptInput({ onSubmit, disabled, placeholder }: PromptInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSubmit(trimmed);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row gap-3">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder ?? 'e.g. Design a scalable ride-sharing system like Uber'}
          disabled={disabled}
          rows={3}
          className="flex-1 w-full px-4 py-3 rounded-xl border border-slate-600 bg-slate-800/80 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500 resize-none font-sans text-base"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="px-6 py-3 rounded-xl bg-sky-600 hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-colors shrink-0"
        >
          {disabled ? 'Generating…' : 'Generate Design'}
        </button>
      </div>
    </form>
  );
}
