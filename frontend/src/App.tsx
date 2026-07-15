import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { MainLayout } from './components/layout/MainLayout'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { LoginPage } from './pages/auth/Login'
import { RegisterPage } from './pages/auth/Register'
import { DashboardPage } from './pages/dashboard/Dashboard'
import { HelpPage } from './pages/help/Help'
import { NotFoundPage } from './pages/NotFound'
import { ProfilePage } from './pages/profile/Profile'
import { SettingsPage } from './pages/settings/Settings'
import { PromptPage } from './pages/prompt/PromptPage'
import { LoadingScreen } from './components/ai/LoadingScreen'
import { ResultPage } from './pages/result/ResultPage'
import './styles/global.css'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
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
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/prompt" element={<PromptPage />} />
              <Route path="/loading" element={<LoadingScreen />} />
              <Route path="/result" element={<ResultPage />} />
              <Route path="/help" element={<HelpPage />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
