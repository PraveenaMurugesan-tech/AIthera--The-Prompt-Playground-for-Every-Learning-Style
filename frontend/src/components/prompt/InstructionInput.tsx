import React from 'react';

interface InstructionInputProps {
  value: string;
  onChange: (value: string) => void;
}

export const InstructionInput: React.FC<InstructionInputProps> = ({ value, onChange }) => {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="instructions" className="text-sm font-medium text-slate-700 dark:text-slate-200">
        Additional Instructions <span className="text-slate-400 font-normal">(Optional)</span>
      </label>
      <textarea
        id="instructions"
        rows={4}
        className="block w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white transition-shadow shadow-sm resize-y"
        placeholder="Any specific focus areas, tone, or constraints..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
};
