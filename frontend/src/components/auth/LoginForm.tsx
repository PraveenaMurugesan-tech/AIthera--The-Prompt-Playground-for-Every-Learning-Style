
export const LoginForm = () => {
  return (
    <div className="flex justify-center items-center h-screen bg-slate-50 dark:bg-slate-900">
      <div className="p-8 bg-white dark:bg-slate-800 rounded-xl shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-slate-900 dark:text-white">Login</h2>
        <p className="text-slate-600 dark:text-slate-400 mb-6">This is a placeholder for the login form.</p>
        <button className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Login
        </button>
      </div>
    </div>
  );
};
