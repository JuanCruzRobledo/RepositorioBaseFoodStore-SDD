import React from "react";

type State = { hasError: boolean; error: Error | null };

export class ErrorBoundary extends React.Component<React.PropsWithChildren, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error("[ErrorBoundary]", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-red-50 p-8">
          <div className="max-w-md text-center space-y-3">
            <h2 className="text-2xl font-bold text-red-700">Algo salio mal</h2>
            <p className="text-sm text-red-600">{this.state.error?.message}</p>
            <button
              onClick={() => location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded-md text-sm"
            >
              Recargar
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
