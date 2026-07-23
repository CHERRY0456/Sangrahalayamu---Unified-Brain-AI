import React from 'react';

const CATEGORIES = [
  'Financial Reports',
  'Energy Reports',
  'Legal Documents',
  'Compliance',
  'HR',
  'Other',
];

interface CategorySelectorProps {
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
}

export default function CategorySelector({
  selectedCategory,
  onSelectCategory,
}: CategorySelectorProps) {
  return (
    <div className="space-y-3">
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Select Batch Category
      </label>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => onSelectCategory(cat)}
            className={`rounded-lg border py-3 px-4 text-xs font-semibold tracking-wide transition-all text-center cursor-pointer ${
              selectedCategory === cat
                ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                : 'border-border bg-card hover:bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>
    </div>
  );
}
