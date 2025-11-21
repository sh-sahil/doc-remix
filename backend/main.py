from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
from typing import List
import json
import uuid

from models import DocumentStructure, RewriteRequest, RewriteResponse
from document_processor import DocxHandler
from llm_service import GeminiService
from dotenv import load_dotenv

load_dotenv()

# In-memory storage for handlers (in production use Redis/DB)
# Map: document_id -> DocxHandler instance
document_handlers = {}

def get_or_create_handler(doc_id: str):
    if doc_id in document_handlers:
        return document_handlers[doc_id]
    
    # Try to load from disk
    # Check for modified version first
    modified_path = f"{UPLOAD_DIR}/modified_{doc_id}.docx"
    if os.path.exists(modified_path):
         try:
            handler = DocxHandler(modified_path)
            handler.extract_structure()
            document_handlers[doc_id] = handler
            return handler
         except Exception as e:
             print(f"Failed to restore modified handler: {e}")

    meta_path = f"{UPLOAD_DIR}/{doc_id}.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                data = json.load(f)
            handler = DocxHandler(data["file_path"])
            # We need to re-extract structure to populate id_map
            # This is expensive but necessary on reload
            handler.extract_structure() 
            document_handlers[doc_id] = handler
            return handler
        except Exception as e:
            print(f"Failed to restore handler: {e}")
            return None
    return None


app = FastAPI(title="DocRemix API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
KB_DIR = "knowledge_base"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(KB_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "DocRemix API is running"}

@app.post("/upload/docx")
async def upload_docx(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    handler = DocxHandler(file_location)
    html_preview = handler.extract_structure()
    
    # Store handler
    doc_id = str(uuid.uuid4())
    document_handlers[doc_id] = handler
    
    # Persist metadata for server restarts
    with open(f"{UPLOAD_DIR}/{doc_id}.json", "w") as f:
        json.dump({"file_path": file_location}, f)
    
    return {
        "filename": file.filename, 
        "status": "uploaded", 
        "id": doc_id,
        "html": html_preview,
        "structure": handler.structure
    }

@app.post("/upload/kb")
async def upload_kb(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_location = f"{KB_DIR}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)
    return {"files": saved_files, "status": "uploaded"}

@app.post("/rewrite")
async def rewrite_section(request: RewriteRequest):
    handler = get_or_create_handler(request.document_id)
    if not handler:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Collect text from all sections
    original_texts = []
    for sec_id in request.section_ids:
        if sec_id in handler.id_map:
            original_texts.append(handler.id_map[sec_id]["obj"].text)
    
    full_original_text = "\n\n".join(original_texts)
    
    # Prepare context files
    context_files = [f"{KB_DIR}/{fname}" for fname in os.listdir(KB_DIR) if fname.endswith(".md")]
    
    # Call Gemini
    try:
        llm = GeminiService()
        new_text = llm.rewrite(full_original_text, context_files, request.custom_instructions)
    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
    
    # Update Document
    # We put the new text in the first section
    first_id = request.section_ids[0]
    handler.update_section(first_id, new_text)
    
    # Clear other sections
    for sec_id in request.section_ids[1:]:
        handler.update_section(sec_id, "") # Clear content
    
    # Save immediately to persist changes
    output_path = f"{UPLOAD_DIR}/modified_{request.document_id}.docx"
    handler.save(output_path)
        
    return {
        "rewrites": {first_id: new_text, **{sid: "" for sid in request.section_ids[1:]}}
    }

@app.get("/download/{document_id}")
async def download_document(document_id: str):
    handler = get_or_create_handler(document_id)
    if not handler:
        raise HTTPException(status_code=404, detail="Document not found")
    
    output_path = f"{UPLOAD_DIR}/modified_{document_id}.docx"
    handler.save(output_path)
    
    from fastapi.responses import FileResponse
    return FileResponse(output_path, filename="remixed_document.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
