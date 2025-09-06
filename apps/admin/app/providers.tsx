'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { worker } from '@/lib/mocks';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: (failureCount, error: any) => {
              // Don't retry on 401/403 errors
              if (error?.status === 401 || error?.status === 403) {
                return false;
              }
              return failureCount < 3;
            },
          },
        },
      })
  );

  useEffect(() => {
    // Start MSW worker in development
    if (process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_MOCKS === 'true') {
      worker.start({
        onUnhandledRequest: 'bypass',
      });
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
