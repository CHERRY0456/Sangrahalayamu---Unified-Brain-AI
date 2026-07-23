'use client';

import React from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Menu, Sun, Moon, ChevronRight } from 'lucide-react';
import { useAppStore } from '@/store/app-context';
import { usePersonaStore } from '@/features/persona/persona-context';

interface HeaderProps {
  onToggleSidebar: () => void;
  onOpenMobile: () => void;
}

export default function Header({ onToggleSidebar, onOpenMobile }: HeaderProps) {
  const pathname = usePathname();
  const router = useRouter();
  
  const { mode, setMode } = useAppStore();
  const { profile, logout } = usePersonaStore();
  
  const isDark = mode === 'dark';

  const toggleTheme = () => {
    setMode(isDark ? 'light' : 'dark');
  };

  // Get active user initials
  const getInitials = () => {
    if (!profile) return '';
    return profile.name
      .split(' ')
      .map((n) => n[0] || '')
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Format breadcrumbs dynamically from pathname
  const getBreadcrumbs = () => {
    if (pathname === '/' || pathname === '/dashboard') {
      return ['Sangrahalayamu', 'Dashboard'];
    }
    const segments = pathname.split('/').filter(Boolean);
    const formattedSegments = segments.map((seg) => {
      if (seg === 'processing') return 'AI Processing';
      if (seg === 'chat') return 'AI Chat';
      return seg.charAt(0).toUpperCase() + seg.slice(1);
    });
    return ['Sangrahalayamu', ...formattedSegments];
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-border bg-card/85 backdrop-blur-md px-4 text-foreground shadow-sm transition-all duration-200">
      {/* Left Area: Toggle & Logo & Breadcrumbs */}
      <div className="flex items-center gap-3">
        {/* Toggle Button for Desktop Sidebar */}
        <button
          onClick={onToggleSidebar}
          className="hidden md:flex rounded-lg p-2 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
          aria-label="Toggle Sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Toggle Button for Mobile Drawer */}
        <button
          onClick={onOpenMobile}
          className="flex md:hidden rounded-lg p-2 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
          aria-label="Open Navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Brand Name on Mobile Only */}
        <div className="flex items-center gap-1.5 md:hidden">
          <span className="text-lg">⚙️</span>
          <span className="font-bold text-sm tracking-tight text-primary">Sangrahalayamu</span>
        </div>

        <span className="hidden md:block h-4 w-px bg-border mx-2" />

        {/* Dynamic Breadcrumbs */}
        <nav className="hidden sm:flex items-center gap-1.5 text-sm font-medium">
          {breadcrumbs.map((crumb, idx) => {
            const isLast = idx === breadcrumbs.length - 1;
            return (
              <React.Fragment key={idx}>
                {idx > 0 && <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/60" />}
                <span
                  className={
                    isLast ? 'text-foreground font-semibold' : 'text-muted-foreground'
                  }
                >
                  {crumb}
                </span>
              </React.Fragment>
            );
          })}
        </nav>
      </div>

      {/* Right Area: Theme Toggle & User Profile */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          aria-label="Toggle Theme Mode"
        >
          {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        {/* User profile dropdown on hover */}
        {profile ? (
          <div className="relative group cursor-pointer">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-black shadow-sm hover:opacity-90 transition-all select-none">
              {getInitials()}
            </div>
            
            {/* Mock Dropdown on hover */}
            <div className="absolute right-0 mt-2 w-52 origin-top-right rounded-lg border border-border bg-card p-2 shadow-md hidden group-hover:block animate-in fade-in slide-in-from-top-1 duration-100">
              <div className="px-2 py-1.5 text-[10px] font-bold text-muted-foreground border-b border-border mb-1 space-y-0.5">
                <div className="font-extrabold text-foreground truncate">
                  {profile.name}
                </div>
                <div className="truncate font-mono text-[9px]">
                  {profile.designation}
                </div>
              </div>
              
              <button
                onClick={() => router.push('/settings')}
                className="w-full text-left rounded px-2 py-1.5 text-xs hover:bg-secondary text-foreground cursor-pointer font-semibold transition-colors"
              >
                Profile Settings
              </button>
              <button
                onClick={logout}
                className="w-full text-left rounded px-2 py-1.5 text-xs hover:bg-secondary text-destructive cursor-pointer font-bold transition-colors"
              >
                Log Out
              </button>
            </div>
          </div>
        ) : (
          <div className="h-9 w-9 rounded-full bg-secondary animate-pulse shrink-0" />
        )}
      </div>
    </header>
  );
}
