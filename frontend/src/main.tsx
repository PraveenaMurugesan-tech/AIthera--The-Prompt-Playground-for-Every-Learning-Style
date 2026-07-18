import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
      <Toaster 
        position="top-right" 
        toastOptions={{
          className: 'dark:bg-gray-800 dark:text-white',
        }}
      />
    </ErrorBoundary>
  </StrictMode>,
)
