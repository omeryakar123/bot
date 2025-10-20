
# Telegram WebApp Bot (FastAPI + python-telegram-bot + SQLite)

## 🚀 Özellikler
- /start → Telegram içinde **WebApp butonu** ile oyunu açar
- /me → Kullanıcının en iyi skorunu gösterir
- /top → İlk 10 leaderboard
- FastAPI backend → `/api/submit_score` ve `/api/leaderboard`
- `initData` imza doğrulama (Telegram WebApp resmi yöntemi)
- SQLite kalıcı veritabanı

## 🔧 Kurulum (lokal)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env .env        # .env içini doldur
uvicorn app:fastapi_app --reload
```
Telegram'da botunuza yazın: `/start`

## 🌐 Deploy (Render)
- Repo'yu GitHub'a yükleyin
- Render > New > Web Service
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app:fastapi_app --host 0.0.0.0 --port $PORT`
- Env Vars: `BOT_TOKEN`, `WEBAPP_URL`, `ADMIN_ID`

## 🌐 Deploy (Railway/Heroku)
- `Procfile` hazır:
```
web: uvicorn app:fastapi_app --host 0.0.0.0 --port $PORT
```

## 🕹️ Frontend entegrasyonu (örnek JS)
```html
<script>
  async function submitScore(score) {
    const tg = window.Telegram?.WebApp;
    if (!tg || !tg.initData) {
      alert("Telegram WebApp initData yok!");
      return;
    }
    const res = await fetch("/api/submit_score", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ initData: tg.initData, score })
    });
    const data = await res.json();
    console.log("submit_score cevabı:", data);
  }
  // Oyun bittiğinde: submitScore(finalScore);
</script>
```

## 🛡️ Güvenlik
- `initData` HMAC-SHA256 ile doğrulanır (kimlik sahteciliğine karşı).
- Sadece doğrulanmış kullanıcılara skor yazılır.

## ❓ SSS
- Bot ve API aynı proseste çalışır (tek servis). Ücretsiz katmanlarda uygundur.
- DB: `scores.db` dosyası klasörde oluşur (kalıcı disk sağlayan servis seçiniz).
