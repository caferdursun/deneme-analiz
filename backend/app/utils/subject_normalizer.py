"""
Utility for normalizing subject names to avoid duplicates
"""
import re
from typing import Dict


# Mapping of variations to canonical names
SUBJECT_MAPPINGS: Dict[str, str] = {
    # Math variations
    "T.Matematik": "Matematik",
    "Temel Matematik": "Matematik",

    # Science variations
    "Fen Bilimleri": "Fen Bilimleri",

    # Social sciences
    "Sosyal Bilimler": "Sosyal Bilimler",
    "Din Kültürü ve Ahlak Bilgisi": "Din Kültürü",
}


def normalize_subject_name(subject_name: str) -> str:
    """
    Normalize subject name by:
    1. Removing (T) suffix (TYT exam marker)
    2. Applying custom mappings
    3. Trimming whitespace

    Args:
        subject_name: Original subject name from PDF

    Returns:
        Normalized subject name

    Examples:
        >>> normalize_subject_name("Türkçe(T)")
        'Türkçe'
        >>> normalize_subject_name("Fizik(T)")
        'Fizik'
        >>> normalize_subject_name("T.Matematik(T)")
        'Matematik'
        >>> normalize_subject_name("Temel Matematik")
        'Matematik'
    """
    if not subject_name:
        return subject_name

    # Remove (T) suffix
    normalized = re.sub(r'\(T\)$', '', subject_name).strip()

    # Apply custom mappings
    if normalized in SUBJECT_MAPPINGS:
        normalized = SUBJECT_MAPPINGS[normalized]

    return normalized


def normalize_subjects_in_data(data: Dict) -> Dict:
    """
    Normalize all subject names in extracted exam data

    Args:
        data: Exam data dictionary with subjects, learning_outcomes, questions

    Returns:
        Data with normalized subject names
    """
    # Normalize subject results
    if "subjects" in data:
        for subject in data["subjects"]:
            if "subject_name" in subject:
                subject["subject_name"] = normalize_subject_name(subject["subject_name"])

    # Normalize learning outcomes
    if "learning_outcomes" in data:
        for outcome in data["learning_outcomes"]:
            if "subject_name" in outcome:
                outcome["subject_name"] = normalize_subject_name(outcome["subject_name"])

    # Normalize questions
    if "questions" in data:
        for question in data["questions"]:
            if "subject_name" in question:
                question["subject_name"] = normalize_subject_name(question["subject_name"])

    return data
