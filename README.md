steps:
  # ==============================================================================
  # KROK 0: PRZYGOTOWANIE I CACHE (MEMORY RECALL)
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/gsutil'
    id: 'restore-cache'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "🧠 Pobieranie cache pluginów..."
        mkdir -p /workspace/99_INFRA/terraform/.terraform.d/plugin-cache
        
        if gsutil cp gs://${}/terraform-plugins.tgz /workspace/terraform-plugins.tgz; then
          echo "✅ Cache pobrany. Rozpakowywanie..."
          tar -xzf /workspace/terraform-plugins.tgz -C /workspace/99_INFRA/terraform/.terraform.d/plugin-cache
        else
          echo "⚠️ Brak cache lub błąd pobierania. Budujemy od zera."
        fi

  # ==============================================================================
  # KROK 1: INICJALIZACJA TERRAFORM (GENOME BASE)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-init'
    dir: '99_INFRA/terraform'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "🌍 [GENOME] Inicjalizacja środowiska Terraform..."
        # Konfiguracja CLI, aby korzystał z lokalnego cache
        echo 'plugin_cache_dir = "/workspace/99_INFRA/terraform/.terraform.d/plugin-cache"' > .terraformrc
        export TF_CLI_CONFIG_FILE=$(pwd)/.terraformrc
        
        terraform init -no-color
    waitFor: ['restore-cache']

  # ==============================================================================
  # KROK 2: AEGIS SHIELD - SECURITY SCAN (PRE-FLIGHT)
  # ==============================================================================
  - name: 'bridgecrew/checkov'
    id: 'aegis-scan'
    dir: '99_INFRA/terraform'
    # Dodajemy --soft-fail jeśli nie chcemy przerywać builda przy błędach, 
    # w przeciwnym razie usuń ten flagę.
    args: ['-d', '.', '--skip-check', 'CKV_GCP_XX'] 
    waitFor: ['tf-init']

  # ==============================================================================
  # KROK 3: PLANOWANIE ZMIAN (PREDICTION LAYER)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-plan'
    dir: '99_INFRA/terraform'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "🔮 Generowanie planu zmian..."
        export TF_CLI_CONFIG_FILE=$(pwd)/.terraformrc
        
        terraform plan -out=tfplan -no-color
        terraform show -json tfplan > ../../plan.json
    waitFor: ['aegis-scan']

  # ==============================================================================
  # KROK 4: GENEROWANIE TOŻSAMOŚCI (IDENTITY PROOF)
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/gcloud'
    id: 'oidc-token'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "🔑 Generowanie tokena OIDC..."
        gcloud auth print-identity-token \
          --audiences="https://europe-central2-hivemind-alpha.cloudfunctions.net/guverner-enforcement" \
          > /workspace/oidc_token.txt
    waitFor: ['tf-plan']

  # ==============================================================================
  # KROK 5: GUVERNER POLICY ENFORCEMENT (AEGIS SHIELD - LOGIC)
  # ==============================================================================
  - name: 'python:3.11-slim'
    id: 'policy-check'
    entrypoint: 'python'
    args:
      - '-c'
      - |
        import os
        import json
        import time
        import urllib.request
        import sys

        GUVERNER_URL = "https://europe-central2-hivemind-alpha.cloudfunctions.net/guverner-enforcement"
        PLAN_FILE = "plan.json"
        TOKEN_FILE = "oidc_token.txt"
        MAX_RETRIES = 3

        print(f"🛡️ Rozpoczynam audyt planu...")

        # 1. Wczytanie Planu
        try:
            with open(PLAN_FILE, 'rb') as f:
                plan_data = f.read()
        except FileNotFoundError:
            print("❌ Błąd: Nie znaleziono pliku plan.json!")
            sys.exit(1)

        # 2. Wczytanie Tokena OIDC
        try:
            with open(TOKEN_FILE, 'r') as f:
                oidc_token = f.read().strip()
        except FileNotFoundError:
            print("❌ Błąd: Nie wygenerowano tokena OIDC!")
            sys.exit(1)

        # 3. Request z autoryzacją
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {}"
        }
        
        req = urllib.request.Request(GUVERNER_URL, data=plan_data, headers=headers)

        for attempt in range(MAX_RETRIES):
            try:
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    
                if result.get("status") == "BLOCKED":
                    print(f"❌ Blokada wdrożenia! Powód: {result.get('reason')}")
                    sys.exit(1)
                
                print("✅ Zgoda udzielona.")
                sys.exit(0)

            except Exception as e:
                print(f"⚠️ Próba {attempt+1}/{} nieudana: {str(e)}")
                time.sleep(2 ** attempt)

        print("❌ Nie udało się połączyć z Guvernerem po wielu próbach.")
        sys.exit(1)
    waitFor: ['oidc-token']

  # ==============================================================================
  # KROK 6: NOTYFIKACJA WSTĘPNA (SYNAPSE LINK)
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/curl'
    id: 'slack-notify-start'
    secretEnv: ['SLACK_WEBHOOK']
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\": \"🚀 Hivemind Deployment\nStatus: Plan Approved & Creating Resources...\nBuild ID: $BUILD_ID\nRepo: $REPO_NAME\"}" \
        $$SLACK_WEBHOOK
    waitFor: ['policy-check']

  # ==============================================================================
  # KROK 7: ARCHIWIZACJA DOWODOWA (AUDIT TRAIL)
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/gsutil'
    id: 'audit-log'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "📂 Zabezpieczanie planu..."
        gsutil cp plan.json gs://${}/plans/plan-${}.json || echo "⚠️ Warning: Nie udało się zapisać logu."
    waitFor: ['policy-check']

  # ==============================================================================
  # KROK 8: APLIKACJA ZMIAN (EXECUTION)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-apply'
    dir: '99_INFRA/terraform'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "⚙️ Wdrażanie zmian..."
        export TF_CLI_CONFIG_FILE=$(pwd)/.terraformrc
        terraform apply -auto-approve tfplan
    waitFor: ['audit-log', 'slack-notify-start']

  # ==============================================================================
  # KROK 9: ZAPISANIE CACHE (MEMORY STORAGE)
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/gsutil'
    id: 'save-cache'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "🧠 Aktualizacja cache..."
        # Pakujemy tylko zawartość katalogu cache, nie całą ścieżkę absolutną
        cd /workspace/99_INFRA/terraform/.terraform.d/plugin-cache
        tar -czf /workspace/terraform-plugins.tgz .
        gsutil cp /workspace/terraform-plugins.tgz gs://${}/terraform-plugins.tgz
    waitFor: ['tf-apply']

# ==============================================================================
# KONFIGURACJA GLOBALNA
# ==============================================================================
substitutions:
  _CACHE_BUCKET: 'hivemind-build-cache-v1'
  _AUDIT_BUCKET: 'hivemind-audit-logs'

availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/slack-webhook/versions/latest
      env: 'SLACK_WEBHOOK'

timeout: '1800s'

options:
  logging: CLOUD_LOGGING_ONLY