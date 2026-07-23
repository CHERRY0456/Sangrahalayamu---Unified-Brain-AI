import type { Metadata } from 'next';
import '@/styles/globals.css';
import { AppProvider } from '@/store/app-context';
import { PersonaProvider } from '@/features/persona/persona-context';
import DeveloperPreviewSwitcher from '@/features/persona/developer-preview-switcher';

export const metadata: Metadata = {
  title: 'Sangrahalayamu | Document Intelligence Platform',
  description: 'AI-Powered Repository and Industrial Document Intelligence Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var mode = localStorage.getItem('ib-mode') || 'dark';
                  var theme = localStorage.getItem('ib-theme') || 'zinc';
                  
                  document.documentElement.setAttribute('data-theme', theme);
                  
                  if (mode === 'dark') {
                    document.documentElement.classList.add('dark');
                  } else {
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen bg-background text-foreground antialiased transition-colors duration-200">
        <AppProvider>
          <PersonaProvider>
            {children}
            <DeveloperPreviewSwitcher />
          </PersonaProvider>
        </AppProvider>
      </body>
    </html>
  );
}
