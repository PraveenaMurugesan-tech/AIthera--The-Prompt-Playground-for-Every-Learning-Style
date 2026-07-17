import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { AlertCircle, Mail, Lock, LogIn, Sparkles } from 'lucide-react';
import { isValidEmail } from '../../utils/validation';

export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const { login, loading, error, clearError } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearError();

    if (!isValidEmail(email)) {
      setValidationError('Please enter a valid email address');
      return;
    }

    if (!password.trim()) {
      setValidationError('Password is required');
      return;
    }

    try {
      await login({ email, password });
      // Navigation is now handled by the context (preserving origin route)
    } catch {
      // Error is handled by AuthContext and exposed via the `error` state
    }
  };

  const displayError = validationError || error;

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] dark:bg-slate-950 p-4 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 dark:bg-blue-600/10 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-500/10 dark:bg-indigo-600/10 blur-[120px] rounded-full" />
      
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-2xl shadow-blue-900/5 border border-slate-200/60 dark:border-slate-800 p-8 relative z-10 backdrop-blur-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-blue-50 dark:bg-blue-500/10 rounded-2xl mb-4">
            <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Welcome Back</h2>
          <p className="text-slate-500 dark:text-slate-400">Sign in to continue your learning journey.</p>
        </div>

        {displayError && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl flex items-start gap-3 text-red-600 dark:text-red-400" role="alert" aria-live="assertive">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="flex-1 text-sm font-medium">{displayError}</div>
            <button onClick={() => { clearError(); setValidationError(null); }} className="opacity-70 hover:opacity-100 transition-opacity" aria-label="Dismiss error">×</button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300 ml-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                placeholder="you@example.com"
                required
                aria-required="true"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between ml-1">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
            </div>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                placeholder="••••••••"
                required
                aria-required="true"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed mt-2 shadow-lg shadow-blue-600/20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                Sign In
              </>
            )}
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-slate-500 dark:text-slate-400">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
};
