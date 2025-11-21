import google.generativeai as genai
import os
from typing import List

class GeminiService:
    def __init__(self, api_key: str = None):
        # Use env var if not passed
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API Key is missing")
        genai.configure(api_key=key)
        
        # Using the requested model
        self.model = genai.GenerativeModel('models/gemini-2.5-flash-lite')  

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

        # 2. Construct Prompt
        prompt = f"""
You are an expert editor and writer.
Your task is to rewrite the following "Original Text" to fit the style, tone, and information provided in the "Context".

### Context (Knowledge Base):
{context_content[:20000]} 
(Context truncated if too long)

USE THIS CONTEXT TO REWRITE THE ORIGINAL TEXT. DONT RETURN THE ORIGINAL TEXT

### Instructions:
1. Adapt the "Original Text" to align with the context.
2. {custom_instructions if custom_instructions else "Keep the flow natural and professional."}
3. Maintain the original meaning but enhance it with the knowledge base.
4. IMPORTANT: Return the result in Markdown format. Dont Use **bold** for emphasis and *italic*. 
5. Do NOT add markdown headers (#) or blockquotes (>) unless the original text had them. 
6. CRITICAL: Maintain the exact structure and length of the original text. If the original is an abstract, write an abstract. If it is a list, write a list. Do NOT add conversational filler like "Here is the rewrite". Return ONLY the new text.

### Original Text:
{original_text}

### Rewritten Text:

"""
        
        # 3. Call API
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return original_text # Fallback
