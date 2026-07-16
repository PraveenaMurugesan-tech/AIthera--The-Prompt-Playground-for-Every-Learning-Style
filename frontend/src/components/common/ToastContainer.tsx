import { useToast } from '../../context/ToastContext'

export const ToastContainer = () => {
  const { toasts, dismissToast } = useToast()

  if (toasts.length === 0) return null

  return (
    <div className="toast-container-fixed" aria-live="polite">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast-alert-pill ${toast.type} animate-fade-in`}
          role="alert"
        >
          <span className="toast-icon">
            {toast.type === 'success' && '✅'}
            {toast.type === 'error' && '❌'}
            {toast.type === 'info' && 'ℹ️'}
            {toast.type === 'loading' && (
              <span className="toast-spinner-small" aria-hidden="true" />
            )}
          </span>
          <span className="toast-message">{toast.message}</span>
          <button
            type="button"
            className="toast-close"
            onClick={() => dismissToast(toast.id)}
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}
export default ToastContainer
