import { useState, useEffect, useRef } from 'react';

export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastRan = useRef(0);
  const handler = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const handlerClear = () => {
      if (handler.current) clearTimeout(handler.current);
    }
    
    if (Date.now() - lastRan.current >= limit) {
      setThrottledValue(value);
      lastRan.current = Date.now();
    } else {
      handlerClear();
      handler.current = setTimeout(() => {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }, limit - (Date.now() - lastRan.current));
    }

    return handlerClear;
  }, [value, limit]);

  return throttledValue;
}
