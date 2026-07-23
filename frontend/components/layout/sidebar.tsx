'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { usePersonaStore } from '@/features/persona/persona-context';
import {
  LayoutDashboard,
  Upload,
  Cpu,
  MessageSquare,
  Network,
  ShieldCheck,
  History,
  Settings,
  Eye,
  X
} from 'lucide-react';

interface SidebarProps {
  isCollapsed: boolean;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

const ICON_MAP: Record<string, React.ComponentType<any>> = {
  LayoutDashboard,
  UploadCloud: Upload,
  Cpu,
  MessageSquare,
  Eye,
  ShieldCheck,
  History,
  Settings,
};

export default function Sidebar({ isCollapsed, isOpenMobile, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();
  const { workspaceManifest } = usePersonaStore();

  // Dynamically resolve navigation links based on compiled Workspace Manifest
  const navItems = workspaceManifest
    ? [
        ...workspaceManifest.sidebar.map((item) => ({
          href: item.path,
          label: item.label,
          icon: ICON_MAP[item.icon] || MessageSquare,
        })),
        { href: '/settings', label: 'Settings', icon: Settings },
      ]
    : [
        { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/settings', label: 'Settings', icon: Settings },
      ];

  const sidebarContent = (
    <div className="flex h-full flex-col bg-card border-r border-border text-foreground transition-all duration-200">
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-xl">⚙️</span>
          {(!isCollapsed || isOpenMobile) && (
            <span className="font-bold tracking-tight text-lg text-primary">
              Sangrahalayamu
            </span>
          )}
        </div>
        {isOpenMobile && (
          <button
            onClick={onCloseMobile}
            className="rounded p-1.5 hover:bg-secondary text-muted-foreground"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Dynamic Nav List */}
      <nav className="flex-1 space-y-1 p-3 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={isOpenMobile ? onCloseMobile : undefined}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-primary text-primary-foreground shadow-sm animate-in fade-in duration-100'
                  : 'hover:bg-secondary text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {(!isCollapsed || isOpenMobile) && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside
        className={`hidden md:block shrink-0 h-screen sticky top-0 transition-all duration-200 ${
          isCollapsed ? 'w-16' : 'w-64'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Overlay Navigation Menu (Drawer) */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          {/* Overlay background */}
          <div
            className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
          />
          {/* Sidebar Drawer container */}
          <div className="relative flex w-64 max-w-xs flex-col animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
