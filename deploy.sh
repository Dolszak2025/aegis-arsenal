#!/bin/bash

gcloud functions deploy genesis-proof-of-life \
    --gen2 \
    --runtime=python312 \
    --region=europe-central2 \
    --source=. \
    --entry-point=genesis_proof_of_life_function \
    --trigger-topic=aegis-pubsub-topic \
    --allow-unauthenticated \
    --set-env-vars SUPABASE_CONN_STRING=${SUPABASE_CONN_STRING} \
    --set-secrets OPENAI_API_KEY=openai-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest \
    --service-account=aegis-bot-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --ingress-settings=internal-only