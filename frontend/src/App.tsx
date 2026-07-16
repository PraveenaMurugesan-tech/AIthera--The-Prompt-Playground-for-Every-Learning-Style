import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { MainLayout } from './components/layout/MainLayout'

import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { ToastProvider } from './context/ToastContext'

import { LoginPage } from './pages/auth/Login'
import { RegisterPage } from './pages/auth/Register'

import './styles/global.css'

// Lazy loaded page components
const DashboardPage = lazy(() =>
  import('./pages/dashboard/Dashboard').then((m) => ({
    default: m.DashboardPage,
  }))
)

const WorkspacePage = lazy(() =>
  import('./pages/workspace/Workspace').then((m) => ({
    default: m.WorkspacePage,
  }))
)

const ProfilePage = lazy(() =>
  import('./pages/profile/Profile').then((m) => ({
    default: m.ProfilePage,
  }))
)

const SettingsPage = lazy(() =>
  import('./pages/settings/Settings').then((m) => ({
    default: m.SettingsPage,
  }))
)

const HelpPage = lazy(() =>
  import('./pages/help/Help').then((m) => ({
    default: m.HelpPage,
  }))
)

const NotFoundPage = lazy(() =>
  import('./pages/NotFound').then((m) => ({
    default: m.NotFoundPage,
  }))
)

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              <Route
                element={
                  <ProtectedRoute>
                    <MainLayout />
                  </ProtectedRoute>
                }
              >
                <Route
                  element={
                    <Suspense
                      fallback={
                        <div
                          className="route-loading-shimmer"
                          role="status"
                          aria-label="Loading page"
                        >
                          <div className="shimmer-circle" />
                          <div className="shimmer-line" />
                          <div className="shimmer-line short" />
                        </div>
                      }
                    >
                      <Outlet />
                    </Suspense>
                  }
                >
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/workspace" element={<WorkspacePage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/help" element={<HelpPage />} />
                </Route>
              </Route>

              <Route
                path="*"
                element={
                  <Suspense
                    fallback={<div className="loading-fallback">Loading...</div>}
                  >
                    <NotFoundPage />
                  </Suspense>
                }
              />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App