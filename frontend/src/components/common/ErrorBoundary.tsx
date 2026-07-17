import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mb-6">
            <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Something went wrong
          </h1>
          <p className="text-gray-500 dark:text-gray-400 max-w-md mb-8">
            An unexpected error occurred. We've logged the issue and are looking into it. Please try reloading the application.
          </p>
          <Button onClick={this.handleReload} className="flex items-center space-x-2">
            <RefreshCw className="w-4 h-4" />
            <span>Reload Application</span>
          </Button>
          {import.meta.env.DEV && this.state.error && (
            <div className="mt-8 p-4 bg-red-50 dark:bg-red-900/10 rounded-lg text-left overflow-auto max-w-2xl w-full">
              <pre className="text-sm text-red-600 dark:text-red-400 whitespace-pre-wrap">
                {this.state.error.toString()}
              </pre>
            </div>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
