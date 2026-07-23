'use client';

import React, { useEffect, useState } from 'react';

export default function WelcomeSection() {
  const [currentDate, setCurrentDate] = useState('');

  useEffect(() => {
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    setCurrentDate(new Date().toLocaleDateString('en-US', options));
  }, []);

  return (
    <div className="flex flex-col gap-1.5">
      <div className="text-xs font-semibold text-primary uppercase tracking-wider">
        {currentDate || 'System Online'}
      </div>
      <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
        Welcome Back, <span className="text-primary font-bold">John Doe</span>
      </h1>
      <p className="max-w-2xl text-sm text-muted-foreground leading-relaxed">
        Sangrahalayamu is your enterprise-grade document intelligence platform. Ingest heterogeneous industrial manuals, schematics, logs, or procedures and query their collective knowledge securely.
      </p>
    </div>
  );
}
