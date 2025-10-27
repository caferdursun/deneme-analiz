"""
Claude AI-powered resource curator service
Uses Claude API to intelligently curate educational resources
"""
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
from app.core.config import settings


class ClaudeCuratorService:
    """Service for AI-powered resource curation using Claude"""

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5-20250929"

    def curate_resources(
        self,
        subject: str,
        topic: str,
        learning_outcome: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Use Claude to curate educational resources for a specific topic

        Args:
            subject: Subject name (e.g., "Biyoloji")
            topic: Topic name (e.g., "Hücre Bölünmeleri")
            learning_outcome: Specific learning outcome description
            category: Learning outcome category
            subcategory: Learning outcome subcategory

        Returns:
            Dictionary with 'youtube', 'pdf', and 'website' resource lists
        """
        prompt = self._build_curation_prompt(
            subject=subject,
            topic=topic,
            learning_outcome=learning_outcome,
            category=category,
            subcategory=subcategory
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract text content from response
            content_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content_text += block.text

            # Parse JSON response
            resources_data = self._parse_claude_response(content_text)

            return resources_data

        except Exception as e:
            print(f"Error in Claude curation: {e}")
            # Return empty lists if Claude fails
            return {
                "youtube": [],
                "pdf": [],
                "website": []
            }

    def _build_curation_prompt(
        self,
        subject: str,
        topic: str,
        learning_outcome: Optional[str],
        category: Optional[str],
        subcategory: Optional[str]
    ) -> str:
        """Build the prompt for Claude to curate resources"""

        outcome_context = ""
        if learning_outcome:
            outcome_context = f"\n**Kazanım:** {learning_outcome}"
        if category:
            outcome_context += f"\n**Kategori:** {category}"
        if subcategory:
            outcome_context += f"\n**Alt Kategori:** {subcategory}"

        prompt = f"""Türkiye'de lise seviyesi (YKS/AYT hazırlık) için eğitim kaynağı küratörlüğü yapıyorsun.

**Konu:** {subject} - {topic}
{outcome_context}

**Görevin:**
1. Bu konu için 3 adet **YouTube videosu** öner
2. Bu konu için 3 adet **PDF döküman veya web sitesi** öner

**Kriterler:**
- Kaynaklar **mutlaka Türkçe** olmalı
- **Lise seviyesine** uygun olmalı (üniversite seviyesi OLMAMALI)
- YouTube için: Eğitim kanalları (Tonguç Akademi, Khan Academy Türkçe, FenBilimleri.net, Eğitim Vadisi vb.)
- PDF/Web için: MEB EBA, edu.tr siteleri, güvenilir eğitim platformları
- Güncel ve kaliteli içerikler olmalı
- Her kaynak konuya **doğrudan ilgili** olmalı

**ÖNEMLİ:** Sadece gerçek, var olan kaynakları öner. URL'leri tahmin etme, gerçek kaynakları araştır.

**Çıktı Formatı (sadece JSON döndür, başka bir şey yazma):**

```json
{{
  "youtube": [
    {{
      "title": "Video başlığı",
      "url": "https://youtube.com/watch?v=...",
      "description": "Videonun içeriği hakkında kısa açıklama",
      "channel_name": "Kanal adı",
      "why_relevant": "Bu videonun neden bu konu için uygun olduğu",
      "estimated_views": "Tahmini izlenme sayısı kategorisi (düşük/orta/yüksek)"
    }}
  ],
  "pdf_and_web": [
    {{
      "title": "Kaynak başlığı",
      "url": "https://...",
      "type": "pdf veya website",
      "description": "Kaynağın içeriği hakkında kısa açıklama",
      "source": "Kaynak platformu (örn: EBA, edu.tr)",
      "why_relevant": "Bu kaynağın neden bu konu için uygun olduğu"
    }}
  ]
}}
```

Şimdi sadece JSON formatında kaynak önerilerini döndür:"""

        return prompt

    def _parse_claude_response(self, response_text: str) -> Dict[str, List[Dict]]:
        """Parse Claude's JSON response"""
        try:
            # Extract JSON from code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

            # Normalize structure
            youtube_resources = data.get("youtube", [])
            pdf_web_resources = data.get("pdf_and_web", [])

            # Split PDF and websites
            pdf_resources = []
            website_resources = []

            for resource in pdf_web_resources:
                if resource.get("type") == "pdf":
                    pdf_resources.append(resource)
                else:
                    website_resources.append(resource)

            return {
                "youtube": youtube_resources[:3],  # Limit to 3
                "pdf": pdf_resources[:3],
                "website": website_resources[:3]
            }

        except json.JSONDecodeError as e:
            print(f"Error parsing Claude response: {e}")
            print(f"Response text: {response_text}")
            return {"youtube": [], "pdf": [], "website": []}

    def calculate_quality_score(
        self,
        resource_data: Dict,
        learning_outcome_match: bool = False
    ) -> float:
        """
        Calculate quality score for a resource (0-100)

        Args:
            resource_data: Resource information from Claude
            learning_outcome_match: Whether resource matches learning outcome

        Returns:
            Quality score (0-100)
        """
        score = 50.0  # Base score

        # Claude relevance (based on why_relevant)
        if resource_data.get("why_relevant"):
            score += 20.0

        # Learning outcome match
        if learning_outcome_match:
            score += 15.0

        # Source quality (for PDF/web)
        source = resource_data.get("source", "").lower()
        if "eba" in source or "edu.tr" in source or "meb" in source:
            score += 10.0
        elif "gov.tr" in source:
            score += 5.0

        # YouTube channel reputation
        channel = resource_data.get("channel_name", "").lower()
        reputable_channels = [
            "tonguç", "khan academy", "fenbilimleri",
            "eğitim vadisi", "eba", "fizikle", "kimya aşkı"
        ]
        if any(ch in channel for ch in reputable_channels):
            score += 10.0

        # Estimated views (for YouTube)
        views = resource_data.get("estimated_views", "").lower()
        if views == "yüksek" or views == "high":
            score += 5.0

        return min(score, 100.0)
