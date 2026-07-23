'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

// Structured metadata for files (since File object is not serializable)
export interface StagedFileMeta {
  name: string;
  size: number;
  category: string;
}

export type RetrievalMode = 'automatic' | 'manual';
export type ThemePalette = 'zinc' | 'slate' | 'stone' | 'gray';
export type AppearanceMode = 'light' | 'dark';

export interface ProcessingOptionsState {
  summarization: boolean;
  entityExtraction: boolean;
  relationshipDiscovery: boolean;
  timelineExtraction: boolean;
  keyInsights: boolean;
  complianceAnalysis: boolean;
}

interface AppContextType {
  // Upload batch files
  stagedFiles: StagedFileMeta[];
  setStagedFiles: React.Dispatch<React.SetStateAction<StagedFileMeta[]>>;
  
  // Metadata batch details
  category: string;
  setCategory: (value: string) => void;
  description: string;
  setDescription: (value: string) => void;
  
  // Processing options
  retrievalMode: RetrievalMode;
  setRetrievalMode: (value: RetrievalMode) => void;
  processingOptions: ProcessingOptionsState;
  setProcessingOptions: React.Dispatch<React.SetStateAction<ProcessingOptionsState>>;
  
  // Theme & Appearance Sync States
  theme: ThemePalette;
  setTheme: (value: ThemePalette) => void;
  mode: AppearanceMode;
  setMode: (value: AppearanceMode) => void;

  // Reset all staged files & options
  resetBatch: () => void;
}

const defaultProcessingOptions: ProcessingOptionsState = {
  summarization: true,
  entityExtraction: true,
  relationshipDiscovery: false,
  timelineExtraction: false,
  keyInsights: true,
  complianceAnalysis: false,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [stagedFiles, setStagedFiles] = useState<StagedFileMeta[]>([]);
  const [category, setCategoryState] = useState('Other');
  const [description, setDescriptionState] = useState('');
  const [retrievalMode, setRetrievalModeState] = useState<RetrievalMode>('automatic');
  const [processingOptions, setProcessingOptions] = useState<ProcessingOptionsState>(defaultProcessingOptions);
  
  // Theme state definitions
  const [theme, setThemeState] = useState<ThemePalette>('zinc');
  const [mode, setModeState] = useState<AppearanceMode>('dark');

  // Sync with localStorage on mount (persistence layer)
  useEffect(() => {
    try {
      const savedFiles = localStorage.getItem('ib-staged-files');
      const savedCategory = localStorage.getItem('ib-batch-category');
      const savedDesc = localStorage.getItem('ib-batch-desc');
      const savedMode = localStorage.getItem('ib-retrieval-mode');
      const savedOptions = localStorage.getItem('ib-processing-options');
      
      const savedTheme = localStorage.getItem('ib-theme') as ThemePalette;
      const savedAppMode = localStorage.getItem('ib-mode') as AppearanceMode;

      if (savedFiles) setStagedFiles(JSON.parse(savedFiles));
      if (savedCategory) setCategoryState(savedCategory);
      if (savedDesc) setDescriptionState(savedDesc);
      if (savedMode) setRetrievalModeState(savedMode as RetrievalMode);
      if (savedOptions) setProcessingOptions(JSON.parse(savedOptions));
      
      if (savedTheme) setThemeState(savedTheme);
      if (savedAppMode) setModeState(savedAppMode);
    } catch (e) {
      console.error('Failed to load persisted state from localStorage:', e);
    }
  }, []);

  // Set selectors side effects applying details to html elements
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    localStorage.setItem('ib-theme', theme);
  }, [theme]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const root = document.documentElement;
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('ib-mode', mode);
  }, [mode]);

  // Write changes to localStorage (persistence layer)
  const setCategory = (val: string) => {
    setCategoryState(val);
    localStorage.setItem('ib-batch-category', val);
  };

  const setDescription = (val: string) => {
    setDescriptionState(val);
    localStorage.setItem('ib-batch-desc', val);
  };

  const setRetrievalMode = (val: RetrievalMode) => {
    setRetrievalModeState(val);
    localStorage.setItem('ib-retrieval-mode', val);
  };

  const setTheme = (val: ThemePalette) => {
    setThemeState(val);
  };

  const setMode = (val: AppearanceMode) => {
    setModeState(val);
  };

  useEffect(() => {
    if (stagedFiles.length > 0) {
      localStorage.setItem('ib-staged-files', JSON.stringify(stagedFiles));
    } else {
      localStorage.removeItem('ib-staged-files');
    }
  }, [stagedFiles]);

  useEffect(() => {
    localStorage.setItem('ib-processing-options', JSON.stringify(processingOptions));
  }, [processingOptions]);

  const resetBatch = () => {
    setStagedFiles([]);
    setCategoryState('Other');
    setDescriptionState('');
    setRetrievalModeState('automatic');
    setProcessingOptions(defaultProcessingOptions);
    
    // Clear persistence keys
    localStorage.removeItem('ib-staged-files');
    localStorage.removeItem('ib-batch-category');
    localStorage.removeItem('ib-batch-desc');
    localStorage.removeItem('ib-retrieval-mode');
  };

  return (
    <AppContext.Provider
      value={{
        stagedFiles,
        setStagedFiles,
        category,
        setCategory,
        description,
        setDescription,
        retrievalMode,
        setRetrievalMode,
        processingOptions,
        setProcessingOptions,
        theme,
        setTheme,
        mode,
        setMode,
        resetBatch,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppStore() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppStore must be used within an AppProvider');
  }
  return context;
}
