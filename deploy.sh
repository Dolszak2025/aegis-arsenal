#!/bin/bash

# 1. Przygotowanie zależności
# GCP wymaga pliku o nazwie 'requirements.txt'. Kopiujemy Twój plik.
if [ -f "requirements_senses.txt" ]; then
    echo "📦 Wykryto requirements_senses.txt - kopiowanie do requirements.txt..."
    cp requirements_senses.txt requirements.txt
else
    echo "⚠️ Nie znaleziono requirements_senses.txt, upewnij się, że requirements.txt istnieje."
fi

# 2. Wdrożenie do Cloud Functions (Gen 2)
# Gen 2 to pod spodem Cloud Run, więc świetnie obsługuje FastAPI.
echo "🚀 Wdrażanie Logos Orchestrator..."

gcloud functions deploy logos-orchestrator \
    --gen2 \
    --region=europe-central2 \
    --runtime=python311 \
    --source=. \
    --entry-point=app \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512Mi \
    --timeout=60s

# UWAGA:
# --source=.          -> bierze cały obecny katalog (wraz z folderem logos_orchestrator)
# --entry-point=app   -> szuka obiektu 'app' w pliku main.py (tym w root)