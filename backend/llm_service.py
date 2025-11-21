import google.generativeai as genai
import os
from typing import List

class GeminiService:
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API Key is missing")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def _count_lines(self, text: str) -> int:
        return len([l for l in text.strip().split('\n') if l.strip()])

    def rewrite(self, original_text: str, context_files: List[str], custom_instructions: str = None) -> str:
        # 1. Read context files
        context_content = ""
        for file_path in context_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    context_content += f"\n--- File: {os.path.basename(file_path)} ---\n"
                    context_content += f.read()
            except Exception as e:
                print(f"Error reading context file {file_path}: {e}")

        # 2. Calculate metrics for enforcement
        original_word_count = self._count_words(original_text)
        original_line_count = self._count_lines(original_text)
        
        # 3. Parse user instructions for explicit length demands
        length_instruction = ""
        if custom_instructions:
            ci_lower = custom_instructions.lower()
            if any(x in ci_lower for x in ["one line", "1 line", "single line"]):
                length_instruction = "OUTPUT MUST BE EXACTLY 1 LINE. NO EXCEPTIONS."
            elif any(x in ci_lower for x in ["two line", "2 line"]):
                length_instruction = "OUTPUT MUST BE EXACTLY 2 LINES. NO EXCEPTIONS."
            elif any(x in ci_lower for x in ["short", "brief", "concise"]):
                length_instruction = f"OUTPUT MUST BE SHORT: MAX {max(1, original_word_count // 2)} WORDS."
            elif any(x in ci_lower for x in ["summary", "summarize"]):
                length_instruction = "OUTPUT MUST BE A BRIEF SUMMARY: 1-3 SENTENCES MAX."

        # 4. Construct the robust prompt
        prompt = f"""
<SYSTEM_RULES>
You are a STRICT text replacement engine for DocRemix. You follow rules EXACTLY.

RULE 1 - OUTPUT LENGTH (HIGHEST PRIORITY):
{length_instruction if length_instruction else f"Match the original text length. Original has {original_word_count} words and {original_line_count} lines. Your output MUST have similar length (±20%)."}

RULE 2 - NO HALLUCINATION (CRITICAL):
- You may ONLY use facts that appear in the CONTEXT or ORIGINAL_TEXT below.
- If the context lacks information for a specific claim, KEEP the original text for that part.
- NEVER invent names, dates, numbers, statistics, or claims not in the provided content.
- When uncertain, preserve the original phrasing.

RULE 3 - STRUCTURE PRESERVATION:
- If original is a single sentence → output a single sentence.
- If original is a bullet list → output a bullet list with SAME number of items.
- If original is a paragraph → output a paragraph.
- If original is a heading → output a heading of same level.
- NEVER add extra paragraphs, sections, or elaboration.

RULE 4 - REPLACEMENT LOGIC:
- Your job: Replace ONLY the content/meaning while keeping structure intact.
- Find the most relevant information in CONTEXT that maps to the original text's purpose.
- If no relevant info exists in CONTEXT, return the ORIGINAL_TEXT unchanged.

RULE 5 - FORMATTING:
- Use **bold** and *italic* only if the original used them.
- NO headers (#), blockquotes (>), or code blocks unless original had them.
- NO bullet points unless original had them.

RULE 6 - OUTPUT FORMAT:
- Return ONLY the rewritten text.
- NO preamble like "Here is the rewritten text:"
- NO explanations or notes.
- NO apologies or caveats.
</SYSTEM_RULES>

<CONTEXT>
{context_content[:15000]}
</CONTEXT>

<USER_INSTRUCTIONS>
{custom_instructions if custom_instructions else "Rewrite naturally while preserving tone and length."}
</USER_INSTRUCTIONS>

<ORIGINAL_TEXT>
{original_text}
</ORIGINAL_TEXT>

<TASK>
Rewrite ORIGINAL_TEXT using facts from CONTEXT. Follow all SYSTEM_RULES strictly.
{f"CRITICAL: {length_instruction}" if length_instruction else ""}
</TASK>

<OUTPUT>
"""

        # 5. Call API with stricter generation config
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,  # Lower = more deterministic
                top_p=0.8,
                top_k=40,
            )
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            result = response.text.strip()
            
            # 6. Post-processing validation
            result = self._post_process(result, original_text, custom_instructions)
            return result
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return original_text

    def _post_process(self, result: str, original: str, instructions: str) -> str:
        """Enforce length constraints as a safety net."""
        if not instructions:
            return result
            
        ci_lower = instructions.lower()
        
        # Force single line if requested
        if any(x in ci_lower for x in ["one line", "1 line", "single line"]):
            lines = [l.strip() for l in result.split('\n') if l.strip()]
            if lines:
                return lines[0]
            return result
        
        # Force two lines if requested
        if any(x in ci_lower for x in ["two line", "2 line"]):
            lines = [l.strip() for l in result.split('\n') if l.strip()]
            return '\n'.join(lines[:2]) if lines else result
        
        # Truncate if way too long vs original
        orig_words = self._count_words(original)
        result_words = self._count_words(result)
        if result_words > orig_words * 2 and orig_words > 0:
            words = result.split()
            return ' '.join(words[:int(orig_words * 1.3)])
        
        return result