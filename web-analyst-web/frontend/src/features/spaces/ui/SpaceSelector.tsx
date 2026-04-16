'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useSpaces } from '../application/SpaceContext';
import ConfirmModal from '../../../shared/ui/ConfirmModal';

export default function SpaceSelector() {
  const { state, dispatch, activeSpace } = useSpaces();
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isRenaming, setIsRenaming] = useState(false);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [newName, setNewName] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);

  const open = useCallback(() => {
    setIsOpen(true);
    requestAnimationFrame(() => {
      setIsVisible(true);
      setIsAnimating(true);
    });
  }, []);

  const close = useCallback(() => {
    setIsVisible(false);
    setIsAnimating(true);
  }, []);

  const handleTransitionEnd = () => {
    setIsAnimating(false);
    if (!isVisible) setIsOpen(false);
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        close();
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [close]);

  useEffect(() => {
    if (isRenaming && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [isRenaming]);

  const handleCreateSpace = () => {
    dispatch({ type: 'CREATE_SPACE' });
    close();
  };

  const handleDeleteSpace = (id: string) => {
    setDeleteId(id);
  };

  const confirmDelete = () => {
    if (deleteId) {
      dispatch({ type: 'DELETE_SPACE', payload: deleteId });
      setDeleteId(null);
    }
  };

  const startRename = (id: string, currentName: string) => {
    setRenamingId(id);
    setNewName(currentName);
    setIsRenaming(true);
  };

  const commitRename = () => {
    if (renamingId && newName.trim()) {
      dispatch({ type: 'RENAME_SPACE', payload: { id: renamingId, name: newName.trim() } });
    }
    setIsRenaming(false);
    setRenamingId(null);
    setNewName('');
  };

  const cancelRename = () => {
    setIsRenaming(false);
    setRenamingId(null);
    setNewName('');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => isOpen ? close() : open()}
        className="flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm sm:text-base whitespace-nowrap"
      >
        <span className="font-medium text-gray-700">📁 {activeSpace?.name || 'Select Space'}</span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div
            className={`fixed inset-0 bg-black/20 z-40 sm:hidden transition-opacity duration-200 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
            onClick={close}
          />
          <div
            onTransitionEnd={handleTransitionEnd}
            className={`fixed bottom-0 left-0 right-0 sm:absolute sm:bottom-auto sm:top-full sm:left-0 sm:right-auto mt-0 sm:mt-2 w-full sm:w-80 bg-white border border-gray-200 rounded-t-2xl sm:rounded-lg shadow-lg z-50
              transition-all duration-200 ease-out origin-top
              ${isVisible
                ? 'translate-y-0 sm:translate-y-0 opacity-100 sm:scale-100'
                : 'translate-y-full sm:translate-y-0 opacity-100 sm:opacity-0 sm:scale-95'
              }`}
          >
            <div className="w-12 h-1 bg-gray-300 rounded-full mx-auto mt-2 sm:hidden" />
            <div className="p-2 border-b border-gray-200">
              <button
                onClick={handleCreateSpace}
                className="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                + New Space
              </button>
            </div>

            <div className="max-h-[60vh] sm:max-h-96 overflow-y-auto">
            {state.spaces.map((space, index) => {
              const colors = [
                'bg-blue-50 hover:bg-blue-100',
                'bg-green-50 hover:bg-green-100',
                'bg-purple-50 hover:bg-purple-100',
                'bg-pink-50 hover:bg-pink-100',
                'bg-yellow-50 hover:bg-yellow-100',
                'bg-indigo-50 hover:bg-indigo-100',
              ];
              const colorClass = colors[index % colors.length];
              
              return (
              <div
                key={space.id}
                className={`p-3 border-b border-gray-100 ${
                  space.id === activeSpace?.id ? 'ring-2 ring-blue-500 ring-inset' : ''
                } ${colorClass}`}
              >
                {isRenaming && renamingId === space.id ? (
                  <div className="flex items-center gap-2">
                    <input
                      ref={renameInputRef}
                      type="text"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') commitRename();
                        if (e.key === 'Escape') cancelRename();
                      }}
                      className="flex-1 px-2 py-1 text-sm border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button onClick={commitRename} className="text-green-600 hover:text-green-700">✓</button>
                    <button onClick={cancelRename} className="text-red-600 hover:text-red-700">✕</button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => {
                        dispatch({ type: 'SET_ACTIVE_SPACE', payload: space.id });
                        close();
                      }}
                      className="flex-1 text-left"
                    >
                      <div className="font-medium text-gray-900">{space.name}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(space.updatedAt).toLocaleString()}
                      </div>
                    </button>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => startRename(space.id, space.name)}
                        className="p-1 text-gray-500 hover:text-blue-600 transition-colors"
                        title="Rename"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDeleteSpace(space.id)}
                        className="p-1 text-gray-500 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
            })}
          </div>
        </div>
        </>
      )}
      <ConfirmModal
        open={deleteId !== null}
        title="Delete Space"
        message="Are you sure you want to delete this space? This action cannot be undone."
        confirmLabel="Delete"
        variant="danger"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
