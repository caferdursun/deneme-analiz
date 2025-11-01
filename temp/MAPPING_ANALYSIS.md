# Kazanım-Müfredat Eşleştirme Analizi

**Tarih:** 2025-11-01
**Dosyalar:**
- `learning_outcomes_export.json` (81 kazanım)
- `curriculum_export.json` (686 müfredat konusu)

---

## 🔴 KRİTİK PROBLEMLER

### 1. **Subject Name Uyumsuzluğu**

#### **Learning Outcomes Format:**
```
- "12. SINIF KURS EDEBİYAT YKS"
- "Biyoloji.09"
- "Biyoloji.10"
- "Fizik.10"
- "Fizik.11"
- "Matematik.09"
- "Matematik.10"
- "Matematik.11"
- "Kimya.09"
- "KURS 11-12. SINIF MATEMATİK"
```

#### **Curriculum Format:**
```
- "Türk Dili ve Edebiyatı"
- "Biyoloji"
- "Fizik"
- "Matematik"
- "Kimya"
- "Coğrafya"
- "Tarih"
```

**Problem:**
- Learning outcomes'da **sınıf numarası suffix'i var** (örn: "Matematik.09", "Biyoloji.10")
- Curriculum'da **sadece ders adı var** (örn: "Matematik", "Biyoloji")
- Doğrudan string matching ile eşleştirme **YAPILAMAZ**

**Etki:** ⚠️ **YÜKSEk - Eşleştirme başarısız olacak**

---

### 2. **Türk Dili ve Edebiyatı Uyumsuzluğu**

#### Learning Outcomes:
```json
"subject_name": "12. SINIF KURS EDEBİYAT YKS"
```

#### Curriculum:
```json
"subject_name": "Türk Dili ve Edebiyatı"
```

**Problem:** Tamamen farklı isimlendirme!

**Etki:** ⚠️ **KRİTİK - 45 kazanım (toplam %55) eşleşemeyecek**

---

### 3. **Kategori-Konu Yapısal Uyumsuzluk**

#### Learning Outcomes Yapısı (Düz Liste):
```json
{
  "subject_name": "Matematik.09",
  "category": "SAYILAR VE CEBİR / Denklemler ve Eşitsizlikler",
  "subcategory": "Üslü İfadeler ve Denklemler"
}
```

#### Curriculum Yapısı (Hiyerarşik):
```json
{
  "subject_name": "Matematik",
  "grade": "9",
  "unit_no": 2,
  "unit_name": "Sayılar ve Cebir",
  "topic_name": "Üslü sayılar ve köklü sayılar"
}
```

**Problem:**
- Learning outcomes: `category` ve `subcategory` olarak düz yapı
- Curriculum: `unit` → `topic` olarak hiyerarşik yapı
- İsimlendirme farklılıkları:
  - LO: "SAYILAR VE CEBİR / Denklemler ve Eşitsizlikler"
  - Curr: "Sayılar ve Cebir" (unit_name)
  - LO: "Üslü İfadeler ve Denklemler"
  - Curr: "Üslü sayılar ve köklü sayılar" (topic_name)

**Etki:** ⚠️ **ORTA - Fuzzy matching gerekecek**

---

### 4. **Grade (Sınıf) Bilgisi Eksikliği**

#### Learning Outcomes:
- Grade bilgisi subject_name'e gömülü: `"Matematik.09"` → "9. sınıf"
- Bazılarında yok: `"12. SINIF KURS EDEBİYAT YKS"`

#### Curriculum:
- Grade ayrı bir alan: `"grade": "9"`

**Problem:** Grade bilgisini parse etmek gerekecek

**Etki:** ⚠️ **DÜŞÜK - Regex ile çözülebilir**

---

## 🟡 ORTA SEVİYE PROBLEMLER

### 5. **Büyük/Küçük Harf Tutarsızlığı**

```
Learning Outcomes:
- "ANLATIM BİLGİSİ" (BÜYÜK HARF)
- "CÜMLE ANLAM" (BÜYÜK HARF)
- "PARAGRAF" (BÜYÜK HARF)

Curriculum:
- "Sayma ve Olasılık" (Title Case)
- "Fonksiyonlar" (Normal)
```

**Çözüm:** Case-insensitive matching

---

### 6. **Null Subcategory Değerleri**

```json
{
  "subject_name": "Biyoloji.10",
  "category": "Biyoloji.10",
  "subcategory": null
}
```

45 kazanımın `subcategory` alanı `null`

**Problem:** Eşleştirmede subcategory'ye güvenilemez

---

### 7. **Veri Kalitesi Sorunları**

#### Örnek 1: Duplicate Category
```json
{
  "subject_name": "12. SINIF KURS EDEBİYAT YKS",
  "category": "12. SINIF KURS EDEBİYAT YKS",  // ← subject ile aynı!
  "subcategory": null
}
```

#### Örnek 2: Garip Format
```json
{
  "subject_name": "KURS 11-12. SINIF MATEMATİK",
  "category": "1413315 Eşkenar Üçgen",  // ← Sayısal prefix?
  "subcategory": null
}
```

---

## 🟢 İYİ TARAFLAR

### ✅ Bazı Eşleşmeler Kolay Olacak

#### Örnek 1: Fizik Optik
```
Learning Outcome:
  subject: "Fizik.10"
  category: "OPTİK"
  subcategory: "DÜZLEM AYNA"

Curriculum muhtemelen içerir:
  subject: "Fizik"
  grade: "10"
  unit: "Optik"
  topic: "Düzlem ayna"
```

**Eşleşme:** ✅ İyi (fuzzy matching ile)

---

#### Örnek 2: Matematik Üslü İfadeler
```
Learning Outcome:
  subject: "Matematik.09"
  category: "SAYILAR VE CEBİR / Denklemler ve Eşitsizlikler"
  subcategory: "Üslü İfadeler ve Denklemler"

Curriculum:
  subject: "Matematik"
  grade: "9"
  unit: "Sayılar ve Cebir"
  topic: "Üslü sayılar..."
```

**Eşleşme:** ✅ Makul (regex + fuzzy matching)

---

## 📊 EŞLEŞTİRME BAŞARI TAHMİNİ

### Subject Bazında:

| Subject | LO Sayısı | Eşleşme Zorluğu | Tahmin Başarı |
|---------|-----------|-----------------|---------------|
| 12. SINIF KURS EDEBİYAT YKS | 45 | 🔴 Çok Zor | %30-40% |
| Matematik.09/10/11 | 9 | 🟡 Orta | %70-80% |
| Fizik.10/11 | 9 | 🟡 Orta | %70-80% |
| Biyoloji.09/10/12 | 5 | 🟡 Orta | %60-70% |
| Kimya.09/10/11/12 | 5 | 🟡 Orta | %60-70% |
| Tarih.09 | 4 | 🟡 Orta | %60-70% |
| Diğerleri | 4 | 🟢 Kolay | %80-90% |

**Genel Başarı Tahmini:** %55-65%

---

## 🛠️ ÖNERİLEN EŞLEŞTİRME STRATEJİSİ

### Adım 1: Subject Name Normalization
```python
def normalize_subject(subject_name):
    # "Matematik.09" → "Matematik", "9"
    # "12. SINIF KURS EDEBİYAT YKS" → "Türk Dili ve Edebiyatı", "12"

    mapping = {
        "12. SINIF KURS EDEBİYAT YKS": "Türk Dili ve Edebiyatı",
        "KURS 11-12. SINIF MATEMATİK": "Matematik"
    }

    # Check mapping first
    if subject_name in mapping:
        return mapping[subject_name], extract_grade(subject_name)

    # Extract pattern: "Subject.Grade"
    match = re.match(r"(.+?)\.(\d+)", subject_name)
    if match:
        return match.group(1), match.group(2)

    return subject_name, None
```

### Adım 2: Multi-Level Fuzzy Matching
```python
from fuzzywuzzy import fuzz

def match_learning_outcome_to_curriculum(lo, curriculum):
    # 1. Match subject + grade
    subject, grade = normalize_subject(lo['subject_name'])

    candidates = [
        c for c in curriculum
        if c['subject_name'] == subject and c['grade'] == grade
    ]

    # 2. Match unit (from category)
    unit_scores = [
        (topic, fuzz.ratio(lo['category'], topic['unit_name']))
        for candidate in candidates
        for topic in candidate['topics']
    ]

    # 3. Match topic (from subcategory)
    if lo['subcategory']:
        topic_scores = [
            (topic, fuzz.ratio(lo['subcategory'], topic['topic_name']))
            for topic, _ in unit_scores
        ]

    # 4. Return best match above threshold (>= 70)
    best = max(scores, key=lambda x: x[1])
    if best[1] >= 70:
        return best[0]

    return None
```

### Adım 3: Manual Mapping for Edge Cases
```python
MANUAL_MAPPINGS = {
    # Edebiyat special cases
    ("12. SINIF KURS EDEBİYAT YKS", "ANLATIM BİLGİSİ"):
        ("Türk Dili ve Edebiyatı", "12", "Dil Bilgisi", "Anlatım"),

    # Matematik special cases
    ("KURS 11-12. SINIF MATEMATİK", "1413315 Eşkenar Üçgen"):
        ("Matematik", "11", "Geometri", "Üçgenler"),
}
```

---

## 🎯 SONUÇ VE ÖNERİLER

### ✅ Eşleştirme Mümkün Ama Dikkat Gerekli:

1. **Subject name normalization** şart
2. **Fuzzy matching** kullanılmalı (fuzzywuzzy veya rapidfuzz)
3. **Manual mapping** bazı edge case'ler için gerekli
4. **Grade extraction** için regex pattern
5. **Case-insensitive** karşılaştırma
6. **Null handling** için fallback stratejisi

### ⚠️ Riskler:

1. **%35-45 kazanım eşleşemeyebilir** (özellikle Edebiyat)
2. **Yanlış eşleşmeler** (false positives) olabilir
3. **Manuel düzeltme** gerekebilir

### 💡 Öneriler:

1. **Önce test et:** 10-15 kazanımla manual matching yap, başarı oranını gör
2. **Threshold ayarla:** Fuzzy matching için 70-80 arası threshold dene
3. **Logging ekle:** Hangi eşleşmelerin zayıf olduğunu kaydet
4. **UI'da göster:** Kullanıcıya eşleşme skorunu göster, düzeltme imkanı ver
5. **Veri temizliği:** Learning outcomes verisi gelecekte daha temiz gelmeli

---

## 📋 ÖRNEK EŞLEŞTİRMELER

### ✅ Başarılı Olabilecek:

```
LO: "Fizik.10" + "OPTİK" + "DÜZLEM AYNA"
→ Curr: "Fizik" + "10" + "Optik" + "Düzlem ayna"
Score: ~85%
```

```
LO: "Matematik.09" + "SAYILAR VE CEBİR" + "Üslü İfadeler"
→ Curr: "Matematik" + "9" + "Sayılar ve Cebir" + "Üslü sayılar"
Score: ~75%
```

### ⚠️ Zor Olacak:

```
LO: "12. SINIF KURS EDEBİYAT YKS" + "PARAGRAF" + "Paragrafta Konu"
→ Curr: "Türk Dili ve Edebiyatı" + ??? + ??? + ???
Score: ~40% (manual mapping gerekir)
```

```
LO: "KURS 11-12. SINIF MATEMATİK" + "1413315 Eşkenar Üçgen"
→ Curr: "Matematik" + ??? + "Geometri" + "Üçgenler"
Score: ~50% (garip format)
```

---

## 🚀 UYGULAMA PLANI

### Phase 1: Basit String Matching (1-2 saat)
- Subject name cleanup
- Grade extraction
- Exact match (beklenen başarı: %20-30)

### Phase 2: Fuzzy Matching (2-3 saat)
- fuzzywuzzy entegrasyonu
- Unit/topic matching
- Threshold tuning
- Beklenen başarı: %50-65

### Phase 3: Manual Mappings (2-3 saat)
- Edge case'leri tespit et
- Manual mapping dictionary oluştur
- Beklenen başarı: %70-80

### Phase 4: UI & Feedback (3-4 saat)
- Eşleşme skorunu göster
- Kullanıcı düzeltme arayüzü
- Final başarı: %85-95 (user input ile)

---

**SONUÇ:** Eşleştirme problemi var ama çözülebilir! Fuzzy matching + manual mappings + user feedback kombinasyonu ile %85+ başarı mümkün.
