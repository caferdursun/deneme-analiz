"""
Local PDF parser for extracting and validating exam data
"""
import pdfplumber
import re
from typing import Dict, Any, List, Optional
from pathlib import Path


class LocalPDFParser:
    """Extract key numerical data from exam PDFs using local parsing"""

    def __init__(self):
        self.text_content = ""
        self.tables = []

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse PDF and extract key numerical data for validation

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted numerical data
        """
        with pdfplumber.open(pdf_path) as pdf:
            # Extract all text
            self.text_content = "\n".join(page.extract_text() or "" for page in pdf.pages)

            # Extract tables from all pages
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    self.tables.extend(tables)

        return {
            "student_info": self._extract_student_info(),
            "overall_scores": self._extract_overall_scores(),
            "subject_scores": self._extract_subject_scores(),
            "answer_grid": self._extract_answer_grid(),
            "metadata": self._extract_metadata()
        }

    def _extract_student_info(self) -> Dict[str, Optional[str]]:
        """Extract student information"""
        info = {}

        # Extract student name
        name_match = re.search(r'(?:Adı Soyadı|Ad Soyad)[:\s]+([A-ZÇĞİÖŞÜ\s]+)', self.text_content)
        if name_match:
            info['name'] = name_match.group(1).strip()

        # Extract school
        school_match = re.search(r'(?:Okul|Kurum)[:\s]+([A-ZÇĞİÖŞÜ\s\.]+)', self.text_content)
        if school_match:
            info['school'] = school_match.group(1).strip()

        # Extract class/section
        class_match = re.search(r'(?:Sınıf|Şube)[:\s]+(\d+/[A-Z]|\d+\s*[A-Z])', self.text_content)
        if class_match:
            info['class_section'] = class_match.group(1).strip()

        return info

    def _extract_overall_scores(self) -> Dict[str, Optional[float]]:
        """Extract overall exam scores"""
        scores = {}

        # Look for patterns like "Toplam: 88" or "D: 53 Y: 14 B: 21"
        # Total questions
        total_match = re.search(r'(?:Toplam|Top)[:\s]+(\d+)', self.text_content)
        if total_match:
            scores['total_questions'] = int(total_match.group(1))

        # Correct answers (Doğru)
        correct_match = re.search(r'(?:Doğru|D)[:\s]+(\d+)', self.text_content)
        if correct_match:
            scores['total_correct'] = int(correct_match.group(1))

        # Wrong answers (Yanlış)
        wrong_match = re.search(r'(?:Yanlış|Y)[:\s]+(\d+)', self.text_content)
        if wrong_match:
            scores['total_wrong'] = int(wrong_match.group(1))

        # Blank answers (Boş)
        blank_match = re.search(r'(?:Boş|B)[:\s]+(\d+)', self.text_content)
        if blank_match:
            scores['total_blank'] = int(blank_match.group(1))

        # Net score
        net_match = re.search(r'(?:Net|N)[:\s]+(\d+[,.]?\d*)', self.text_content)
        if net_match:
            net_str = net_match.group(1).replace(',', '.')
            scores['net_score'] = float(net_str)

        return scores

    def _extract_subject_scores(self) -> List[Dict[str, Any]]:
        """Extract per-subject scores from tables"""
        subjects = []

        # Common subject names
        subject_names = ['Matematik', 'Fizik', 'Kimya', 'Biyoloji', 'Türkçe', 'Edebiyat']

        for table in self.tables:
            for row in table:
                if not row or len(row) < 3:
                    continue

                # Check if first cell contains a subject name
                first_cell = str(row[0] or "").strip()
                for subject_name in subject_names:
                    if subject_name.lower() in first_cell.lower():
                        # Try to extract numeric data from the row
                        numbers = self._extract_numbers_from_row(row)
                        if numbers and len(numbers) >= 4:
                            subjects.append({
                                'subject_name': subject_name,
                                'total_questions': numbers[0] if len(numbers) > 0 else None,
                                'correct': numbers[1] if len(numbers) > 1 else None,
                                'wrong': numbers[2] if len(numbers) > 2 else None,
                                'blank': numbers[3] if len(numbers) > 3 else None,
                                'net_score': numbers[4] if len(numbers) > 4 else None,
                            })
                        break

        return subjects

    def _extract_numbers_from_row(self, row: List[Any]) -> List[float]:
        """Extract all numbers from a table row"""
        numbers = []
        for cell in row:
            if cell is None:
                continue
            # Find all numbers in the cell
            cell_str = str(cell).replace(',', '.')
            found_numbers = re.findall(r'\d+\.?\d*', cell_str)
            numbers.extend([float(n) for n in found_numbers])
        return numbers

    def _extract_answer_grid(self) -> Dict[str, int]:
        """Extract answer statistics from answer grid"""
        stats = {}

        # Count answer occurrences (A, B, C, D, E)
        for answer in ['A', 'B', 'C', 'D', 'E']:
            # Look for patterns like "Cevap: A" or "Öğrenci: A"
            pattern = rf'(?:Cevap|Öğrenci|Şık)[:\s]+{answer}'
            matches = re.findall(pattern, self.text_content)
            stats[f'answer_{answer}_count'] = len(matches)

        # Count blank answers (represented as "." or "Boş")
        blank_pattern = r'(?:Öğrenci|Şık)[:\s]+\.'
        blank_matches = re.findall(blank_pattern, self.text_content)
        stats['blank_count'] = len(blank_matches)

        return stats

    def _extract_metadata(self) -> Dict[str, Optional[str]]:
        """Extract exam metadata"""
        metadata = {}

        # Exam date
        date_match = re.search(r'(?:Tarih|Sınav Tarihi)[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})', self.text_content)
        if date_match:
            metadata['exam_date'] = date_match.group(1)

        # Exam name
        exam_name_match = re.search(r'((?:\d{4}[-\s])?[\w\s]+SINAV[I\s]+[\w\s]+)', self.text_content, re.IGNORECASE)
        if exam_name_match:
            metadata['exam_name'] = exam_name_match.group(1).strip()

        # Booklet type
        booklet_match = re.search(r'(?:Kitapçık|Kitapcik)[:\s]+([A-E])', self.text_content, re.IGNORECASE)
        if booklet_match:
            metadata['booklet_type'] = booklet_match.group(1)

        return metadata

    def get_text_content(self) -> str:
        """Get the raw text content of the PDF"""
        return self.text_content

    def get_tables(self) -> List[List[List[Any]]]:
        """Get extracted tables from the PDF"""
        return self.tables
