'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from './sidebar';
import Header from './header';

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isOpenMobile, setIsOpenMobile] = useState(false);

  // Load saved sidebar state on desktop
  useEffect(() => {
    const saved = localStorage.getItem('ib-sidebar-collapsed');
    if (saved) {
      setIsCollapsed(saved === 'true');
    }
  }, []);

  const handleToggleSidebar = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem('ib-sidebar-collapsed', String(next));
      return next;
    });
  };

  return (
    <div className="flex min-h-screen bg-background text-foreground transition-colors duration-200">
      {/* Sidebar - Desktop and Mobile Drawer wrapper */}
      <Sidebar
        isCollapsed={isCollapsed}
        isOpenMobile={isOpenMobile}
        onCloseMobile={() => setIsOpenMobile(false)}
      />

      {/* Main Container */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header navbar */}
        <Header
          onToggleSidebar={handleToggleSidebar}
          onOpenMobile={() => setIsOpenMobile(true)}
        />

        {/* Dynamic Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
