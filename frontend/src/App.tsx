import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { MainLayout } from './components/layout/MainLayout'

import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { ToastProvider } from './context/ToastContext'

import './styles/global.css'

// Fallback loader
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] dark:bg-slate-950">
    <div className="w-10 h-10 border-4 border-blue-600/30 border-t-blue-600 rounded-full animate-spin" />
  </div>
);

// Lazy loaded components
const LoginPage = lazy(() => import('./pages/auth/Login').then(m => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('./pages/auth/Register').then(m => ({ default: m.RegisterPage })))
const DashboardPage = lazy(() => import('./pages/dashboard/Dashboard').then(m => ({ default: m.DashboardPage })))
const WorkspacePage = lazy(() => import('./pages/workspace/Workspace').then(m => ({ default: m.WorkspacePage })))
const HelpPage = lazy(() => import('./pages/help/Help').then(m => ({ default: m.HelpPage })))
const NotFoundPage = lazy(() => import('./pages/NotFound').then(m => ({ default: m.NotFoundPage })))
const ProfilePage = lazy(() => import('./pages/profile/Profile').then(m => ({ default: m.ProfilePage })))
const SettingsPage = lazy(() => import('./pages/settings/Settings').then(m => ({ default: m.SettingsPage })))
const PromptPage = lazy(() => import('./pages/prompt/PromptPage').then(m => ({ default: m.PromptPage })))
const LoadingScreen = lazy(() => import('./components/ai/LoadingScreen').then(m => ({ default: m.LoadingScreen })))
const ResultPage = lazy(() => import('./pages/result/ResultPage').then(m => ({ default: m.ResultPage })))
const ChatPage = lazy(() => import('./pages/chat/ChatPage').then(m => ({ default: m.ChatPage })))
const CouncilPage = lazy(() => import('./pages/council/CouncilPage').then(m => ({ default: m.CouncilPage })))
const HistoryPage = lazy(() => import('./pages/history/HistoryPage').then(m => ({ default: m.HistoryPage })))
const VoicePage = lazy(() => import('./pages/voice/VoicePage').then(m => ({ default: m.VoicePage })))
const UploadPage = lazy(() => import('./pages/upload/UploadPage').then(m => ({ default: m.UploadPage })))
const RecommendationPage = lazy(() => import('./pages/recommendations/RecommendationPage').then(m => ({ default: m.RecommendationPage })))

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            <Suspense fallback={<PageLoader />}>
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
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/workspace" element={<WorkspacePage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/prompt" element={<PromptPage />} />
                  <Route path="/loading" element={<LoadingScreen />} />
                  <Route path="/result" element={<ResultPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/council" element={<CouncilPage />} />
                  <Route path="/history" element={<HistoryPage />} />
                  <Route path="/voice" element={<VoicePage />} />
                  <Route path="/upload" element={<UploadPage />} />
                  <Route path="/recommendations" element={<RecommendationPage />} />
                  <Route path="/help" element={<HelpPage />} />
                </Route>
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Suspense>
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App