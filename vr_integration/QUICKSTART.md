# 🚀 Hızlı Başlangıç Kılavuzu

## 1️⃣ Gereksinimler

- Python 3.8+
- Eğitilmiş ML modeli (`modeleğitimi/model_checkpoint/` klasöründe)
- Modern web tarayıcısı (Chrome, Firefox, Edge)

## 2️⃣ Kurulum (5 dakika)

### Adım 1: Python Bağımlılıklarını Yükle

```bash
cd vr_integration
pip install -r requirements.txt
```

### Adım 2: Model Kontrolü

Model dosyalarının varlığını kontrol edin:

```bash
# Windows
dir modeleğitimi\model_checkpoint

# Linux/Mac
ls modeleğitimi/model_checkpoint
```

Şu dosyalar olmalı:
- `best_model.bin`
- `label_map.json`

**Not:** Eğer model yoksa, önce `modeleğitimi/train_transformer.py` ile modeli eğitin.

### Adım 3: API'yi Başlat

```bash
# Terminal 1
python vr_integration/run_api.py
```

API `http://localhost:8000` adresinde çalışacak.

### Adım 4: Frontend'i Aç

Yeni bir terminal açın:

```bash
# Terminal 2
cd vr_integration/frontend
python -m http.server 8080
```

Tarayıcıda `http://localhost:8080` adresine gidin.

## 3️⃣ Test Et

### Test 1: API Health Check

Tarayıcıda veya terminalde:

```bash
curl http://localhost:8000/health
```

### Test 2: Örnek Soru

Frontend'de şu soruyu deneyin:

```
Alanı 144 cm² olan karenin çevresi kaç cm'dir?
```

Seçenekler:
- A) 24
- B) 48
- C) 36
- D) 12

Görsel Bağımlı: `bagimli` seçin.

"🔮 Tahmin Et ve VR'ı Aktifleştir" butonuna tıklayın.

### Test 3: Python Test Scripti

```bash
python vr_integration/test_integration.py
```

## 4️⃣ Kullanım Senaryosu

1. **Soru Girişi:** Öğrenci soruyu ve seçenekleri girer
2. **Model Tahmini:** Backend model tahmin yapar
3. **VR Kararı:** VR Engine açılacak mı karar verir
4. **Sahne Yükleme:** Uygun 3D sahne yüklenir
5. **Etkileşim:** Öğrenci 3D görselleştirme ile öğrenir

## 5️⃣ Sorun Giderme

### API başlamıyor

```bash
# Port kullanımda mı kontrol et
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac

# Farklı port dene
uvicorn vr_integration.api.main:app --port 8001
```

### Model bulunamıyor

```bash
# Model checkpoint yolunu kontrol et
python -c "import os; print(os.path.exists('modeleğitimi/model_checkpoint/best_model.bin'))"
```

### CORS hatası

Frontend'de CORS hatası alıyorsanız, `vr_integration/api/main.py` dosyasında:

```python
allow_origins=["*"]  # Development için
```

Production'da spesifik origin'ler ekleyin.

### VR sahnesi yüklenmiyor

1. Tarayıcı konsolunu açın (F12)
2. Hataları kontrol edin
3. Three.js CDN bağlantısını kontrol edin

## 6️⃣ API Kullanımı (Programatik)

### Python ile

```python
import requests

response = requests.post('http://localhost:8000/predict', json={
    "soru_metin": "Alanı 144 cm² olan karenin çevresi kaç cm'dir?",
    "secenekler": {
        "A": "24",
        "B": "48"
    },
    "gorsel_bagimli": "bagimli"
})

data = response.json()
print(f"Alt Konu: {data['alt_konu']}")
print(f"VR Aktif: {data['vr_config']['activated']}")
```

### JavaScript ile

```javascript
const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        soru_metin: "Alanı 144 cm² olan karenin çevresi kaç cm'dir?",
        gorsel_bagimli: "bagimli"
    })
});

const data = await response.json();
console.log(data);
```

## 7️⃣ Sonraki Adımlar

- [ ] Unity entegrasyonu ekle
- [ ] Daha fazla VR sahnesi implementasyonu
- [ ] Kullanıcı etkileşim logları
- [ ] Performans optimizasyonu
- [ ] Mobile AR desteği

## 📞 Destek

Sorun yaşıyorsanız:
1. `test_integration.py` çalıştırın
2. API loglarını kontrol edin
3. Tarayıcı konsolunu kontrol edin

