import React, { createContext, useContext, useEffect, useRef, useState } from 'react'

const FullScreenContext = createContext()

export function FullScreenProvider({ children }) {
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [goFullScreen, setGoFullScreen] = useState(null);
  const fsRootRef = useRef(null);

  useEffect(() => {
    const el = fsRootRef.current;
    if (el) {
      const f =
        el?.requestFullscreen ||
        el?.webkitRequestFullscreen ||
        el?.mozRequestFullScreen ||
        el?.msRequestFullscreen;

      if (f) {
        setGoFullScreen(() => () => f.call(el));
      }

      const onChange = () => setIsFullScreen(!!document.fullscreenElement);
      document.addEventListener('fullscreenchange', onChange);
      return () => document.removeEventListener('fullscreenchange', onChange);
    }
  }, [fsRootRef.current]);

  return (
    <FullScreenContext.Provider value={{ isFullScreen, goFullScreen, fsRootRef }}>
      {children}
    </FullScreenContext.Provider>
  )
}

export function useFullScreenContext() { return useContext(FullScreenContext) }
