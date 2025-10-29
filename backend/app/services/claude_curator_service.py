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
                max_tokens=16000,
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

        prompt = f"""Sen Türkiye'de **TYT/AYT/YKS hazırlık** için eğitim kaynağı küratörüsün. Görevin yüksek kaliteli, doğrulanmış kaynaklar önermek.

**Konu:** {subject} - {topic}
{outcome_context}

**Sınav Bağlamı:**
- TYT (Temel Yeterlilik Testi): 1. oturum - Matematik, Türkçe, Fen, Sosyal
- AYT (Alan Yeterlilik Testi): 2. oturum - Alan dersleri (Mat, Fen, Sözel)
- YKS: Yükseköğretim Kurumları Sınavı (TYT + AYT)

**Görevin:**
1. Bu konu için 3 adet **YouTube videosu** öner (TYT/AYT/YKS odaklı)
2. Bu konu için 3 adet **direkt erişilebilir web sayfası veya PDF** öner

**KALİTE KRİTERLERİ (ZORUNLU):**

**YouTube için:**
- Video başlığında konuyla DOĞRUDAN ilgili olmalı
- Kanal tanınmış bir TYT/AYT kanalı olmalı (Tonguç, Khan Academy TR, FenBilimleri, Eğitim Vadisi, Fizikle, Hocalara Geldik, vb.)
- Video süresi 5-30 dakika arası (çok kısa veya çok uzun videolar önerme)
- Başlıkta TYT, AYT veya YKS geçmesi ZORUNLU
- Video içeriği SADECE bu konuya odaklanmalı (genel konu anlatımı değil)
- Eğer bu konuya özel bir video bulamıyorsan, HİÇ ÖNERİ YAPMA (boş liste döndür)

**PDF/Web için:**
- **KESİNLİKLE** ana sayfa önerme (örn: tonguçakademi.com YANLIŞ)
- Sayfa içeriği SADECE bu konuya odaklanmalı
- Login/kayıt gerektiren siteler YASAK (MEB EBA, Morpa Kampüs, vb.)
- PDF ise, doğrudan .pdf uzantılı link ver
- Web sayfası ise, konuya özel bir makale/ders sayfası olmalı
- Eğer bu konuya özel bir kaynak bulamıyorsan, HİÇ ÖNERİ YAPMA (boş liste döndür)

**Güvenilir Platformlar:**
- YouTube: Tonguç Akademi, Khan Academy Türkçe, FenBilimleri.net, Eğitim Vadisi, Fizikle, Hocalara Geldik, Kimya Aşkı, Biyoloji Portalı
- Web: Khan Academy TR, FenBilimleri.net, AçıkLise, Biyoloji Portalı, edu.tr alan adlı siteler
- PDF: Üniversite ders notları, açık eğitim materyalleri

**YASAKLAR (ÖNERİRSEN YANLIŞ OLUR):**
❌ MEB EBA ve login gerektiren siteler
❌ Ana sayfalar ve genel içerikler
❌ Konuyla DOLAYLI ilgili kaynaklar
❌ Üniversite seviyesi ileri düzey içerikler
❌ Ticari kurs siteleri (Udemy, Udacity vb.)
❌ Tahmin edilen/uydurulan URL'ler
❌ Çok eski (5+ yıl önce) içerikler

**KALİTE KONTROLÜ:**
Her öneri için kendin şu soruları sor:
1. Bu kaynak SADECE bu konuyu mu anlatıyor? (Evet olmalı)
2. Lise öğrencisi bu kaynaktan faydalanabilir mi? (Evet olmalı)
3. URL'i biliyorum, tahmin etmiyorum? (Evet olmalı)
4. Kaynak TYT/AYT hazırlığı için mi üretilmiş? (Evet olmalı)

Eğer herhangi bir sorunun cevabı HAYIR ise, o kaynağı ÖNERME!

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

        # Source quality (for PDF/web) - open access, no login required
        source = resource_data.get("source", "").lower()
        url = resource_data.get("url", "").lower()

        # Bonus for trusted open education platforms
        if any(platform in source or platform in url for platform in [
            "khan academy", "fenbilimleri", "biyoloji portalı",
            "açıklise", "fizikle", "kimya aşkı"
        ]):
            score += 10.0
        elif "edu.tr" in url and "eba" not in url:  # edu.tr but not EBA
            score += 5.0

        # YouTube channel reputation
        channel = resource_data.get("channel_name", "").lower()
        reputable_channels = [
            "tonguç", "khan academy", "fenbilimleri",
            "eğitim vadisi", "fizikle", "kimya aşkı", "biyoloji portalı",
            "hocalara geldik", "uni", "matematik", "fizik", "kimya", "biyoloji"
        ]
        if any(ch in channel for ch in reputable_channels):
            score += 10.0

        # Estimated views (for YouTube)
        views = resource_data.get("estimated_views", "").lower()
        if views == "yüksek" or views == "high":
            score += 5.0

        return min(score, 100.0)

    def generate_video_search_keywords(
        self,
        subject: str,
        topic: str,
        description: Optional[str] = None,
        learning_outcome: Optional[str] = None
    ) -> List[str]:
        """
        Çalışma kartı içeriğinden 3-5 akıllı search keyword üret

        Args:
            subject: Ders adı (örn: "Fizik", "Matematik")
            topic: Konu başlığı (örn: "Prizmalar", "Türev")
            description: Konu açıklaması (opsiyonel)
            learning_outcome: Kazanım metni (opsiyonel)

        Returns:
            List of 3-5 search keywords optimized for YouTube

        Example Input:
            subject: "Fizik"
            topic: "Prizmalar"
            description: "Işık kırılması ve renk ayrışması"

        Example Output:
            ["prizmalar konu anlatımı",
             "prizma ışık kırılması soru çözümü",
             "fizik prizma örnekleri",
             "ayt fizik prizmalar",
             "ışık renk ayrışması prizma"]
        """
        # Build context
        context_parts = [f"Ders: {subject}", f"Konu: {topic}"]

        if description:
            context_parts.append(f"Açıklama: {description}")

        if learning_outcome:
            context_parts.append(f"Kazanım: {learning_outcome}")

        context = "\n".join(context_parts)

        # Create prompt
        prompt = f"""Sen bir TYT/AYT üniversite sınavı hazırlık uzmanısın. Görevin, öğrencilerin YouTube'da eğitim videoları ararken kullanacakları en etkili arama terimlerini önermek.

Aşağıdaki konu için 3-5 farklı YouTube arama terimi öner:

{context}

ÖNEMLİ KURALLAR:
1. Her keyword farklı bir bakış açısından olmalı (konu anlatımı, soru çözümü, örnek, özet, vb.)
2. Türkçe eğitim içeriği için optimize edilmiş olmalı
3. "TYT", "AYT", ders adı gibi bağlam kelimeler içermeli
4. Gerçek öğrencilerin arama şekillerini taklit et
5. Çok genel veya çok spesifik olma - orta seviyede tut

Sadece JSON formatında yanıt ver:
{{"keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]}}

Her keyword maksimum 6 kelime olmalı."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,  # Creativity için
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            content = response.content[0].text.strip()

            # Extract JSON from response
            if "```json" in content:
                # Remove markdown code blocks
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # Parse JSON
            data = json.loads(content)
            keywords = data.get("keywords", [])

            # Validate keywords
            if not keywords or len(keywords) < 3:
                # Fallback to basic keywords
                return self._generate_fallback_keywords(subject, topic)

            # Return max 5 keywords
            print(f"✅ Claude generated {len(keywords)} keywords for {subject}/{topic}")
            return keywords[:5]

        except Exception as e:
            print(f"Claude keyword generation error: {e}")
            # Fallback to basic keywords
            return self._generate_fallback_keywords(subject, topic)

    def _generate_fallback_keywords(self, subject: str, topic: str) -> List[str]:
        """
        Generate basic fallback keywords if Claude API fails

        Args:
            subject: Subject name
            topic: Topic name

        Returns:
            List of 3-5 basic keywords
        """
        print(f"⚠️ Using fallback keywords for {subject}/{topic}")
        # Basic keyword templates
        keywords = [
            f"{topic} konu anlatımı",
            f"{topic} {subject} soru çözümü",
            f"{subject} {topic} AYT",
            f"{topic} TYT {subject}",
            f"{subject} {topic} örnekleri"
        ]

        return keywords[:5]
