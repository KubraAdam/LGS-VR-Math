# VR Integration Module - LGS Math Learning System

Bu modül, ML modeli ile VR/AR görselleştirmelerini entegre eder.

## 📁 Klasör Yapısı

```
vr_integration/
├── vr_engine/          # VR karar motoru
│   └── vr_decision.py  # VR açılma kararı ve sahne seçimi
├── model_inference/    # Model tahmin servisi
│   └── predictor.py    # BERT model yükleme ve tahmin
├── api/                # FastAPI backend
│   └── main.py         # REST API endpoints
├── frontend/           # WebAR frontend
│   ├── index.html      # Ana arayüz
│   ├── app.js          # API entegrasyonu
│   └── vr_scenes/      # VR sahne implementasyonları
│       ├── scene_manager.js
│       ├── area_geometry_scene.js
│       ├── area_perimeter_scene.js
│       ├── number_line_scene.js
│       └── comparison_scene.js
└── requirements.txt    # Python bağımlılıkları
```

## 🚀 Kurulum

### 1. Python Bağımlılıkları

```bash
pip install -r requirements.txt
```

### 2. Model Kontrolü

Model dosyalarının şu konumda olduğundan emin olun:
- `modeleğitimi/model_checkpoint/best_model.bin`
- `modeleğitimi/model_checkpoint/label_map.json`

### 3. API'yi Başlat

```bash
cd vr_integration/api
python main.py
```

API `http://localhost:8000` adresinde çalışacak.

### 4. Frontend'i Aç

`vr_integration/frontend/index.html` dosyasını tarayıcıda açın.

**Not:** Frontend için bir web sunucusu kullanmanız önerilir (CORS için):

```bash
# Python ile basit sunucu
cd vr_integration/frontend
python -m http.server 8080
```

Sonra `http://localhost:8080` adresine gidin.

## 📡 API Endpoints

### `POST /predict`

Soru metninden tahmin yapar ve VR konfigürasyonu döner.

**Request:**
```json
{
  "soru_metin": "Alanı 144 cm² olan karenin çevresi kaç cm'dir?",
  "secenekler": {
    "A": "24",
    "B": "48",
    "C": "36",
    "D": "12"
  },
  "gorsel_bagimli": "bagimli"
}
```

**Response:**
```json
{
  "alt_konu": "Alan ve Geometri",
  "soru_tipi": "Problem",
  "confidence": {
    "alt_konu": 0.95,
    "soru_tipi": 0.88
  },
  "vr_config": {
    "activated": true,
    "scene_type": "area_geometry",
    "mode": "guided",
    "config": {
      "shapes": ["kare", "dikdörtgen", "üçgen"],
      "draggable_edges": true,
      "live_area_calculation": true
    }
  }
}
```

### `POST /vr-config`

Sadece VR konfigürasyonu döner (tahmin zaten yapılmışsa).

### `GET /health`

Sistem durumu kontrolü.

## 🎮 VR Sahne Tipleri

### 1. Area Geometry (`area_geometry`)
- Etkileşimli 3D şekiller (kare, dikdörtgen, üçgen)
- Sürüklenebilir kenarlar
- Canlı alan hesaplama

### 2. Area-Perimeter (`area_perimeter`)
- 3B şekil
- Renkli çevre çizgisi
- Alan ve çevre farkı görselleştirme

### 3. Number Line (`number_line`)
- 3B sayı doğrusu
- √n noktası vurgulama
- En yakın tam sayılar

### 4. Comparison (`comparison`)
- 3B çubuk grafik
- √ ifadelerin karşılaştırılması
- Görsel sıralama

## 🔧 VR Karar Kriterleri

VR şu durumlarda **otomatik açılır**:

1. **Görsel Bağımlı:** `gorsel_bagimli = "bagimli"`
2. **Alt Konu:** 
   - Alan ve Geometri
   - Alan-Çevre
   - Sayı Doğrusu / Yaklaşık Değer
   - Karşılaştırma ve Sıralama
3. **Soru Tipi:**
   - Problem
   - Yorum

**Hesaplama** tipi sorularda VR **opsiyonel** (göster butonu).

## 🎯 Kullanım Senaryosu

1. Öğrenci soruyu girer
2. Model `alt_konu` ve `soru_tipi` tahmin eder
3. VR Engine karar verir (açılacak mı, hangi sahne)
4. WebAR sahnesi yüklenir
5. Öğrenci 3D görselleştirme ile öğrenir

## 🔮 Gelecek Geliştirmeler

- [ ] Unity entegrasyonu
- [ ] AR Foundation desteği
- [ ] Daha fazla sahne tipi
- [ ] Kullanıcı etkileşim logları
- [ ] Performans metrikleri

## 📝 Notlar

- WebAR şu an Three.js ile çalışıyor
- Unity entegrasyonu için ayrı bir modül eklenebilir
- Model dosyaları eğitim sonrası oluşturulmalı
- Production'da CORS ayarları yapılmalı

