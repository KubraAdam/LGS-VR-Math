# 🏗️ VR Entegrasyon Mimarisi

## Genel Bakış

Sistem 3 ana katmandan oluşur:

```
┌─────────────────────────────────────┐
│   Frontend (WebAR - Three.js)       │
│   - Kullanıcı arayüzü              │
│   - 3D sahne renderlama            │
│   - Etkileşim yönetimi              │
└──────────────┬──────────────────────┘
               │ HTTP REST API
┌──────────────▼──────────────────────┐
│   Backend (FastAPI)                 │
│   - API endpoints                   │
│   - Model + VR entegrasyonu         │
│   - CORS yönetimi                   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│ ML Model    │  │ VR Engine   │
│ Predictor   │  │ Decision     │
│             │  │             │
│ - BERT      │  │ - Karar      │
│ - Inference │  │ - Sahne      │
│             │  │   seçimi    │
└─────────────┘  └─────────────┘
```

## Modül Yapısı

### 1. VR Engine (`vr_engine/`)

**Sorumluluk:** VR açılacak mı, hangi sahne kullanılacak karar verir.

**Karar Kriterleri:**
- ✅ `gorsel_bagimli = "bagimli"` → VR açılır
- ✅ `alt_konu` in VR_ENABLED_TOPICS → VR açılır
- ✅ `soru_tipi` in VR_ENABLED_TYPES → VR açılır

**Çıktı:**
```python
{
    "activated": True,
    "scene_type": "area_geometry",
    "mode": "guided",
    "config": {...}
}
```

### 2. Model Inference (`model_inference/`)

**Sorumluluk:** Eğitilmiş BERT modelini yükler ve tahmin yapar.

**İşlem Akışı:**
1. Model ve tokenizer yükle
2. Soru metnini formatla
3. Tokenize et
4. Model tahmini yap
5. Etiketleri decode et

**Çıktı:**
```python
{
    "alt_konu": "Alan ve Geometri",
    "soru_tipi": "Problem",
    "confidence": {...}
}
```

### 3. API (`api/`)

**Sorumluluk:** Frontend ve backend arasında köprü.

**Endpoints:**
- `POST /predict` - Ana endpoint (model + VR)
- `POST /vr-config` - Sadece VR config
- `GET /health` - Sistem durumu

**İşlem Akışı:**
```
Request → Model Predict → VR Decision → Response
```

### 4. Frontend (`frontend/`)

**Sorumluluk:** Kullanıcı arayüzü ve 3D görselleştirme.

**Bileşenler:**
- `index.html` - Ana arayüz
- `app.js` - API entegrasyonu
- `vr_scenes/` - 3D sahne implementasyonları

**VR Sahne Tipleri:**
- `AreaGeometryScene` - Alan ve geometri
- `AreaPerimeterScene` - Alan-çevre
- `NumberLineScene` - Sayı doğrusu
- `ComparisonScene` - Karşılaştırma

## Veri Akışı

### Senaryo: Öğrenci Soru Girdi

```
1. Frontend: Soru metni + seçenekler
   ↓
2. API: /predict endpoint
   ↓
3. Model Predictor: BERT tahmini
   ↓
4. VR Engine: Karar + sahne seçimi
   ↓
5. API: JSON response
   ↓
6. Frontend: VR sahnesi yükle
   ↓
7. Three.js: 3D render
```

## VR Karar Matrisi

| Alt Konu | Soru Tipi | Görsel | VR Açılır? | Sahne |
|----------|-----------|--------|------------|-------|
| Alan ve Geometri | Problem | Bağımlı | ✅ | area_geometry |
| Alan ve Geometri | Hesaplama | - | ⚠️ Opsiyonel | - |
| Yaklaşık Değer | Yorum | - | ✅ | number_line |
| Karşılaştırma | Problem | - | ✅ | comparison |
| Denklemler | Hesaplama | - | ❌ | - |

## Sahne Konfigürasyonları

### Area Geometry
```json
{
    "shapes": ["kare", "dikdörtgen", "üçgen"],
    "draggable_edges": true,
    "live_area_calculation": true,
    "show_sqrt_simplification": true
}
```

### Number Line
```json
{
    "highlight_nearest_integers": true,
    "show_approximation": true,
    "interactive_point": true,
    "number_range": [-10, 10]
}
```

### Comparison
```json
{
    "bar_chart_style": true,
    "height_represents_value": true,
    "interactive_bars": true,
    "show_comparison_lines": true
}
```

## Genişletilebilirlik

### Yeni Sahne Ekleme

1. `vr_scenes/` klasörüne yeni scene dosyası ekle
2. `BaseScene`'den türet
3. `scene_manager.js`'e ekle
4. `vr_decision.py`'de mapping ekle

### Yeni Alt Konu Desteği

1. `vr_decision.py` → `VR_ENABLED_TOPICS` ekle
2. `TOPIC_TO_SCENE` mapping ekle
3. Gerekirse yeni sahne oluştur

### Unity Entegrasyonu

1. Unity projesi oluştur
2. API'den VR config al
3. Unity sahne yöneticisi yaz
4. Frontend'de Unity WebGL embed et

## Performans Notları

- **Model Yükleme:** İlk tahmin yavaş (~2-3 saniye)
- **VR Render:** 60 FPS hedeflenir
- **API Response:** ~100-300ms (model dahil)
- **Sahne Yükleme:** ~500ms-1s

## Güvenlik

- CORS: Development'ta `*`, production'da spesifik origin
- Model dosyaları: `.gitignore`'da
- API: Rate limiting eklenebilir
- Input validation: Pydantic modelleri

## Test Stratejisi

1. **Unit Tests:** Her modül ayrı test
2. **Integration Tests:** `test_integration.py`
3. **E2E Tests:** Frontend + Backend birlikte
4. **Performance Tests:** API response time

