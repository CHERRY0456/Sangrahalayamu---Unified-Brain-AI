export type UserRole =
  | 'Field Technician'
  | 'Maintenance Engineer'
  | 'Project Manager'
  | 'Regulatory & Compliance Manager'
  | 'Director / Executive';

export interface EmployeeProfile {
  employeeId: string;
  name: string;
  email: string;
  department: string;
  designation: string;
  avatarUrl?: string;
}

export interface PersonaConfig {
  role: UserRole;
  dashboardWidgets: string[];
  quickActions: { label: string; actionUrl: string; isPlaceholder?: boolean }[];
  chatStarters: string[];
  transparencyFocus: string;
  sidebarNav: { label: string; path: string; icon: string }[];
  defaultLandingWorkspace: string;
  defaultRetrievalMode: 'automatic' | 'manual';
  themeAccent?: string;
  permissions: string[];
}

export interface WorkspaceManifest {
  sidebar: { label: string; path: string; icon: string }[];
  dashboard: string[];
  chatSuggestions: string[];
  transparencyFocus: string;
  quickActions: { label: string; actionUrl: string; isPlaceholder?: boolean }[];
  defaultRoute: string;
}
