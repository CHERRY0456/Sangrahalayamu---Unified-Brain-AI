'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { PERSONA_CONFIGS, PERSONA_PROFILE_TEMPLATES } from './persona-config';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store/app-context';
import { UserRole, EmployeeProfile, PersonaConfig, WorkspaceManifest } from '@/lib/types';
import { eraseCookie, getCookie } from '@/lib/cookies';
import { SESSION_TOKEN_KEY } from '@/lib/constants';
import { authService } from '@/services/auth-service';

export interface AccessRequest {
  id: string;
  employeeName: string;
  employeeId: string;
  documentName: string;
  relevanceScore: number;
  section: string;
  reason: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  timestamp: string;
}

interface PersonaContextType {
  profile: EmployeeProfile | null;
  persona: PersonaConfig | null;
  permissions: string[];
  workspaceManifest: WorkspaceManifest | null;
  isInitializing: boolean;
  initStage: number;
  accessRequests: AccessRequest[];
  isRestoringSession: boolean;
  isDocumentAccessible: (documentName: string) => boolean;
  loginUser: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  switchPersona: (role: UserRole) => void;
  submitAccessRequest: (documentName: string, relevanceScore: number, section: string, reason: string) => void;
  approveAccessRequest: (id: string) => void;
  rejectAccessRequest: (id: string) => void;
}

const PersonaContext = createContext<PersonaContextType | undefined>(undefined);

export function PersonaProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { setRetrievalMode } = useAppStore();
  
  const [profile, setProfile] = useState<EmployeeProfile | null>(null);
  const [persona, setPersona] = useState<PersonaConfig | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [workspaceManifest, setWorkspaceManifest] = useState<WorkspaceManifest | null>(null);
  
  const [isInitializing, setIsInitializing] = useState(false);
  const [isRestoringSession, setIsRestoringSession] = useState(true);
  const [initStage, setInitStage] = useState(0);

  // Access override clearance requests (loaded from backend on mount)
  const [accessRequests, setAccessRequests] = useState<AccessRequest[]>([]);

  // Restore authenticated session from backend on mount using stored JWT
  useEffect(() => {
    const restoreSession = async () => {
      setIsRestoringSession(true);
      try {
        const sessionCookie = getCookie(SESSION_TOKEN_KEY);
        const path = window.location.pathname;

        if (sessionCookie) {
          // Fetch current user profile from backend
          const meData = await authService.getMe();
          if (meData) {
            setProfile(meData.profile);
            setPermissions(meData.permissions);
            setWorkspaceManifest(meData.manifest);

            // Resolve persona config from profile email or sorted permissions
            const emailKey = meData.profile.email.toLowerCase();
            const matchedTemplate = Object.values(PERSONA_PROFILE_TEMPLATES).find(
              t => t.email.toLowerCase() === emailKey
            );
            const resolvedRole = matchedTemplate?.personaRole || Object.keys(PERSONA_CONFIGS).find(role =>
              JSON.stringify((meData.permissions || []).slice().sort()) ===
              JSON.stringify((PERSONA_CONFIGS[role as UserRole]?.permissions || []).slice().sort())
            ) as UserRole | undefined;

            if (resolvedRole && PERSONA_CONFIGS[resolvedRole]) {
              setPersona(PERSONA_CONFIGS[resolvedRole]);
              setRetrievalMode(PERSONA_CONFIGS[resolvedRole].defaultRetrievalMode);
            } else {
              // Fallback for custom/unmatched users (like admin@sangrahalayamu.com)
              setPersona(PERSONA_CONFIGS['Director / Executive']);
              setRetrievalMode(PERSONA_CONFIGS['Director / Executive'].defaultRetrievalMode);
            }
          } else {
            // Token expired and refresh failed — redirect to login
            if (path !== '/' && path !== '/login') router.push('/login');
          }
        } else if (path !== '/' && path !== '/login') {
          router.push('/login');
        }
      } catch (e) {
        console.error('Failed to restore session:', e);
      } finally {
        setIsRestoringSession(false);
      }
    };
    restoreSession();
  }, [router]);

  const loginUser = async (email: string, password: string): Promise<boolean> => {
    let authPayload: any;
    try {
      setIsInitializing(true);
      setInitStage(0);

      // Stage 1: Authenticate
      setInitStage(1);
      authPayload = await authService.login(email, password);

      // Stage 2: Loading profile
      setInitStage(2);
      setProfile(authPayload.profile);
      setPermissions(authPayload.permissions);

      // Stage 3: Configuring workspace
      setInitStage(3);
      setWorkspaceManifest(authPayload.manifest);

      // Stage 4: Load AI preferences — resolve persona config by matching permissions or profile email
      setInitStage(4);
      const emailKey = authPayload.profile.email.toLowerCase();
      const matchedTemplate = Object.values(PERSONA_PROFILE_TEMPLATES).find(
        t => t.email.toLowerCase() === emailKey
      );
      const resolvedRole = matchedTemplate?.personaRole || Object.keys(PERSONA_CONFIGS).find(role =>
        JSON.stringify((authPayload.permissions || []).slice().sort()) ===
        JSON.stringify((PERSONA_CONFIGS[role as UserRole]?.permissions || []).slice().sort())
      ) as UserRole | undefined;

      if (resolvedRole && PERSONA_CONFIGS[resolvedRole]) {
        setPersona(PERSONA_CONFIGS[resolvedRole]);
        setRetrievalMode(PERSONA_CONFIGS[resolvedRole].defaultRetrievalMode);
      } else {
        // Fallback for custom/unmatched users
        setPersona(PERSONA_CONFIGS['Director / Executive']);
        setRetrievalMode(PERSONA_CONFIGS['Director / Executive'].defaultRetrievalMode);
      }

      // Brief pause to let user see stage 4 complete
      await new Promise((resolve) => setTimeout(resolve, 400));

    } catch (e: any) {
      setIsInitializing(false);
      setInitStage(0);
      throw e; // Re-throw so login page can display the error message
    }

    setIsInitializing(false);
    setInitStage(0);
    return true;
  };

  const logout = async () => {
    // Revoke refresh token on backend (best-effort)
    await authService.logout();

    setProfile(null);
    setPersona(null);
    setPermissions([]);
    setWorkspaceManifest(null);
    setAccessRequests([]);

    router.push('/login');
  };

  const switchPersona = (role: UserRole) => {
    // Switch local persona view for demo/development purposes
    const config = PERSONA_CONFIGS[role];
    if (config) {
      setPersona(config);
      setRetrievalMode(config.defaultRetrievalMode);
    }
  };

  const submitAccessRequest = (documentName: string, relevanceScore: number, section: string, reason: string) => {
    const randomDigits = Math.floor(10000 + Math.random() * 90000);
    const newRequest: AccessRequest = {
      id: `REQ-2026-${randomDigits}`,
      employeeName: profile ? profile.name : 'Unknown User',
      employeeId: profile ? profile.employeeId : 'EMP-XXXX',
      documentName,
      relevanceScore,
      section,
      reason,
      status: 'Pending',
      timestamp: 'Just now',
    };
    setAccessRequests((prev) => [newRequest, ...prev]);
  };

  const approveAccessRequest = (id: string) => {
    setAccessRequests((prev) =>
      prev.map((req) => (req.id === id ? { ...req, status: 'Approved' as const } : req))
    );
  };

  const rejectAccessRequest = (id: string) => {
    setAccessRequests((prev) =>
      prev.map((req) => (req.id === id ? { ...req, status: 'Rejected' as const } : req))
    );
  };

  const isDocumentAccessible = (documentName: string): boolean => {
    if (!profile || !persona) return false;
    
    // Director / Executive has access to all files
    if (persona.role === 'Director / Executive') return true;

    // Check if there is an approved override request for this document and this user
    const hasApprovedRequest = accessRequests.some(
      (req) => 
        req.documentName === documentName && 
        req.status === 'Approved' && 
        req.employeeId === profile.employeeId
    );
    if (hasApprovedRequest) return true;

    // Default to true for now since real permissions should be fetched dynamically
    // In a fully dynamic system, the document's metadata from the DB would dictate this.
    return true;
  };

  return (
    <PersonaContext.Provider
      value={{
        profile,
        persona,
        permissions,
        workspaceManifest,
        isInitializing,
        isRestoringSession,
        initStage,
        accessRequests,
        isDocumentAccessible,
        loginUser,
        logout,
        switchPersona,
        submitAccessRequest,
        approveAccessRequest,
        rejectAccessRequest,
      }}
    >
      {children}
    </PersonaContext.Provider>
  );
}

export function usePersonaStore() {
  const context = useContext(PersonaContext);
  if (!context) {
    throw new Error('usePersonaStore must be used within a PersonaProvider');
  }
  return context;
}
