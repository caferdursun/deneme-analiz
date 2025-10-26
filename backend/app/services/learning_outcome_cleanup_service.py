"""
Learning Outcome Cleanup Service - Claude AI-powered similarity detection and merge
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from app.models.learning_outcome import LearningOutcome
from app.models.outcome_merge_history import OutcomeMergeHistory
from app.utils.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class LearningOutcomeCleanupService:
    """
    Service for analyzing and merging similar learning outcomes using Claude AI
    """

    def __init__(self, db: Session):
        self.db = db
        self.claude_client = ClaudeClient()

    def analyze_outcomes(self, student_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze learning outcomes for similarity using Claude AI

        Returns similarity groups with confidence scores
        """
        # Fetch all active learning outcomes
        query = self.db.query(LearningOutcome).filter(
            LearningOutcome.is_merged == 0
        )

        if student_id:
            # Filter by student's exams
            query = query.join(LearningOutcome.exam).filter(
                LearningOutcome.exam.has(student_id=student_id)
            )

        outcomes = query.all()

        if not outcomes:
            return {
                "total_outcomes": 0,
                "similarity_groups": [],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        logger.info(f"Analyzing {len(outcomes)} learning outcomes for similarity")

        # Group outcomes by subject for better analysis
        outcomes_by_subject = {}
        for outcome in outcomes:
            subject = outcome.subject_name
            if subject not in outcomes_by_subject:
                outcomes_by_subject[subject] = []

            outcomes_by_subject[subject].append({
                "id": outcome.id,
                "subject": outcome.subject_name,
                "category": outcome.category or "",
                "subcategory": outcome.subcategory or "",
                "description": outcome.outcome_description or "",
                "total_questions": outcome.total_questions,
                "acquired": outcome.acquired,
                "lost": outcome.lost,
                "success_rate": float(outcome.success_rate) if outcome.success_rate else 0
            })

        # Analyze each subject separately
        all_similarity_groups = []

        for subject, subject_outcomes in outcomes_by_subject.items():
            if len(subject_outcomes) < 2:
                # No need to analyze if only one outcome
                continue

            logger.info(f"Analyzing {len(subject_outcomes)} outcomes for subject: {subject}")

            subject_groups = self._analyze_subject_outcomes(subject, subject_outcomes)
            all_similarity_groups.extend(subject_groups)

        return {
            "total_outcomes": len(outcomes),
            "similarity_groups": all_similarity_groups,
            "high_confidence_count": len([g for g in all_similarity_groups if g["confidence_score"] >= 90]),
            "medium_confidence_count": len([g for g in all_similarity_groups if 80 <= g["confidence_score"] < 90]),
            "low_confidence_count": len([g for g in all_similarity_groups if g["confidence_score"] < 80]),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    def _analyze_subject_outcomes(self, subject: str, outcomes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Use Claude AI to analyze outcomes for a specific subject
        """
        # Create prompt for Claude
        prompt = self._create_similarity_analysis_prompt(subject, outcomes)

        try:
            # Call Claude API
            response = self.claude_client.analyze_text(prompt)

            # Parse Claude's response (expecting JSON format)
            similarity_groups = self._parse_claude_response(response, outcomes)

            return similarity_groups

        except Exception as e:
            logger.error(f"Error analyzing outcomes with Claude: {e}")
            return []

    def _create_similarity_analysis_prompt(self, subject: str, outcomes: List[Dict]) -> str:
        """
        Create a prompt for Claude to analyze learning outcomes similarity
        """
        outcomes_text = json.dumps(outcomes, ensure_ascii=False, indent=2)

        prompt = f"""Türkçe eğitim sistemi için öğrenme kazanımlarını analiz et ve benzer olanları grupla.

Konu: {subject}

Kazanımlar:
{outcomes_text}

Görev:
1. Semantik olarak benzer kazanımları grupla (Türkçe dil varyasyonlarını dikkate al)
2. Her grup için confidence score (0-100) belirle
3. Her grup için standardize edilmiş bir isim öner
4. Neden bu kazanımların benzer olduğunu açıkla

Benzerlik kriterleri:
- Aynı veya çok benzer kavramları kapsıyor mu?
- Sadece kelime farklılıkları mı var? (örn: "Deyimler" vs "Deyim Bilgisi")
- Aynı alt kategoride mi?
- İçerik olarak overlap var mı?

ÖNEMLI: Sadece gerçekten benzer olan kazanımları grupla. Confidence score'u düşükse (<80) gruplama.

Yanıtını JSON formatında ver:
{{
  "similarity_groups": [
    {{
      "group_id": "unique_id",
      "confidence_score": 95,
      "suggested_name": "Standardize edilmiş kazanım adı",
      "reason": "Neden bu kazanımlar benzer",
      "outcome_ids": ["id1", "id2", "id3"]
    }}
  ]
}}

Sadece JSON yanıtı ver, başka açıklama ekleme."""

        return prompt

    def _parse_claude_response(self, response: str, outcomes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Parse Claude's JSON response into similarity groups
        """
        try:
            # Try to extract JSON from response
            response = response.strip()

            # Find JSON content (might be wrapped in markdown code blocks)
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            data = json.loads(response)

            similarity_groups = []

            for group in data.get("similarity_groups", []):
                # Validate outcome_ids exist
                valid_outcome_ids = [
                    oid for oid in group["outcome_ids"]
                    if any(o["id"] == oid for o in outcomes)
                ]

                if len(valid_outcome_ids) >= 2:  # Only include groups with 2+ outcomes
                    similarity_groups.append({
                        "group_id": group.get("group_id", str(uuid.uuid4())),
                        "confidence_score": group["confidence_score"],
                        "suggested_name": group["suggested_name"],
                        "reason": group["reason"],
                        "outcome_ids": valid_outcome_ids,
                        "total_questions": sum(
                            o["total_questions"] for o in outcomes
                            if o["id"] in valid_outcome_ids
                        ),
                        "outcomes": [o for o in outcomes if o["id"] in valid_outcome_ids]
                    })

            return similarity_groups

        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            logger.debug(f"Response was: {response}")
            return []

    def perform_merge(self, merge_groups: List[Dict[str, Any]], merged_by: str = "system") -> Dict[str, Any]:
        """
        Perform merge operations for approved similarity groups

        merge_groups format:
        [
            {
                "group_id": "...",
                "outcome_ids": ["id1", "id2"],
                "suggested_name": "...",
                "confidence_score": 95
            }
        ]
        """
        merged_count = 0
        failed_count = 0
        merge_results = []

        for group in merge_groups:
            try:
                result = self._merge_outcome_group(group, merged_by)
                merge_results.append(result)
                if result["success"]:
                    merged_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error merging group {group['group_id']}: {e}")
                failed_count += 1
                merge_results.append({
                    "group_id": group["group_id"],
                    "success": False,
                    "error": str(e)
                })

        self.db.commit()

        return {
            "total_groups": len(merge_groups),
            "merged_count": merged_count,
            "failed_count": failed_count,
            "results": merge_results,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _merge_outcome_group(self, group: Dict[str, Any], merged_by: str) -> Dict[str, Any]:
        """
        Merge a single group of outcomes

        Strategy:
        - Select first outcome as primary (target)
        - Merge others into it
        - Update target outcome stats (aggregate)
        - Mark others as merged
        - Create audit trail
        """
        outcome_ids = group["outcome_ids"]
        merge_group_id = group["group_id"]

        if len(outcome_ids) < 2:
            return {"group_id": merge_group_id, "success": False, "error": "Need at least 2 outcomes to merge"}

        # Fetch outcomes
        outcomes = self.db.query(LearningOutcome).filter(
            LearningOutcome.id.in_(outcome_ids),
            LearningOutcome.is_merged == 0
        ).all()

        if len(outcomes) < 2:
            return {"group_id": merge_group_id, "success": False, "error": "Outcomes not found or already merged"}

        # Select target (primary) outcome - use the first one
        target = outcomes[0]
        others = outcomes[1:]

        # Store original target data for audit
        target_data_before = {
            "id": target.id,
            "outcome_description": target.outcome_description,
            "total_questions": target.total_questions,
            "acquired": target.acquired,
            "lost": target.lost,
            "success_rate": float(target.success_rate) if target.success_rate else 0
        }

        # Aggregate statistics
        total_questions = sum(o.total_questions for o in outcomes)
        total_acquired = sum(o.acquired for o in outcomes)
        total_lost = sum(o.lost for o in outcomes)

        # Calculate new success rate
        if total_questions > 0:
            new_success_rate = (total_acquired / total_questions) * 100
        else:
            new_success_rate = 0

        # Update target outcome
        target.outcome_description = group.get("suggested_name", target.outcome_description)
        target.total_questions = total_questions
        target.acquired = total_acquired
        target.lost = total_lost
        target.success_rate = new_success_rate

        # Mark others as merged and create audit trail
        for other in others:
            # Store original data
            original_data = {
                "id": other.id,
                "exam_id": other.exam_id,
                "subject_name": other.subject_name,
                "category": other.category,
                "subcategory": other.subcategory,
                "outcome_description": other.outcome_description,
                "total_questions": other.total_questions,
                "acquired": other.acquired,
                "lost": other.lost,
                "success_rate": float(other.success_rate) if other.success_rate else 0
            }

            # Mark as merged
            other.is_merged = 1
            other.merged_into_id = target.id

            # Create audit trail
            audit = OutcomeMergeHistory(
                id=str(uuid.uuid4()),
                merge_group_id=merge_group_id,
                merged_at=datetime.utcnow(),
                merged_by=merged_by,
                original_outcome_id=other.id,
                target_outcome_id=target.id,
                original_data=original_data,
                target_data_before=target_data_before,
                confidence_score=group.get("confidence_score"),
                similarity_reason=group.get("reason", "")
            )
            self.db.add(audit)

        return {
            "group_id": merge_group_id,
            "success": True,
            "target_id": target.id,
            "merged_ids": [o.id for o in others],
            "total_questions": total_questions,
            "new_success_rate": new_success_rate
        }

    def undo_merge(self, merge_group_id: str, undone_by: str = "system") -> Dict[str, Any]:
        """
        Undo a merge operation by restoring original outcomes
        """
        # Find all merge history records for this group
        merge_records = self.db.query(OutcomeMergeHistory).filter(
            OutcomeMergeHistory.merge_group_id == merge_group_id,
            OutcomeMergeHistory.undone_at.is_(None)
        ).all()

        if not merge_records:
            return {"success": False, "error": "Merge group not found or already undone"}

        restored_count = 0

        for record in merge_records:
            # Find the merged outcome
            merged_outcome = self.db.query(LearningOutcome).filter(
                LearningOutcome.id == record.original_outcome_id
            ).first()

            if merged_outcome and merged_outcome.is_merged == 1:
                # Restore original data
                original = record.original_data
                merged_outcome.outcome_description = original["outcome_description"]
                merged_outcome.total_questions = original["total_questions"]
                merged_outcome.acquired = original["acquired"]
                merged_outcome.lost = original["lost"]
                merged_outcome.success_rate = original["success_rate"]
                merged_outcome.is_merged = 0
                merged_outcome.merged_into_id = None

                restored_count += 1

            # Mark record as undone
            record.undone_at = datetime.utcnow()
            record.undone_by = undone_by

        # Restore target outcome to its original state
        if merge_records:
            first_record = merge_records[0]
            target_outcome = self.db.query(LearningOutcome).filter(
                LearningOutcome.id == first_record.target_outcome_id
            ).first()

            if target_outcome and first_record.target_data_before:
                target_before = first_record.target_data_before
                target_outcome.outcome_description = target_before["outcome_description"]
                target_outcome.total_questions = target_before["total_questions"]
                target_outcome.acquired = target_before["acquired"]
                target_outcome.lost = target_before["lost"]
                target_outcome.success_rate = target_before["success_rate"]

        self.db.commit()

        return {
            "success": True,
            "merge_group_id": merge_group_id,
            "restored_count": restored_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_merge_history(self, limit: int = 50, include_undone: bool = False) -> List[Dict[str, Any]]:
        """
        Get recent merge operations
        """
        query = self.db.query(OutcomeMergeHistory)

        if not include_undone:
            query = query.filter(OutcomeMergeHistory.undone_at.is_(None))

        records = query.order_by(OutcomeMergeHistory.merged_at.desc()).limit(limit).all()

        # Group by merge_group_id
        history_groups = {}
        for record in records:
            group_id = record.merge_group_id
            if group_id not in history_groups:
                history_groups[group_id] = {
                    "merge_group_id": group_id,
                    "merged_at": record.merged_at.isoformat(),
                    "merged_by": record.merged_by,
                    "confidence_score": float(record.confidence_score) if record.confidence_score else None,
                    "similarity_reason": record.similarity_reason,
                    "is_undone": record.undone_at is not None,
                    "undone_at": record.undone_at.isoformat() if record.undone_at else None,
                    "undone_by": record.undone_by,
                    "merged_outcomes": []
                }

            history_groups[group_id]["merged_outcomes"].append({
                "original_id": record.original_outcome_id,
                "target_id": record.target_outcome_id,
                "original_description": record.original_data.get("outcome_description") if record.original_data else None
            })

        return list(history_groups.values())
