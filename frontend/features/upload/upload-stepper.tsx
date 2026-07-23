import React from 'react';
import { Check } from 'lucide-react';

interface UploadStepperProps {
  currentStep: number;
}

const STEPS = [
  { number: 1, name: 'Ingest Files' },
  { number: 2, name: 'Add Metadata' },
  { number: 3, name: 'Review Details' },
];

export default function UploadStepper({ currentStep }: UploadStepperProps) {
  return (
    <div className="w-full py-4 border-b border-border mb-6">
      <div className="flex items-center justify-between max-w-xl mx-auto">
        {STEPS.map((step, idx) => {
          const isCompleted = currentStep > step.number;
          const isActive = currentStep === step.number;

          return (
            <React.Fragment key={step.number}>
              {/* Step Circle & Name */}
              <div className="flex flex-col items-center gap-1.5 flex-1 relative">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full border text-xs font-bold transition-all duration-200 ${
                    isCompleted
                      ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                      : isActive
                      ? 'border-primary text-primary font-bold shadow-sm'
                      : 'border-border text-muted-foreground bg-secondary/20'
                  }`}
                >
                  {isCompleted ? <Check className="h-4.5 w-4.5" /> : step.number}
                </div>
                <span
                  className={`text-[11px] font-semibold uppercase tracking-wider ${
                    isActive ? 'text-primary' : 'text-muted-foreground'
                  }`}
                >
                  {step.name}
                </span>
              </div>

              {/* Progress Line Divider */}
              {idx < STEPS.length - 1 && (
                <div className="h-0.5 flex-1 bg-border mx-2 -translate-y-3.5">
                  <div
                    className="h-full bg-primary transition-all duration-350"
                    style={{ width: currentStep > step.number ? '100%' : '0%' }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
