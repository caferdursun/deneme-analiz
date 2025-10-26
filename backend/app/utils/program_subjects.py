"""
University entrance exam program definitions and relevant subjects
"""
from typing import List, Dict

# Program-specific subject lists
PROGRAM_SUBJECTS: Dict[str, List[str]] = {
    "MF": [  # Matematik-Fen (Math-Science)
        "Türkçe",
        "Matematik",
        "Geometri",
        "Fizik",
        "Kimya",
        "Biyoloji",
    ],
    "TM": [  # Türkçe-Matematik (Turkish-Math)
        "Türkçe",
        "Matematik",
        "Geometri",
        "Tarih",
        "Coğrafya",
    ],
    "SÖZEL": [  # Sözel (Verbal/Social Sciences)
        "Türkçe",
        "Tarih",
        "Coğrafya",
        "Felsefe",
        "Din Kültürü",
    ],
    "DİL": [  # Dil (Language)
        "Türkçe",
    ],
}


def get_program_subjects(program: str) -> List[str]:
    """
    Get relevant subjects for a specific program

    Args:
        program: Program code (MF, TM, SÖZEL, DİL)

    Returns:
        List of subject names relevant to the program
    """
    return PROGRAM_SUBJECTS.get(program, [])


def is_subject_relevant(subject_name: str, program: str) -> bool:
    """
    Check if a subject is relevant for a specific program

    Args:
        subject_name: Name of the subject
        program: Program code (MF, TM, SÖZEL, DİL)

    Returns:
        True if subject is relevant for the program
    """
    relevant_subjects = get_program_subjects(program)
    return subject_name in relevant_subjects
