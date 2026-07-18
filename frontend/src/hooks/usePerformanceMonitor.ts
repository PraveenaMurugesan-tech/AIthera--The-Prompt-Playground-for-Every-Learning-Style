import { useEffect } from 'react';

export function usePerformanceMonitor(componentName: string) {
  useEffect(() => {
    if (import.meta.env.DEV && import.meta.env.VITE_ENABLE_PERF_MONITOR !== 'false') {
      const startTime = performance.now();

      return () => {
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        // We use console.info here to keep performance metrics separate from standard logs
        console.info(`[Perf] ${componentName} mounted for ${duration}ms`);
      };
    }
  }, [componentName]);
}
