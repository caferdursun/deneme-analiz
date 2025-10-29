# YouTube Kaynak Önerme Algoritması - Implementation Plan

## Proje Durumu: Phase 3 + Enhanced Filtering Tamamlandı ✅

### Phase 1 Tamamlandı (Commit: 974234a)
- ✅ YouTubeChannel model oluşturuldu
- ✅ Database migration başarıyla uygulandı (`youtube_channels` tablosu)
- ✅ Model integration tamamlandı

### Phase 2 Tamamlandı (Commit: 5d1b22e)
- ✅ search_channels() metodu eklendi (kanal arama, abone sayısına göre sıralama)
- ✅ get_channel_details() metodu eklendi (kanal istatistikleri)
- ✅ search_videos_in_channel() metodu eklendi (kanal içi video arama + filtreleme)
- ✅ verify_video_availability() metodu eklendi (video erişilebilirlik kontrolü)
- ✅ isodate dependency eklendi (ISO 8601 duration parsing)
- ✅ Test scripts yazıldı ve başarıyla çalıştırıldı
- ✅ Tonguç Akademi ile test edildi (3.8M subscriber)

### Phase 3 Tamamlandı (Commit: 98b7d18)
- ✅ generate_video_search_keywords() metodu eklendi (Claude AI ile keyword üretimi)
- ✅ AI-powered 3-5 akıllı keyword üretimi
- ✅ Fallback template-based keywords
- ✅ Test edildi: 5 farklı ders/konu kombinasyonu

### Phase 4 Tamamlandı (Partial - Commit: 98b7d18)
- ✅ ChannelService oluşturuldu (tam CRUD operasyonları)
- ✅ discover_channels_for_subject() - Otomatik kanal keşfi
- ✅ get_trusted_channels() - Trust score'a göre filtreleme
- ✅ refresh_channel_stats() - Kanal istatistik güncelleme
- ✅ add_channel_manually() - Manuel kanal ekleme
- ✅ 24 kanal veritabanına eklendi (5 ders, toplam 24 kanal)

### Enhanced Filtering System (Commit: 98b7d18) - CRITICAL FIX
- ✅ Video filtreleri güçlendirildi (silinen/erişilemeyen videoları önler)
- ✅ Engagement-based scoring eklendi (like_ratio * sqrt(views))
- ✅ Katmanlı kalite kontrolleri:
  - Duration: 5-30 dakika
  - Views: >5K
  - Age: 2 hafta - 3 yıl
  - Like ratio: >0.3%
  - Comment count: >5
- ✅ verify_video_availability() yaş kontrolü eklendi
- ✅ Test edildi: Fizik/Prizmalar konusunda başarılı

---

## Kalan Implementation Phases

### **Phase 2: YouTube Service Enhancement** (~200 lines)
**Dosya:** `/root/projects/deneme-analiz/backend/app/services/youtube_service.py`

**Eklenecek 4 Metod:**

```python
def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
    """
    YouTube'da kanal ara, abone sayısına göre sırala

    Args:
        query: Arama kelimesi (örn: "Matematik AYT TYT")
        max_results: Max kanal sayısı

    Returns:
        List of dicts with: channel_id, channel_name, subscriber_count,
                           video_count, thumbnail_url, description

    API Call: search?part=snippet&type=channel&order=viewCount&q={query}
    Follow-up: channels?part=statistics,snippet&id={channel_ids}
    """

def get_channel_details(self, channel_id: str) -> Dict:
    """
    Kanal istatistiklerini getir

    Returns: channel_name, subscriber_count, video_count, view_count,
             thumbnail_url, description, custom_url

    API Call: channels?part=statistics,snippet&id={channel_id}
    """

def search_videos_in_channel(
    self,
    channel_id: str,
    query: str,
    max_results: int = 3
) -> List[Dict]:
    """
    Belirli bir kanalda video ara

    Filters:
        - Duration: 5-30 minutes
        - View count: >5000
        - Published: last 3 years

    API Call: search?part=snippet&channelId={channel_id}&q={query}&type=video
    Follow-up: videos?part=statistics,contentDetails&id={video_ids}

    Returns: video_id, title, description, thumbnail_url, channel_name,
             view_count, like_count, duration, published_at
    """

def verify_video_availability(self, video_id: str) -> bool:
    """
    Video var mı, oynatılabilir mi kontrol et

    Checks:
        - Video exists
        - embeddable: true
        - Not private/deleted

    API Call: videos?part=status&id={video_id}
    Returns: True if available and embeddable
    """
```

**API Key Check:**
- `YOUTUBE_API_KEY` environment variable kullan
- Fallback: Eğer key yoksa, eski static resources döndür

---

### **Phase 3: Claude Keyword Generation** (~100 lines)
**Dosya:** `/root/projects/deneme-analiz/backend/app/services/claude_curator_service.py`

**Eklenecek Metod:**

```python
def generate_video_search_keywords(
    self,
    subject: str,
    topic: str,
    description: Optional[str] = None,
    learning_outcome: Optional[str] = None
) -> List[str]:
    """
    Çalışma kartı içeriğinden 3-5 akıllı search keyword üret

    Claude Prompt:
    - "Sen bir TYT/AYT sınav hazırlık uzmanısın"
    - "Öğrencilerin YouTube'da arayacağı keyword'ler öner"
    - "Konuya uygun, farklı açılardan 3-5 arama terimi"
    - Format: JSON {"keywords": ["...", "...", "..."]}

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
```

**Model:** claude-sonnet-4-5-20250929
**Max Tokens:** 1000 (keywords için yeterli)
**Temperature:** 0.7 (creativity için)

---

### **Phase 4: Channel Service** (~250 lines)
**Yeni Dosya:** `/root/projects/deneme-analiz/backend/app/services/channel_service.py`

**Class: ChannelService**

```python
class ChannelService:
    def __init__(self, db: Session):
        self.db = db
        self.youtube_service = YouTubeService()

    def discover_channels_for_subject(
        self,
        subject: str,
        force_refresh: bool = False
    ) -> List[YouTubeChannel]:
        """
        Bir ders için kanalları otomatik keşfet

        Algorithm:
        1. Check if channels exist in DB for this subject
        2. If exists and not force_refresh, return from DB
        3. Else, search YouTube: "{subject} AYT TYT"
        4. Get top 5-10 channels by subscriber count
        5. Save to database with trust_score=70.0, discovered_via='auto_search'
        6. Return channels

        Returns: List of YouTubeChannel objects
        """

    def get_trusted_channels(
        self,
        subject: str,
        min_trust_score: float = 70.0,
        limit: int = 5,
        is_active: bool = True
    ) -> List[YouTubeChannel]:
        """
        Bir ders için güvenilir kanalları getir

        Query:
            WHERE subject_name = {subject}
            AND trust_score >= {min_trust_score}
            AND is_active = {is_active}
            ORDER BY subscriber_count DESC
            LIMIT {limit}
        """

    def refresh_channel_stats(self, channel_id: str) -> YouTubeChannel:
        """
        Kanal istatistiklerini güncelle

        Steps:
        1. Get channel from DB
        2. Fetch latest stats from YouTube API
        3. Update: subscriber_count, video_count, view_count, last_updated
        4. Save to DB
        5. Return updated channel
        """

    def add_channel_manually(
        self,
        channel_id: str,
        subject: str,
        trust_score: float = 80.0,
        notes: Optional[str] = None
    ) -> YouTubeChannel:
        """
        Kanal manüel olarak ekle

        Steps:
        1. Fetch channel details from YouTube
        2. Create YouTubeChannel object
        3. Set discovered_via='manual_add'
        4. Save to DB
        5. Return channel
        """

    def deactivate_channel(self, channel_id: str) -> bool:
        """
        Kanalı deaktif et (soft delete)

        Update: is_active = False
        """

    def get_all_subjects_with_channels(self) -> List[str]:
        """
        Kanalı olan derslerin listesi

        SELECT DISTINCT subject_name FROM youtube_channels
        WHERE is_active = 1
        """
```

---

### **Phase 5: ResourceService Refactor** (~300 lines)
**Dosya:** `/root/projects/deneme-analiz/backend/app/services/resource_service.py`

**Yeni `curate_resources_for_study_item()` Implementation:**

```python
def curate_resources_for_study_item(
    self,
    study_plan_item_id: str,
    exclude_urls: Optional[List[str]] = None
) -> Dict[str, List[Resource]]:
    """
    NEW ALGORITHM - Channel-based video curation
    """
    from app.services.channel_service import ChannelService

    # 1. Get study plan item
    item = self.db.query(StudyPlanItem).get(study_plan_item_id)
    if not item:
        return {"youtube": [], "pdf": [], "website": []}

    # 2. Get/Discover trusted channels
    channel_service = ChannelService(self.db)
    channels = channel_service.get_trusted_channels(
        subject=item.subject_name,
        limit=5
    )

    # Auto-discover if no channels found
    if not channels:
        channels = channel_service.discover_channels_for_subject(
            subject=item.subject_name
        )

    # 3. Generate search keywords using Claude
    keywords = self.curator_service.generate_video_search_keywords(
        subject=item.subject_name,
        topic=item.topic,
        description=item.description,
        learning_outcome=self._get_learning_outcome_text(item)
    )

    # 4. Search videos in each channel with each keyword
    all_videos = []
    for channel in channels:
        for keyword in keywords:
            videos = self.youtube_service.search_videos_in_channel(
                channel_id=channel.channel_id,
                query=keyword,
                max_results=3
            )

            # 5. Verify availability
            verified_videos = [
                v for v in videos
                if self.youtube_service.verify_video_availability(v['video_id'])
            ]

            # Add channel trust score to each video
            for video in verified_videos:
                video['channel_trust_score'] = channel.trust_score

            all_videos.extend(verified_videos)

    # 6. Remove duplicates by video_id
    unique_videos = self._deduplicate_videos(all_videos)

    # 7. Score videos
    scored_videos = []
    for video in unique_videos:
        score = self._calculate_video_score(
            video=video,
            topic=item.topic,
            keywords=keywords
        )
        video['score'] = score
        scored_videos.append(video)

    # 8. Sort by score and filter
    top_videos = sorted(
        [v for v in scored_videos if v['score'] >= 55.0],
        key=lambda x: x['score'],
        reverse=True
    )[:10]

    # 9. Filter out blacklisted/excluded URLs
    filtered_videos = self._filter_videos(top_videos, exclude_urls)

    # 10. Create Resource objects
    resources = []
    for video in filtered_videos:
        resource = self._create_resource_from_video(
            video_data=video,
            subject=item.subject_name,
            topic=item.topic,
            learning_outcome_ids=None
        )
        if resource:
            resources.append(resource)

    return {"youtube": resources, "pdf": [], "website": []}


def _calculate_video_score(
    self,
    video: Dict,
    topic: str,
    keywords: List[str]
) -> float:
    """
    NEW SCORING ALGORITHM

    Base: 50
    + Title relevance (keyword match): +15
    + Description relevance (topic match): +10
    + View count (5k-500k sweet spot): +10
    + Duration (5-30 min): +10
    + Channel trust score: +15 (max)
    + Recency (< 3 years): +5

    Max: 100
    """
    score = 50.0

    # Title relevance
    title_lower = video.get('title', '').lower()
    if any(kw.lower() in title_lower for kw in keywords):
        score += 15

    # Description relevance
    desc_lower = video.get('description', '').lower()
    if topic.lower() in desc_lower:
        score += 10

    # View count sweet spot
    views = video.get('view_count', 0)
    if 5000 < views < 500000:
        score += 10
    elif views >= 500000:
        score += 5  # Too viral might not be educational

    # Duration (convert from ISO 8601)
    duration_seconds = video.get('duration_seconds', 0)
    duration_minutes = duration_seconds / 60
    if 5 <= duration_minutes <= 30:
        score += 10

    # Channel trust score (0-100 → 0-15 points)
    channel_trust = video.get('channel_trust_score', 70.0)
    score += (channel_trust / 100) * 15

    # Recency
    published_years_ago = video.get('published_years_ago', 10)
    if published_years_ago <= 3:
        score += 5

    return min(score, 100.0)


def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
    """Remove duplicate videos by video_id"""
    seen = set()
    unique = []
    for video in videos:
        vid_id = video.get('video_id')
        if vid_id and vid_id not in seen:
            seen.add(vid_id)
            unique.append(video)
    return unique


def _filter_videos(
    self,
    videos: List[Dict],
    exclude_urls: Optional[List[str]]
) -> List[Dict]:
    """Filter blacklisted and excluded URLs"""
    # Get blacklisted URLs
    blacklisted = self.db.query(ResourceBlacklist.url).all()
    blacklisted_urls = {url[0] for url in blacklisted}

    # Combine with exclude list
    if exclude_urls:
        blacklisted_urls.update(exclude_urls)

    # Filter
    return [
        v for v in videos
        if v.get('url') not in blacklisted_urls
    ]


def _get_learning_outcome_text(self, item: StudyPlanItem) -> Optional[str]:
    """Get learning outcome description if item has recommendation_id"""
    if not item.recommendation_id:
        return None

    rec = self.db.query(Recommendation).get(item.recommendation_id)
    if not rec or not rec.learning_outcome_ids:
        return None

    lo = self.db.query(LearningOutcome).get(rec.learning_outcome_ids[0])
    return lo.outcome_description if lo else None


def _create_resource_from_video(
    self,
    video_data: Dict,
    subject: str,
    topic: str,
    learning_outcome_ids: Optional[List[str]]
) -> Optional[Resource]:
    """Create Resource object from video data"""
    # Similar to existing _create_curated_resource
    # but uses real video data instead of Claude's suggestions
    ...
```

---

### **Phase 6: Testing**

**Test Cases:**

1. **Channel Discovery Test:**
   ```python
   # Test for Matematik
   channel_service.discover_channels_for_subject("Matematik")
   # Should find: Tonguç Akademi, Khan Academy TR, etc.
   ```

2. **Keyword Generation Test:**
   ```python
   # Test for "Prizmalar" topic
   keywords = claude_curator.generate_video_search_keywords(
       subject="Fizik",
       topic="Prizmalar"
   )
   # Expected: ["prizmalar konu anlatımı", ...]
   ```

3. **Video Search Test:**
   ```python
   # Search in specific channel
   videos = youtube_service.search_videos_in_channel(
       channel_id="UC...",
       query="prizmalar",
       max_results=3
   )
   # Should return relevant videos
   ```

4. **End-to-End Test:**
   ```python
   # Curate resources for study item
   resources = resource_service.curate_resources_for_study_item(
       study_plan_item_id="..."
   )
   # Should return 5-10 high-quality YouTube videos
   ```

---

## Environment Requirements

**YouTube API Key:**
```bash
# .env file
YOUTUBE_API_KEY=your_api_key_here
```

**Quota Considerations:**
- Channel search: 100 units per call
- Video details: 1 unit per video
- Estimated: ~200-300 units per resource curation request
- Daily quota: 10,000 units (default free tier)

---

## Implementation Order

1. ✅ Phase 1: Database (COMPLETED - Commit: 974234a)
2. ✅ Phase 2: YouTubeService (COMPLETED - Commit: 5d1b22e)
3. ✅ Phase 3: ClaudeCuratorService (COMPLETED - Commit: 98b7d18)
4. ✅ Phase 4: ChannelService (COMPLETED - Commit: 98b7d18)
5. ⏳ Phase 5: ResourceService Refactor (NEXT)
6. ⏳ Phase 6: Testing

**Estimated Time:** 1-2 hours for remaining phases

---

## Reference Files

**Test Script (Prototype):**
`/root/projects/deneme-analiz/backend/test_youtube_search.py`

**Prompts Reference:**
`/root/projects/deneme-analiz/prompts.txt` (lines 95-98)

**Current Commits:**
- `974234a` - Phase 1: YouTubeChannel model
- `623bedb` - Move resource system to study plans
- `258dac3` - Add percentage stats to learning outcomes

---

## Next Session TODO

1. Implement YouTubeService enhancements (4 methods)
2. Add Claude keyword generation
3. Create ChannelService
4. Refactor ResourceService.curate_resources_for_study_item()
5. Test with real YouTube API
6. Commit and deploy

**Start Command for Next Session:**
```bash
cd /root/projects/deneme-analiz/backend
source venv/bin/activate
# Read IMPLEMENTATION_PLAN.md
# Start with Phase 2
```
