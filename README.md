steps:
  # ==============================================================================
  # KROK 1: INICJALIZACJA TERRAFORM (GENOME BASE)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-init'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "🌍 [GENOME] Inicjalizacja środowiska Terraform..."
        cd 99_INFRA/terraform
        terraform init -no-color

  # ==============================================================================
  # KROK 2: PLANOWANIE ZMIAN (PREDICTION LAYER)
  # Generuje plan w formacie JSON dla maszyny (Guverner) i tekstowym dla człowieka.
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-plan'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "🔮 [CORTEX] Generowanie planu zmian..."
        cd 99_INFRA/terraform
        # Plan binarny do aplikacji
        terraform plan -out=tfplan -no-color
        # Plan JSON do analizy przez AI (Guverner)
        terraform show -json tfplan > ../../plan.json
    waitFor: ['tf-init']

  # ==============================================================================
  # KROK 3: GUVERNER POLICY ENFORCEMENT (AEGIS SHIELD)
  # Wysyła plan do analizy. Używa Pythona dla lepszej obsługi błędów niż curl.
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
        MAX_RETRIES = 3

        print(f"🛡️ [AEGIS] Rozpoczynam audyt planu w {GUVERNER_URL}...")

        try:
            with open(PLAN_FILE, 'rb') as f:
                plan_data = f.read()
        except FileNotFoundError:
            print("❌ Błąd: Nie znaleziono pliku plan.json!")
            sys.exit(1)

        req = urllib.request.Request(GUVERNER_URL, data=plan_data, headers={'Content-Type': 'application/json'})

        for attempt in range(MAX_RETRIES):
            try:
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    
                    if result.get("status") == "BLOCKED":
                        print(f"❌ [GUVERNER VETO] Blokada wdrożenia! Powód: {result.get('reason')}")
                        sys.exit(1) # Zrywamy build
                    
                    print("✅ [GUVERNER] Zgoda udzielona. Plan zgodny z Konstytucją.")
                    sys.exit(0) # Sukces

            except Exception as e:
                print(f"⚠️ Próba {attempt+1}/{MAX_RETRIES} nieudana: {e}")
                time.sleep(2 ** attempt) # Exponential backoff

        print("❌ Nie udało się połączyć z Guvernerem po wielu próbach.")
        sys.exit(1)
    waitFor: ['tf-plan']

  # ==============================================================================
  # KROK 4: ARCHIWIZACJA DOWODOWA (AUDIT TRAIL)
  # Zapisuje plan do GCS przed wdrożeniem (Forensic Evidence).
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/gsutil'
    id: 'audit-log'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "📂 [ARCHIVE] Zabezpieczanie planu w logach audytowych..."
        # Zmienna $BUILD_ID jest dostępna w Cloud Build
        gsutil cp plan.json gs://${PROJECT_ID}-audit-logs/plans/plan-${BUILD_ID}.json || echo "⚠️ Warning: Nie udało się zapisać logu, ale kontynuuję."
    waitFor: ['policy-check']

  # ==============================================================================
  # KROK 5: APLIKACJA ZMIAN (EXECUTION)
  # Wykonuje się TYLKO jeśli krok 'policy-check' zakończył się sukcesem.
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-apply'
    args: ['apply', '-auto-approve', '99_INFRA/terraform/tfplan']
    dir: '.'
    waitFor: ['policy-check', 'audit-log']

timeout: '1200s'
options:
  logging: CLOUD_LOGGING_ONLY
