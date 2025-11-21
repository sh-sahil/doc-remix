"use client";

import React, { useState } from 'react';
import { DropZone } from '@/components/DropZone';
import { Sidebar } from '@/components/Sidebar';
import { DocumentPreview } from '@/components/DocumentPreview';
import { api } from '@/lib/api';
import { Loader2, Download, Wand2, RefreshCw, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Home() {
  const [docId, setDocId] = useState<string | null>(null);
  const [html, setHtml] = useState<string>("");
  const [structure, setStructure] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [kbFiles, setKbFiles] = useState<string[]>([]);
  const [isRewriting, setIsRewriting] = useState(false);
  const [customPrompt, setCustomPrompt] = useState("");

  const handleDocUpload = async (files: File[]) => {
    if (files.length === 0) return;
    try {
      const res = await api.uploadDocx(files[0]);
      setDocId(res.id);
      setHtml(res.html);
      setStructure(res.structure);
    } catch (e) {
      console.error("Upload failed", e);
      alert("Upload failed");
    }
  };

  const handleKbUpload = async (files: File[]) => {
    if (files.length === 0) return;
    try {
      const res = await api.uploadKb(files);
      setKbFiles(prev => [...prev, ...res.files]);
    } catch (e) {
      console.error("KB Upload failed", e);
    }
  };

  const handleSelect = (id: string, multi: boolean) => {
    // Always toggle for multi-select feel requested by user
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const handleRewrite = async () => {
    if (!docId || selectedIds.length === 0) return;
    setIsRewriting(true);
    try {
      const res = await api.rewriteSection(docId, selectedIds, customPrompt);
      
      // Update HTML locally
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      Object.entries(res.rewrites).forEach(([id, text]) => {
        const el = doc.getElementById(id);
        if (el) {
             // Basic markdown to HTML conversion for display
            el.innerHTML = (text as string)
                .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
                .replace(/\*(.*?)\*/g, '<i>$1</i>');
            
            // If empty (cleared section), maybe hide it or keep it empty
            if (!text) el.innerHTML = "";
        }
      });

      setHtml(doc.body.innerHTML);
      
      // Update structure text
      setStructure(prev => prev.map(s => res.rewrites[s.id] !== undefined ? { ...s, text: res.rewrites[s.id] } : s));
      
      // Deselect after success as requested
      setSelectedIds([]);

    } catch (e) {
      console.error("Rewrite failed", e);
      alert("Rewrite failed. Check console for details.");
    } finally {
      setIsRewriting(false);
    }
  };

  const handleDownload = () => {
    if (!docId) return;
    window.open(api.getDownloadUrl(docId), '_blank');
  };

  return (
    <div className="flex h-screen bg-white text-gray-900 font-sans overflow-hidden">
      {/* Left Sidebar: Controls & Outline */}
      <div className="w-80 flex flex-col border-r bg-gray-50">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <span className="bg-blue-600 text-white p-1 rounded">DR</span> DocRemix
          </h1>
        </div>

        {!docId ? (
           <div className="p-4">
             <DropZone onDrop={handleDocUpload} type="docx" />
           </div>
        ) : (
          <>
            <div className="flex-1 overflow-hidden">
              <Sidebar sections={structure} selectedIds={selectedIds} onSelect={handleSelect} />
            </div>
            
            <div className="p-4 border-t bg-white space-y-4">
              <div>
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Knowledge Base</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {kbFiles.map(f => (
                    <span key={f} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded flex items-center gap-1">
                      <FileText className="w-3 h-3" /> {f}
                    </span>
                  ))}
                </div>
                <DropZone onDrop={handleKbUpload} type="kb" className="p-2 text-xs" />
              </div>

              <div>
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Rewrite Controls</h3>
                <textarea 
                  className="w-full text-sm p-2 border rounded mb-2 h-20 resize-none focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Custom instructions (e.g., 'Make it more formal')"
                  value={customPrompt}
                  onChange={e => setCustomPrompt(e.target.value)}
                />
                <button
                  onClick={handleRewrite}
                  disabled={selectedIds.length === 0 || isRewriting}
                  className={cn(
                    "w-full flex items-center justify-center gap-2 py-2 rounded-md font-medium transition-all",
                    selectedIds.length > 0 
                      ? "bg-blue-600 text-white hover:bg-blue-700 shadow-md" 
                      : "bg-gray-200 text-gray-400 cursor-not-allowed"
                  )}
                >
                  {isRewriting ? <Loader2 className="animate-spin w-4 h-4" /> : <Wand2 className="w-4 h-4" />}
                  {isRewriting ? "Rewriting..." : "Rewrite Selected"}
                </button>
              </div>

              <button
                onClick={handleDownload}
                className="w-full flex items-center justify-center gap-2 py-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm font-medium"
              >
                <Download className="w-4 h-4" /> Download .docx
              </button>
            </div>
          </>
        )}
      </div>

      {/* Main Area: Preview */}
      <div className="flex-1 bg-gray-100 relative">
        {!docId ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <div className="w-64 h-64 bg-gray-200 rounded-full flex items-center justify-center mb-4">
              <FileText className="w-32 h-32 opacity-20" />
            </div>
            <p className="text-lg">Upload a document to start remixing</p>
          </div>
        ) : (
          <DocumentPreview html={html} selectedIds={selectedIds} onSelect={handleSelect} />
        )}
      </div>
    </div>
  );
}
