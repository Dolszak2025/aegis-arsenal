#!/bin/bash

gcloud functions deploy genesis-proof-of-life \
    --gen2 \
    --runtime=python312 \
    --region=europe-central2 \
    --source=. \
    --entry-point=genesis_proof_of_life_function \
    --trigger-http \
    --allow-unauthenticated