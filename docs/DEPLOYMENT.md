# Production Deployment Guide

Panduan penerapan bot otomasi editorial pada server VPS (Ubuntu/Debian) atau platform Container (Google Cloud Run / Railway / Docker).

---

## Opsi 1: Menjalankan dengan Docker Compose (Direkomendasikan)

1. Clone repositori ke server:
   ```bash
   git clone https://github.com/FatirGibran/Autimation-Tele-Prodi.git
   cd Autimation-Tele-Prodi
   ```
2. Salin dan konfigurasikan file `.env`:
   ```bash
   cp .env.example .env
   nano .env
   ```
3. Bangun dan jalankan kontainer:
   ```bash
   docker-compose up -d --build
   ```
4. Periksa log:
   ```bash
   docker-compose logs -f
   ```

---

## Opsi 2: Menjalankan dengan Systemd di VPS Ubuntu

1. Buat virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Buat file service systemd `/etc/systemd/system/editorial-bot.service`:
   ```ini
   [Unit]
   Description=Telegram Editorial Bot Prodi S1 Informatika
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Autimation-Tele-Prodi
   ExecStart=/home/ubuntu/Autimation-Tele-Prodi/venv/bin/python bot.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
3. Aktifkan dan jalankan:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable editorial-bot
   sudo systemctl start editorial-bot
   ```

---

## Opsi 3: Serverless Google Cloud Run

1. Bangun image dengan Google Cloud Build:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/tele-editorial-bot
   ```
2. Deploy ke Cloud Run:
   ```bash
   gcloud run deploy tele-editorial-bot \
     --image gcr.io/[PROJECT_ID]/tele-editorial-bot \
     --platform managed \
     --region asia-southeast2 \
     --allow-unauthenticated \
     --set-env-vars TELEGRAM_BOT_TOKEN="xxx",GEMINI_API_KEY="yyy"
   ```
