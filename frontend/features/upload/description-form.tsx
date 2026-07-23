import React from 'react';

interface DescriptionFormProps {
  description: string;
  onChangeDescription: (value: string) => void;
}

export default function DescriptionForm({
  description,
  onChangeDescription,
}: DescriptionFormProps) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Batch Description (Optional)
      </label>
      <textarea
        value={description}
        onChange={(e) => onChangeDescription(e.target.value)}
        placeholder="Provide contextual details about this document batch to aid cataloging..."
        rows={4}
        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none transition-all focus:border-primary placeholder:text-muted-foreground"
      />
    </div>
  );
}
