'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface ConfirmModalProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'default';
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'default',
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  const [visible, setVisible] = useState(false);
  const [mounted, setMounted] = useState(false);
  const backdropRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      setMounted(true);
      requestAnimationFrame(() => setVisible(true));
    } else {
      setVisible(false);
    }
  }, [open]);

  const handleTransitionEnd = () => {
    if (!visible) setMounted(false);
  };

  if (!mounted) return null;

  const btnClass = variant === 'danger'
    ? 'bg-red-600 hover:bg-red-700 text-white'
    : 'bg-blue-600 hover:bg-blue-700 text-white';

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div
        ref={backdropRef}
        className={`absolute inset-0 bg-black/40 transition-opacity duration-200 ${visible ? 'opacity-100' : 'opacity-0'}`}
        onClick={onCancel}
      />
      <div
        onTransitionEnd={handleTransitionEnd}
        className={`relative bg-white rounded-xl shadow-2xl p-6 w-full max-w-sm transition-all duration-200 ${
          visible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
        }`}
      >
        <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600 mb-6">{message}</p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${btnClass}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
