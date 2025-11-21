"use client";

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone'; // Note: need to install react-dropzone
import { Upload, FileText, Folder } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DropZoneProps {
  onDrop: (files: File[]) => void;
  type: 'docx' | 'kb';
  className?: string;
}

export function DropZone({ onDrop, type, className }: DropZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: type === 'docx' 
      ? { 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] }
      : { 'text/markdown': ['.md'], 'text/plain': ['.txt'] },
    multiple: type === 'kb'
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200",
        isDragActive ? "border-blue-500 bg-blue-50 scale-[1.02]" : "border-gray-300 hover:border-gray-400 hover:bg-gray-50",
        className
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3 text-gray-500">
        {type === 'docx' ? (
          <FileText className="w-10 h-10 text-blue-500" />
        ) : (
          <Folder className="w-10 h-10 text-green-500" />
        )}
        <div>
          <p className="font-medium text-gray-900">
            {isDragActive ? "Drop it here!" : type === 'docx' ? "Drop your Word file" : "Drop Knowledge Base files"}
          </p>
          <p className="text-sm mt-1">
            {type === 'docx' ? "Only .docx supported" : "Markdown (.md) or Text (.txt)"}
          </p>
        </div>
      </div>
    </div>
  );
}
