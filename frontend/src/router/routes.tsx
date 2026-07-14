import { Navigate } from 'react-router-dom'
import { MainLayout } from '../components/layout/MainLayout'
import { LoginPage } from '../pages/auth/Login'
import { RegisterPage } from '../pages/auth/Register'
import { DashboardPage } from '../pages/dashboard/Dashboard'
import { HelpPage } from '../pages/help/Help'
import { NotFoundPage } from '../pages/NotFound'
import { ProfilePage } from '../pages/profile/Profile'
import { SettingsPage } from '../pages/settings/Settings'

export const appRoutes = [
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'profile',
        element: <ProfilePage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: 'help',
        element: <HelpPage />,
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]
