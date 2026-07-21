import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
  moduleName?: string;
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
    console.error(`Uncaught error in module ${this.props.moduleName || 'Global'}:`, error, errorInfo);
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center p-6 m-4 bg-error-50 rounded-lg border border-error-100 text-center">
          <h1 className="text-xl font-bold text-error-600 mb-2">Algo salió mal</h1>
          <p className="text-gray-600 mb-4 text-sm">
            Ha ocurrido un error inesperado en el módulo {this.props.moduleName}.
          </p>
          <div className="bg-error-50 p-3 rounded-md mb-6 overflow-auto max-w-full text-left">
            <p className="text-error-800 text-xs font-mono break-all">
              {this.state.error?.message || 'Error desconocido'}
            </p>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
          >  Intentar nuevamente
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
