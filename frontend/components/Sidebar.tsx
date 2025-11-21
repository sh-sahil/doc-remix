"use client";

import React from 'react';
import { cn } from '@/lib/utils';
import { FileText, Hash, Table as TableIcon } from 'lucide-react';

interface Section {
  id: string;
  type: string;
  text: string;
  style: string;
}

interface SidebarProps {
  sections: Section[];
  selectedIds: string[];
  onSelect: (id: string, multi: boolean) => void;
}

export function Sidebar({ sections, selectedIds, onSelect }: SidebarProps) {
  return (
    <div className="h-full overflow-y-auto p-4 border-r bg-gray-50/50">
      <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Document Outline</h2>
      <div className="space-y-1">
        {sections.map((section) => {
          const isSelected = selectedIds.includes(section.id);
          const isHeading = section.style.toLowerCase().includes('heading');
          
          return (
            <div
              key={section.id}
              onClick={(e) => onSelect(section.id, e.ctrlKey || e.metaKey)}
              className={cn(
                "group flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer text-sm transition-colors",
                isSelected ? "bg-blue-100 text-blue-700" : "hover:bg-gray-100 text-gray-600",
                isHeading && "font-medium text-gray-900"
              )}
            >
              {section.type === 'table' ? (
                <TableIcon className="w-4 h-4 opacity-50" />
              ) : isHeading ? (
                <Hash className="w-4 h-4 opacity-50" />
              ) : (
                <FileText className="w-4 h-4 opacity-50" />
              )}
              <span className="truncate">
                {section.text.slice(0, 40) || "[Empty Section]"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
