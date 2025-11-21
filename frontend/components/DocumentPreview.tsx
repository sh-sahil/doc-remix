"use client";

import React, { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface DocumentPreviewProps {
  html: string;
  selectedIds: string[];
  onSelect: (id: string, multi: boolean) => void;
}

export function DocumentPreview({ html, selectedIds, onSelect }: DocumentPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle clicks within the HTML content
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const section = target.closest('.docx-section');
      if (section && section.id) {
        onSelect(section.id, e.ctrlKey || e.metaKey);
      }
    };

    container.addEventListener('click', handleClick);
    return () => container.removeEventListener('click', handleClick);
  }, [onSelect]);

  // Apply selection styles manually to the injected HTML
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Clear previous selections
    container.querySelectorAll('.docx-section').forEach(el => {
      el.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50/50');
    });

    // Apply new selections
    selectedIds.forEach(id => {
      const el = container.querySelector(`[id="${id}"]`);
      if (el) {
        el.classList.add('ring-2', 'ring-blue-500', 'bg-blue-50/50');
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }, [selectedIds]);

  return (
    <div className="h-full overflow-y-auto bg-gray-100 p-8">
      <div 
        ref={containerRef}
        className="max-w-[816px] mx-auto min-h-[1056px] bg-white shadow-lg p-[96px] text-gray-900"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}
