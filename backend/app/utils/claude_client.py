"""
Claude API client for PDF analysis
"""
import anthropic
import base64
from pathlib import Path
from typing import Dict, Any
import json

from app.core.config import settings
from app.utils.subject_normalizer import normalize_subjects_in_data


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

        user_prompt = """Extract exam data in compact JSON format:

{
  "student": {"name": "", "school": "", "grade": "", "class_section": ""},
  "exam": {"exam_name": "", "exam_date": "YYYY-MM-DD", "booklet_type": "", "exam_number": 0},
  "overall_result": {"total_questions": 0, "total_correct": 0, "total_wrong": 0, "total_blank": 0, "net_score": 0.0, "net_percentage": 0.0, "class_rank": 0, "class_total": 0, "school_rank": 0, "school_total": 0, "class_avg": 0.0, "school_avg": 0.0},
  "subjects": [{"subject_name": "", "total_questions": 0, "correct": 0, "wrong": 0, "blank": 0, "net_score": 0.0, "net_percentage": 0.0, "class_rank": 0, "class_avg": 0.0, "school_rank": 0, "school_avg": 0.0}],
  "learning_outcomes": [{"subject_name": "", "category": "", "subcategory": null, "outcome_description": null, "total_questions": 0, "acquired": 0, "lost": 0, "success_rate": 0.0, "student_percentage": 0.0, "class_percentage": 0.0, "school_percentage": 0.0}],
  "questions": [{"subject_name": "", "question_number": 0, "correct_answer": "", "student_answer": null, "is_correct": false, "is_blank": false}]
}

Notes:
- Date: Convert DD.MM.YYYY to YYYY-MM-DD
- Şb N = class_avg, Ok N = school_avg
- Subjects: Matematik, Fizik, Kimya, Biyoloji, Türkçe, Edebiyat, etc.
- Learning outcomes from "Kazanım Başarı Analizleri" (pages 2-3)
- Questions from answer grid: Cevap vs Öğrenci
- "." in student column = blank
- Net = Correct - (Wrong/4)

Return ONLY valid JSON."""

        try:
            # Call Claude API with vision
            # Note: Sonnet 4.x has 8K output tokens/minute rate limit
            # We use 7500 to stay safely under the limit
            message = self.client.messages.create(
                model=self.model,
                max_tokens=7500,  # Under 8K/minute rate limit for Sonnet 4.x
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

            # Check if response was truncated due to max_tokens
            if message.stop_reason == "max_tokens":
                import os
                debug_dir = "/tmp/claude_debug"
                os.makedirs(debug_dir, exist_ok=True)
                with open(f"{debug_dir}/last_response.txt", "w", encoding="utf-8") as f:
                    f.write(response_text)
                with open(f"{debug_dir}/last_error.txt", "w", encoding="utf-8") as f:
                    f.write(f"Response was truncated! Stop reason: {message.stop_reason}\n")
                    f.write(f"Response length: {len(response_text)} chars\n")
                    f.write(f"Model: {self.model}\n")
                    f.write(f"Max tokens requested: 32000\n")
                raise ValueError(
                    "Claude response was truncated due to max_tokens limit. "
                    "The PDF contains too much data to extract in one request. "
                    "Please try uploading a shorter exam PDF or contact support."
                )

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

    def analyze_text(self, prompt: str, max_tokens: int = 8000) -> str:
        """
        Analyze text using Claude API

        Args:
            prompt: Text prompt for analysis
            max_tokens: Maximum tokens in response

        Returns:
            Claude's text response
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0,  # Deterministic output
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract text response
            response_text = message.content[0].text
            return response_text

        except Exception as e:
            raise Exception(f"Claude API error during text analysis: {str(e)}")

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

    def analyze_exam_pdf_staged(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze exam PDF in 5 stages to avoid token limits

        Stage 1: Basic info (student, exam, overall results, subjects)
        Stage 2: Learning outcomes - Part 1 (first half)
        Stage 3: Learning outcomes - Part 2 (second half)
        Stage 4: Questions - Part 1 (first half)
        Stage 5: Questions - Part 2 (second half)

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Complete dictionary with all extracted exam data
        """
        import time

        # Read PDF once
        with open(pdf_path, "rb") as f:
            pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Stage 1: Basic data
        stage1_data = self._extract_stage1_basic(pdf_data)
        time.sleep(30)

        # Stage 2: Learning outcomes Part 1
        stage2_data = self._extract_stage2_outcomes_part1(pdf_data)
        time.sleep(30)

        # Stage 3: Learning outcomes Part 2
        stage3_data = self._extract_stage3_outcomes_part2(pdf_data)
        time.sleep(30)

        # Stage 4: Questions Part 1
        stage4_data = self._extract_stage4_questions_part1(pdf_data)
        time.sleep(30)

        # Stage 5: Questions Part 2
        stage5_data = self._extract_stage5_questions_part2(pdf_data)

        # Combine all stages
        complete_data = {
            **stage1_data,
            "learning_outcomes": stage2_data.get("learning_outcomes", []) + stage3_data.get("learning_outcomes", []),
            "questions": stage4_data.get("questions", []) + stage5_data.get("questions", [])
        }

        # Normalize subject names (remove (T) suffix and apply mappings)
        complete_data = normalize_subjects_in_data(complete_data)

        return complete_data

    def _extract_stage1_basic(self, pdf_data: str) -> Dict[str, Any]:
        """Stage 1: Extract student, exam, overall results, and subjects"""
        system_prompt = """You are an expert at analyzing Turkish university entrance exam reports.
Extract student, exam metadata, overall results, and subject breakdowns.
Pay close attention to Turkish characters and numerical data accuracy."""

        user_prompt = """Extract basic exam data in JSON format:

{
  "student": {"name": "", "school": "", "grade": "", "class_section": ""},
  "exam": {"exam_name": "", "exam_date": "YYYY-MM-DD", "booklet_type": "", "exam_number": 0},
  "overall_result": {
    "total_questions": 0, "total_correct": 0, "total_wrong": 0, "total_blank": 0,
    "net_score": 0.0, "net_percentage": 0.0,
    "class_rank": 0, "class_total": 0, "school_rank": 0, "school_total": 0,
    "class_avg": 0.0, "school_avg": 0.0
  },
  "subjects": [
    {
      "subject_name": "", "total_questions": 0, "correct": 0, "wrong": 0, "blank": 0,
      "net_score": 0.0, "net_percentage": 0.0,
      "class_rank": 0, "class_avg": 0.0, "school_rank": 0, "school_avg": 0.0
    }
  ]
}

Notes:
- Date: Convert DD.MM.YYYY to YYYY-MM-DD
- Şb N = class_avg, Ok N = school_avg
- Subjects: Matematik, Fizik, Kimya, Biyoloji, Türkçe, Edebiyat, Tarih, Coğrafya, etc.
- Net = Correct - (Wrong/4)

Return ONLY valid JSON."""

        return self._call_claude_api(pdf_data, system_prompt, user_prompt, max_tokens=7500)

    def _extract_stage2_outcomes_part1(self, pdf_data: str) -> Dict[str, Any]:
        """Stage 2: Extract learning outcomes - Part 1 (first half)"""
        system_prompt = """You are an expert at analyzing Turkish exam learning outcomes (kazanımlar).
Extract the FIRST HALF of learning outcome data with precise Turkish text."""

        user_prompt = """Extract FIRST HALF of learning outcomes from "Kazanım Başarı Analizleri" section:

{
  "learning_outcomes": [
    {
      "subject_name": "",
      "category": "",
      "subcategory": null,
      "outcome_description": null,
      "total_questions": 0,
      "acquired": 0,
      "lost": 0,
      "success_rate": 0.0,
      "student_percentage": 0.0,
      "class_percentage": 0.0,
      "school_percentage": 0.0
    }
  ]
}

Notes:
- Extract ONLY the first half of outcomes (approximately first 50%)
- Found in pages 2-3 typically
- Preserve exact Turkish text for categories and descriptions

Return ONLY valid JSON."""

        return self._call_claude_api(pdf_data, system_prompt, user_prompt, max_tokens=7500)

    def _extract_stage3_outcomes_part2(self, pdf_data: str) -> Dict[str, Any]:
        """Stage 3: Extract learning outcomes - Part 2 (second half)"""
        system_prompt = """You are an expert at analyzing Turkish exam learning outcomes (kazanımlar).
Extract the SECOND HALF of learning outcome data with precise Turkish text."""

        user_prompt = """Extract SECOND HALF of learning outcomes from "Kazanım Başarı Analizleri" section:

{
  "learning_outcomes": [
    {
      "subject_name": "",
      "category": "",
      "subcategory": null,
      "outcome_description": null,
      "total_questions": 0,
      "acquired": 0,
      "lost": 0,
      "success_rate": 0.0,
      "student_percentage": 0.0,
      "class_percentage": 0.0,
      "school_percentage": 0.0
    }
  ]
}

Notes:
- Extract ONLY the second half of outcomes (approximately last 50%)
- Found in pages 2-3 typically
- Preserve exact Turkish text for categories and descriptions

Return ONLY valid JSON."""

        return self._call_claude_api(pdf_data, system_prompt, user_prompt, max_tokens=7500)

    def _extract_stage4_questions_part1(self, pdf_data: str) -> Dict[str, Any]:
        """Stage 4: Extract questions - Part 1 (first half)"""
        system_prompt = """You are an expert at analyzing exam answer grids.
Extract question answers from the FIRST HALF of the answer grid."""

        user_prompt = """Extract FIRST HALF of questions from answer grid (approximately questions 1-45):

{
  "questions": [
    {
      "subject_name": "",
      "question_number": 0,
      "correct_answer": "",
      "student_answer": null,
      "is_correct": false,
      "is_blank": false
    }
  ]
}

Notes:
- Extract ONLY the first half of questions (roughly 1-45)
- "Cevap" column = correct_answer
- "Öğrenci" column = student_answer
- "." in student column means blank (null)
- Subject names: Matematik, Fizik, Kimya, Biyoloji, Türkçe, Edebiyat, Tarih, Coğrafya

Return ONLY valid JSON."""

        return self._call_claude_api(pdf_data, system_prompt, user_prompt, max_tokens=7500)

    def _extract_stage5_questions_part2(self, pdf_data: str) -> Dict[str, Any]:
        """Stage 5: Extract questions - Part 2 (second half)"""
        system_prompt = """You are an expert at analyzing exam answer grids.
Extract question answers from the SECOND HALF of the answer grid."""

        user_prompt = """Extract SECOND HALF of questions from answer grid (approximately questions 46-90):

{
  "questions": [
    {
      "subject_name": "",
      "question_number": 0,
      "correct_answer": "",
      "student_answer": null,
      "is_correct": false,
      "is_blank": false
    }
  ]
}

Notes:
- Extract ONLY the second half of questions (roughly 46 onwards)
- "Cevap" column = correct_answer
- "Öğrenci" column = student_answer
- "." in student column means blank (null)
- Subject names: Matematik, Fizik, Kimya, Biyoloji, Türkçe, Edebiyat, Tarih, Coğrafya

Return ONLY valid JSON."""

        return self._call_claude_api(pdf_data, system_prompt, user_prompt, max_tokens=7500)

    def _call_claude_api(
        self,
        pdf_data: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Helper method to call Claude API with consistent error handling"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0,
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

            response_text = message.content[0].text

            # Check for truncation
            if message.stop_reason == "max_tokens":
                raise ValueError(
                    f"Response was truncated at {max_tokens} tokens. "
                    "This stage contains too much data."
                )

            # Parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract from code blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                    return json.loads(json_str)
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    first_newline = response_text.find("\n", json_start)
                    if first_newline > json_start:
                        json_start = first_newline + 1
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                    return json.loads(json_str)
                else:
                    raise ValueError(f"Failed to parse JSON: {e}")

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
