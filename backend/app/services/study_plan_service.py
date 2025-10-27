"""
Study Plan Service for generating personalized study schedules
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
import json
import os

from app.models import StudyPlan, StudyPlanDay, StudyPlanItem, Recommendation, Student
from app.schemas.study_plan import (
    StudyPlanGenerateRequest,
    StudyPlanResponse,
    StudyPlanProgressResponse,
)
from app.core.config import settings
from anthropic import Anthropic


class StudyPlanService:
    """Service for generating and managing study plans"""

    def __init__(self, db: Session):
        self.db = db
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate_study_plan(self, request: StudyPlanGenerateRequest) -> StudyPlanResponse:
        """
        Generate a personalized study plan using Claude AI

        Args:
            request: StudyPlanGenerateRequest with plan parameters

        Returns:
            StudyPlanResponse with complete plan
        """
        # Get student
        student_id = request.student_id
        if not student_id:
            student = self.db.query(Student).first()
            if not student:
                raise ValueError("No student found")
            student_id = student.id

        # Get recommendations
        recommendations = []
        if request.recommendation_ids:
            recommendations = (
                self.db.query(Recommendation)
                .filter(Recommendation.id.in_(request.recommendation_ids))
                .filter(Recommendation.student_id == student_id)
                .all()
            )
        else:
            # If no recommendations specified, get all active ones
            recommendations = (
                self.db.query(Recommendation)
                .filter(Recommendation.student_id == student_id)
                .filter(Recommendation.is_active == True)
                .order_by(Recommendation.priority.asc(), Recommendation.impact_score.desc())
                .limit(10)  # Limit to top 10
                .all()
            )

        if not recommendations:
            raise ValueError("No recommendations found to create study plan")

        # Generate schedule using Claude AI
        schedule = self._generate_schedule_with_claude(
            recommendations=recommendations,
            time_frame=request.time_frame,
            daily_study_time=request.daily_study_time,
            study_style=request.study_style,
        )

        # Create study plan in database
        start_date = date.today()
        end_date = start_date + timedelta(days=request.time_frame - 1)

        study_plan = StudyPlan(
            student_id=student_id,
            name=request.name,
            time_frame=request.time_frame,
            daily_study_time=request.daily_study_time,
            study_style=request.study_style,
            status='active',
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(study_plan)
        self.db.flush()  # Get study_plan.id

        # Create days and items
        for day_data in schedule:
            plan_day = StudyPlanDay(
                plan_id=study_plan.id,
                day_number=day_data['day'],
                date=datetime.strptime(day_data['date'], '%Y-%m-%d').date(),
                total_duration_minutes=sum(item['duration_minutes'] for item in day_data['items']),
                completed=False,
            )
            self.db.add(plan_day)
            self.db.flush()  # Get plan_day.id

            for item_data in day_data['items']:
                plan_item = StudyPlanItem(
                    day_id=plan_day.id,
                    recommendation_id=item_data.get('recommendation_id'),
                    subject_name=item_data['subject'],
                    topic=item_data['topic'],
                    description=item_data.get('description'),
                    duration_minutes=item_data['duration_minutes'],
                    order=item_data['order'],
                    completed=False,
                )
                self.db.add(plan_item)

        self.db.commit()
        self.db.refresh(study_plan)

        return StudyPlanResponse.from_orm(study_plan)

    def _generate_schedule_with_claude(
        self,
        recommendations: List[Recommendation],
        time_frame: int,
        daily_study_time: int,
        study_style: str,
    ) -> List[Dict[str, Any]]:
        """
        Use Claude AI to generate an optimal study schedule

        Returns:
            List of daily schedules in JSON format
        """
        # Prepare recommendations data for Claude
        recs_data = []
        for rec in recommendations:
            recs_data.append({
                "id": rec.id,
                "priority": rec.priority,
                "subject": rec.subject_name,
                "topic": rec.topic,
                "description": rec.description,
                "impact_score": float(rec.impact_score) if rec.impact_score else 0,
                "action_items": rec.action_items or [],
            })

        # Study style parameters
        style_params = {
            "intensive": {
                "study_ratio": 0.85,  # 85% study, 15% review
                "break_frequency": 90,  # Break every 90 min
                "rest_days": 0,
            },
            "balanced": {
                "study_ratio": 0.75,  # 75% study, 25% review
                "break_frequency": 60,  # Break every 60 min
                "rest_days": time_frame // 7,  # 1 rest day per week
            },
            "relaxed": {
                "study_ratio": 0.65,  # 65% study, 35% review
                "break_frequency": 45,  # Break every 45 min
                "rest_days": time_frame // 5,  # More rest days
            },
        }

        params = style_params.get(study_style, style_params['balanced'])

        # Claude AI prompt
        prompt = f"""You are an expert study planner. Create a personalized study schedule.

**Input:**
- Time frame: {time_frame} days
- Daily study time: {daily_study_time} minutes
- Study style: {study_style}
- Style parameters: {json.dumps(params, indent=2)}

**Recommendations to cover:**
{json.dumps(recs_data, indent=2, ensure_ascii=False)}

**Instructions:**
1. Distribute topics across {time_frame} days
2. Prioritize by impact_score and priority (lower priority number = higher importance)
3. Balance subjects across days
4. Include review sessions ({int(params['study_ratio'] * 100)}% new material, {int((1-params['study_ratio'])*100)}% review)
5. Schedule {params['rest_days']} rest days if applicable
6. Each study session should be {params['break_frequency']} minutes or less before a break

**Output Format (JSON array):**
```json
[
  {{
    "day": 1,
    "date": "{(date.today() + timedelta(days=0)).strftime('%Y-%m-%d')}",
    "items": [
      {{
        "recommendation_id": "rec_id_here",
        "subject": "Subject Name",
        "topic": "Topic Name",
        "description": "What to study specifically",
        "duration_minutes": 60,
        "order": 1
      }}
    ]
  }}
]
```

Generate the complete schedule now. Output ONLY valid JSON, no additional text."""

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse Claude's response
        response_text = message.content[0].text

        # Extract JSON from response (remove markdown code blocks if present)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        schedule = json.loads(response_text)

        return schedule

    def get_study_plan(self, plan_id: str) -> Optional[StudyPlanResponse]:
        """Get a study plan by ID"""
        plan = self.db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
        if not plan:
            return None
        return StudyPlanResponse.from_orm(plan)

    def get_active_plan(self, student_id: str) -> Optional[StudyPlanResponse]:
        """Get the active study plan for a student"""
        plan = (
            self.db.query(StudyPlan)
            .filter(StudyPlan.student_id == student_id)
            .filter(StudyPlan.status == 'active')
            .order_by(StudyPlan.created_at.desc())
            .first()
        )
        if not plan:
            return None
        return StudyPlanResponse.from_orm(plan)

    def get_all_plans(self, student_id: str) -> List[StudyPlanResponse]:
        """Get all study plans for a student"""
        plans = (
            self.db.query(StudyPlan)
            .filter(StudyPlan.student_id == student_id)
            .order_by(StudyPlan.created_at.desc())
            .all()
        )
        return [StudyPlanResponse.from_orm(plan) for plan in plans]

    def update_item_completion(self, item_id: str, completed: bool) -> bool:
        """Mark a study plan item as complete/incomplete"""
        item = self.db.query(StudyPlanItem).filter(StudyPlanItem.id == item_id).first()
        if not item:
            return False

        item.completed = completed
        item.completed_at = datetime.utcnow() if completed else None

        # Flush to ensure the item update is reflected in the session
        self.db.flush()

        # Update day completion status
        day = self.db.query(StudyPlanDay).filter(StudyPlanDay.id == item.day_id).first()
        if day:
            # Get all items for this day (including the just-updated item)
            all_items = self.db.query(StudyPlanItem).filter(StudyPlanItem.day_id == day.id).all()
            # Check if ALL items are completed
            day.completed = all(i.completed for i in all_items)

        self.db.commit()
        return True

    def calculate_progress(self, plan_id: str) -> Optional[StudyPlanProgressResponse]:
        """Calculate progress statistics for a study plan"""
        plan = self.db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
        if not plan:
            return None

        # Count items
        total_items = (
            self.db.query(StudyPlanItem)
            .join(StudyPlanDay)
            .filter(StudyPlanDay.plan_id == plan_id)
            .count()
        )

        completed_items = (
            self.db.query(StudyPlanItem)
            .join(StudyPlanDay)
            .filter(StudyPlanDay.plan_id == plan_id)
            .filter(StudyPlanItem.completed == True)
            .count()
        )

        # Count days
        total_days = self.db.query(StudyPlanDay).filter(StudyPlanDay.plan_id == plan_id).count()
        completed_days = (
            self.db.query(StudyPlanDay)
            .filter(StudyPlanDay.plan_id == plan_id)
            .filter(StudyPlanDay.completed == True)
            .count()
        )

        # Calculate days remaining
        today = date.today()
        if today > plan.end_date:
            days_remaining = 0
        else:
            days_remaining = (plan.end_date - today).days + 1

        # Check if on track
        expected_completion = (plan.time_frame - days_remaining) / plan.time_frame if plan.time_frame > 0 else 0
        actual_completion = completed_items / total_items if total_items > 0 else 0
        on_track = actual_completion >= (expected_completion - 0.1)  # 10% tolerance

        return StudyPlanProgressResponse(
            plan_id=plan_id,
            total_items=total_items,
            completed_items=completed_items,
            completion_percentage=round(actual_completion * 100, 1),
            total_days=total_days,
            completed_days=completed_days,
            days_remaining=days_remaining,
            on_track=on_track,
        )

    def archive_plan(self, plan_id: str) -> bool:
        """Archive a study plan"""
        plan = self.db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
        if not plan:
            return False

        plan.status = 'archived'
        plan.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a study plan (cascade deletes days and items)"""
        plan = self.db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
        if not plan:
            return False

        self.db.delete(plan)
        self.db.commit()
        return True
