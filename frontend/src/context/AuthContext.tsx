import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'

type AuthContextValue = {
  user: { name: string } | null
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<{ name: string } | null>({ name: 'Guest' })

  const value = useMemo(
    () => ({
      user,
      login: () => setUser({ name: 'Guest' }),
      logout: () => setUser(null),
    }),
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}
