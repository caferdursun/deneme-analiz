"""
Validation service for comparing Claude AI output with local PDF parsing
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ValidationIssue:
    """Represents a validation issue found during comparison"""

    def __init__(self, field: str, claude_value: Any, local_value: Any, severity: str = "warning"):
        self.field = field
        self.claude_value = claude_value
        self.local_value = local_value
        self.severity = severity  # "warning", "error", "info"

    def __repr__(self):
        return f"ValidationIssue({self.field}: Claude={self.claude_value}, Local={self.local_value}, severity={self.severity})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "claude_value": self.claude_value,
            "local_value": self.local_value,
            "severity": self.severity
        }


class ValidationService:
    """Service for validating Claude AI output against local PDF parsing"""

    def __init__(self, tolerance: float = 0.1):
        """
        Args:
            tolerance: Tolerance for numeric comparisons (0.1 = 10% difference allowed)
        """
        self.tolerance = tolerance
        self.issues: List[ValidationIssue] = []

    def validate(self, claude_data: Dict[str, Any], local_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Claude output against local parsing

        Args:
            claude_data: Data extracted by Claude AI
            local_data: Data extracted by local parser

        Returns:
            Validation report with issues and status
        """
        self.issues = []

        # Validate student info
        self._validate_student_info(
            claude_data.get("student", {}),
            local_data.get("student_info", {})
        )

        # Validate overall scores
        self._validate_overall_scores(
            claude_data.get("overall_result", {}),
            local_data.get("overall_scores", {})
        )

        # Validate subject scores
        self._validate_subject_scores(
            claude_data.get("subjects", []),
            local_data.get("subject_scores", [])
        )

        # Validate metadata
        self._validate_metadata(
            claude_data.get("exam", {}),
            local_data.get("metadata", {})
        )

        # Generate report
        return self._generate_report()

    def _validate_student_info(self, claude_student: Dict, local_student: Dict):
        """Validate student information"""
        if not local_student:
            return

        # Check name match
        if local_student.get("name"):
            if not self._fuzzy_match(
                claude_student.get("name", ""),
                local_student["name"]
            ):
                self.issues.append(ValidationIssue(
                    "student.name",
                    claude_student.get("name"),
                    local_student["name"],
                    "warning"
                ))

        # Check school match
        if local_student.get("school"):
            if not self._fuzzy_match(
                claude_student.get("school", ""),
                local_student["school"],
                threshold=0.7  # More lenient for school names
            ):
                self.issues.append(ValidationIssue(
                    "student.school",
                    claude_student.get("school"),
                    local_student["school"],
                    "info"
                ))

    def _validate_overall_scores(self, claude_scores: Dict, local_scores: Dict):
        """Validate overall exam scores"""
        if not local_scores:
            return

        # Validate numeric fields
        numeric_fields = [
            "total_questions",
            "total_correct",
            "total_wrong",
            "total_blank",
            "net_score"
        ]

        for field in numeric_fields:
            claude_val = claude_scores.get(field)
            local_val = local_scores.get(field)

            if local_val is not None and claude_val is not None:
                if not self._numeric_match(claude_val, local_val):
                    # Critical error for basic counts
                    severity = "error" if field in ["total_questions", "total_correct"] else "warning"
                    self.issues.append(ValidationIssue(
                        f"overall.{field}",
                        claude_val,
                        local_val,
                        severity
                    ))

        # Validate net score calculation: net = correct - (wrong / 4)
        if all(k in claude_scores for k in ["total_correct", "total_wrong", "net_score"]):
            expected_net = claude_scores["total_correct"] - (claude_scores["total_wrong"] / 4)
            actual_net = claude_scores["net_score"]

            if not self._numeric_match(expected_net, actual_net, tolerance=0.05):
                self.issues.append(ValidationIssue(
                    "overall.net_calculation",
                    actual_net,
                    expected_net,
                    "error"
                ))

    def _validate_subject_scores(self, claude_subjects: List[Dict], local_subjects: List[Dict]):
        """Validate per-subject scores"""
        if not local_subjects:
            return

        # Create lookup by subject name
        local_by_name = {s["subject_name"]: s for s in local_subjects}

        for claude_subject in claude_subjects:
            subject_name = claude_subject.get("subject_name")
            if subject_name in local_by_name:
                local_subject = local_by_name[subject_name]

                # Validate numeric fields for this subject
                for field in ["total_questions", "correct", "wrong", "blank", "net_score"]:
                    claude_val = claude_subject.get(field)
                    local_val = local_subject.get(field)

                    if local_val is not None and claude_val is not None:
                        if not self._numeric_match(claude_val, local_val):
                            self.issues.append(ValidationIssue(
                                f"subject.{subject_name}.{field}",
                                claude_val,
                                local_val,
                                "warning"
                            ))

    def _validate_metadata(self, claude_exam: Dict, local_metadata: Dict):
        """Validate exam metadata"""
        if not local_metadata:
            return

        # Check booklet type
        if local_metadata.get("booklet_type"):
            if claude_exam.get("booklet_type") != local_metadata["booklet_type"]:
                self.issues.append(ValidationIssue(
                    "exam.booklet_type",
                    claude_exam.get("booklet_type"),
                    local_metadata["booklet_type"],
                    "warning"
                ))

    def _numeric_match(self, val1: float, val2: float, tolerance: float = None) -> bool:
        """
        Check if two numeric values match within tolerance

        Args:
            val1: First value
            val2: Second value
            tolerance: Allowed relative difference (default: self.tolerance)
        """
        if tolerance is None:
            tolerance = self.tolerance

        try:
            v1 = float(val1)
            v2 = float(val2)

            # Exact match
            if v1 == v2:
                return True

            # Check relative difference
            avg = (abs(v1) + abs(v2)) / 2
            if avg == 0:
                return abs(v1 - v2) < 0.01  # Absolute tolerance for values near zero

            rel_diff = abs(v1 - v2) / avg
            return rel_diff <= tolerance

        except (ValueError, TypeError):
            return False

    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """
        Check if two strings match with fuzzy matching

        Args:
            str1: First string
            str2: Second string
            threshold: Similarity threshold (0-1)
        """
        if not str1 or not str2:
            return False

        # Normalize
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()

        # Exact match
        if s1 == s2:
            return True

        # Simple character-based similarity
        if len(s1) == 0 or len(s2) == 0:
            return False

        # Check if one is substring of another
        if s1 in s2 or s2 in s1:
            return True

        # Calculate simple similarity ratio
        common_chars = sum(1 for c in s1 if c in s2)
        similarity = common_chars / max(len(s1), len(s2))

        return similarity >= threshold

    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        info = [i for i in self.issues if i.severity == "info"]

        status = "passed"
        if errors:
            status = "failed"
        elif warnings:
            status = "warning"

        return {
            "status": status,
            "total_issues": len(self.issues),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self._generate_summary(errors, warnings, info)
        }

    def _generate_summary(self, errors: List, warnings: List, info: List) -> str:
        """Generate human-readable summary"""
        if not self.issues:
            return "Validation passed. Claude output matches local parsing."

        parts = []
        if errors:
            parts.append(f"{len(errors)} critical error(s)")
        if warnings:
            parts.append(f"{len(warnings)} warning(s)")
        if info:
            parts.append(f"{len(info)} info message(s)")

        return f"Validation completed with {', '.join(parts)}. Review issues for details."
