import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';
import { Button } from './Button';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  isLoading = false,
  onConfirm,
  onCancel,
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isLoading) {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isLoading, onCancel]);

  // Focus trap could be added here, but for simplicity we focus the dialog
  useEffect(() => {
    if (isOpen && dialogRef.current) {
      dialogRef.current.focus();
    }
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={!isLoading ? onCancel : undefined}
            aria-hidden="true"
          />
          <div className="fixed inset-0 flex items-center justify-center p-4 z-50 pointer-events-none">
            <motion.div
              ref={dialogRef}
              tabIndex={-1}
              role="dialog"
              aria-modal="true"
              aria-labelledby="dialog-title"
              aria-describedby="dialog-description"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md p-6 pointer-events-auto outline-none"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-full ${isDestructive ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'}`}>
                    <AlertTriangle className="w-6 h-6" />
                  </div>
                  <h2 id="dialog-title" className="text-xl font-bold text-gray-900 dark:text-white">
                    {title}
                  </h2>
                </div>
                <button
                  onClick={onCancel}
                  disabled={isLoading}
                  className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 p-1"
                  aria-label="Close dialog"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <p id="dialog-description" className="text-gray-600 dark:text-gray-300 mb-6 ml-11">
                {message}
              </p>
              
              <div className="flex justify-end space-x-3 mt-6">
                <Button 
                  variant="outline" 
                  onClick={onCancel} 
                  disabled={isLoading}
                >
                  {cancelLabel}
                </Button>
                <Button 
                  variant={isDestructive ? 'primary' : 'primary'}
                  className={isDestructive ? 'bg-red-600 hover:bg-red-700 text-white border-transparent' : ''}
                  onClick={onConfirm}
                  isLoading={isLoading}
                  disabled={isLoading}
                >
                  {confirmLabel}
                </Button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
