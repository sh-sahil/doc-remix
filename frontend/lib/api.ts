import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = {
  uploadDocx: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await axios.post(`${API_URL}/upload/docx`, formData);
    return res.data;
  },
  
  uploadKb: async (files: File[]) => {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    const res = await axios.post(`${API_URL}/upload/kb`, formData);
    return res.data;
  },

  rewriteSection: async (documentId: string, sectionIds: string[], instructions?: string) => {
    const res = await axios.post(`${API_URL}/rewrite`, {
      document_id: documentId,
      section_ids: sectionIds,
      custom_instructions: instructions
    });
    return res.data;
  },

  getDownloadUrl: (documentId: string) => `${API_URL}/download/${documentId}`
};
