# DocRemix – Smart Word Document Rewriter (with Selective Editing)

**DocRemix** is a beautiful, local-first web app that lets you:

-   Upload any `.docx` file (reports, proposals, resumes, etc.)
-   See a pixel-perfect live preview (just like real Word)
-   Click to select any paragraph, heading, or list item (multi-select with Ctrl/Cmd)
-   Upload your own Markdown knowledge base (your project notes, tone guide, content library)
-   Rewrite only the selected parts using Gemini (or any LLM) — everything else stays 100% untouched
-   Download the final file as a perfect `.docx` with all original formatting preserved

Perfect for reusing old Word templates made by someone else while replacing the content with your own project details.

## Features

-   Live Word-like preview (fonts, spacing, headings, bullets – everything looks right)
-   Click-to-select sections (sidebar outline + direct click in preview)
-   Multi-select & bulk rewrite
-   Uses your Markdown files as a knowledge base/context
-   Preserves 100% of original formatting (bold, italic, indentation, tables\*, colors, etc.)
-   Undo/redo coming soon
-   Works completely offline/local (no data leaves your machine)
-   Dark mode ready

\* Tables are visible but not yet editable in this MVP – coming in v2.

## Quick Start (under 2 minutes)

### 1. Prerequisites

-   Python 3.9+
-   Node.js 18+ (or 20+)
-   A free Gemini API key → <https://aistudio.google.com/app/apikey>

### 2. Clone & Setup

```bash
git clone https://github.com/yourusername/docremix.git
cd docremix

# Backend
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_actual_key_here" > .env

# Test backend
uvicorn main:app --reload
# → should say "DocRemix API is running" at http://localhost:8000
```

```bash
# In another terminal → Frontend
cd ../frontend
npm install
npm run dev
# → opens http://localhost:3000
```

### 3. Use It!

1.  Drag & drop any `.docx` file.
2.  Drag your Markdown knowledge base files (multiple allowed).
3.  Click any section (or Ctrl+click multiple).
4.  (Optional) Add custom instructions like “Make it sound more technical” or “Use first-person.”
5.  Click “Rewrite Selected.”
6.  Click “Download .docx” when happy.

## Sample Files (included)

Run this to generate a test document:

```bash
cd samples
python create_sample.py
```

Then upload:
-   `sample.docx` → the legacy template
-   `knowledge.md` → your new project content

Try selecting “Current Issues” and “Proposed Solution” → watch them transform instantly!

## Folder Structure

```
docremix/
├── backend/              → FastAPI + python-docx + Gemini
├── frontend/             → Next.js 14 + Tailwind + beautiful UI
├── uploads/              → auto-created (your docs live here temporarily)
├── knowledge_base/       → auto-created (your .md files)
└── samples/              → example docx + markdown
```

## Tech Stack

**Backend**
-   FastAPI + Uvicorn
-   `python-docx` (perfect formatting preservation)
-   Google Gemini API (`gemini-2.5-flash-lite` or `pro`)

**Frontend**
-   Next.js 14 (App Router)
-   React 19 + TypeScript
-   Tailwind CSS + shadcn-style components
-   `react-dropzone`, `lucide-react`, `framer-motion`

## Roadmap / What’s Coming Next

-   [ ] Full table editing support
-   [ ] Undo/Redo history
-   [ ] Compare mode (side-by-side before/after)
-   [ ] Save projects & reload later
-   [ ] Support for images, headers/footers, page breaks
-   [ ] One-click “Rewrite Entire Document”
-   [ ] Local LLM option (Ollama/Llama.cpp)

## Contributing

Pull requests are welcome! Especially if you improve table handling or the preview fidelity.

## License

MIT © 2025 – Feel free to use, modify, and ship.

---

**Made because I was tired of copy-pasting from perfect Word templates and losing all the formatting.**
<br>
Now I just select → rewrite → download. Done.

Enjoy remixing


