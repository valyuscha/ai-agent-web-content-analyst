'use client';

import { useRef, useState, useEffect, useCallback } from 'react';
import { TabNavigationProps } from './TabNavigation.types';

export default function TabNavigation({ tabs, activeTab, onTabChange }: TabNavigationProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const checkScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 0);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  }, []);

  useEffect(() => {
    checkScroll();
    window.addEventListener('resize', checkScroll);
    return () => window.removeEventListener('resize', checkScroll);
  }, [checkScroll]);

  const scroll = (direction: 'left' | 'right') => {
    scrollRef.current?.scrollBy({ left: direction === 'left' ? -120 : 120, behavior: 'smooth' });
  };

  return (
    <div className="bg-white rounded-lg shadow mb-4 sm:mb-6 relative">
      {canScrollLeft && (
        <button
          onClick={() => scroll('left')}
          className="absolute left-0 top-0 bottom-0 z-10 w-8 flex items-center justify-center bg-gradient-to-r from-white via-white/90 to-transparent rounded-l-lg"
          aria-label="Scroll tabs left"
        >
          <span className="text-gray-600 text-lg font-bold">‹</span>
        </button>
      )}
      {canScrollRight && (
        <button
          onClick={() => scroll('right')}
          className="absolute right-0 top-0 bottom-0 z-10 w-8 flex items-center justify-center bg-gradient-to-l from-white via-white/90 to-transparent rounded-r-lg"
          aria-label="Scroll tabs right"
        >
          <span className="text-gray-600 text-lg font-bold">›</span>
        </button>
      )}
      <div
        ref={scrollRef}
        onScroll={checkScroll}
        className="flex border-b overflow-x-auto scrollbar-hide"
      >
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-3 py-2 sm:px-6 sm:py-3 text-sm sm:text-base font-medium whitespace-nowrap focus:outline-none ${
              activeTab === tab.id
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
