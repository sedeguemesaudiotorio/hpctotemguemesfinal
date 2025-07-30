import { useEffect, useRef } from 'react';

const useAutoRestart = (onRestart, timeoutMs = 30000, isActive = true) => {
  const timeoutRef = useRef(null);

  const resetTimer = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    if (isActive) {
      timeoutRef.current = setTimeout(() => {
        onRestart();
      }, timeoutMs);
    }
  };

  useEffect(() => {
    if (isActive) {
      resetTimer();
    } else {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isActive, timeoutMs, onRestart]);

  // Función para resetear el timer manualmente en actividad del usuario
  const handleUserActivity = () => {
    resetTimer();
  };

  return { handleUserActivity, resetTimer };
};

export default useAutoRestart;