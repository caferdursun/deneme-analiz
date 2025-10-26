"""
Claude API client for PDF analysis
"""
import anthropic
import base64
from pathlib import Path
from typing import Dict, Any
import json

from app.core.config import settings


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables")

        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5-20250929"  # Claude 4.5 Sonnet - flagship model for PDF analysis

    def analyze_exam_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze exam PDF and extract structured data

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted exam data
        """
        # Read PDF file as base64
        with open(pdf_path, "rb") as f:
            pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Create the analysis prompt
        system_prompt = """You are an expert at analyzing Turkish university entrance exam reports.
Extract all information from the PDF in the exact JSON format specified.
Pay close attention to Turkish characters and numerical data accuracy.
The PDF contains a student's exam results with detailed breakdowns."""

        user_prompt = """Analyze this exam report PDF and extract ALL information in the following JSON structure:

{
  "student": {
    "name": "string",
    "school": "string",
    "grade": "string",
    "class_section": "string"
  },
  "exam": {
    "exam_name": "string",
    "exam_date": "YYYY-MM-DD",
    "booklet_type": "string",
    "exam_number": "integer"
  },
  "overall_result": {
    "total_questions": "integer",
    "total_correct": "integer",
    "total_wrong": "integer",
    "total_blank": "integer",
    "net_score": "float",
    "net_percentage": "float",
    "class_rank": "integer",
    "class_total": "integer",
    "school_rank": "integer",
    "school_total": "integer",
    "class_avg": "float",
    "school_avg": "float"
  },
  "subjects": [
    {
      "subject_name": "string",
      "total_questions": "integer",
      "correct": "integer",
      "wrong": "integer",
      "blank": "integer",
      "net_score": "float",
      "net_percentage": "float",
      "class_rank": "integer",
      "class_avg": "float",
      "school_rank": "integer",
      "school_avg": "float"
    }
  ],
  "learning_outcomes": [
    {
      "subject_name": "string",
      "category": "string",
      "subcategory": "string or null",
      "outcome_description": "string or null",
      "total_questions": "integer",
      "acquired": "integer",
      "lost": "integer",
      "success_rate": "float",
      "student_percentage": "float",
      "class_percentage": "float",
      "school_percentage": "float"
    }
  ],
  "questions": [
    {
      "subject_name": "string",
      "question_number": "integer",
      "correct_answer": "string (A-E)",
      "student_answer": "string (A-E) or null for blank",
      "is_correct": "boolean",
      "is_blank": "boolean"
    }
  ]
}

Important extraction notes:
1. Exam date format from "Tarih" field (DD.MM.YYYY → convert to YYYY-MM-DD)
2. Extract "Şb N" (class average net) and "Ok N" (school average net)
3. For subjects: Matematik, Fizik, Kimya, Biyoloji, Türkçe or "12. SINIF KURS EDEBİYAT YKS"
4. Learning outcomes from "Kazanım Başarı Analizleri" section (pages 2-3)
5. Questions from answer grid - compare "Cevap" (correct) vs "Öğrenci" (student answer)
6. Blank answers shown as "." in student answer column
7. Wrong answers shown in lowercase in answer key
8. Net score formula: Correct - (Wrong / 4)

Return ONLY valid JSON, no additional text."""

        try:
            # Call Claude API with vision
            message = self.client.messages.create(
                model=self.model,
                max_tokens=16000,  # Increased for full exam data (88 questions + learning outcomes)
                temperature=0,  # Deterministic output for data extraction
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                        ],
                    }
                ],
            )

            # Extract text response
            response_text = message.content[0].text

            # Save response for debugging
            import os
            debug_dir = "/tmp/claude_debug"
            os.makedirs(debug_dir, exist_ok=True)
            with open(f"{debug_dir}/last_response.txt", "w", encoding="utf-8") as f:
                f.write(response_text)

            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)
                return extracted_data
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                    extracted_data = json.loads(json_str)
                    return extracted_data
                elif "```" in response_text:
                    # Try generic code block
                    json_start = response_text.find("```") + 3
                    # Skip the language identifier if present
                    first_newline = response_text.find("\n", json_start)
                    if first_newline > json_start:
                        json_start = first_newline + 1
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                    extracted_data = json.loads(json_str)
                    return extracted_data
                else:
                    # Save error details
                    with open(f"{debug_dir}/last_error.txt", "w", encoding="utf-8") as f:
                        f.write(f"JSON Error: {e}\n\n")
                        f.write(f"Response length: {len(response_text)} chars\n\n")
                        f.write(f"First 1000 chars:\n{response_text[:1000]}\n\n")
                        f.write(f"Error location (around char {e.pos}):\n{response_text[max(0, e.pos-200):min(len(response_text), e.pos+200)]}\n")
                    raise ValueError(f"Failed to parse JSON response: {e}\n\nSee /tmp/claude_debug/last_error.txt for details")

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test if Claude API is accessible"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}],
            )
            return True
        except Exception:
            return False
