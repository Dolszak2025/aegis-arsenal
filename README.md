steps:
  # ==============================================================================
  # KROK 1: INICJALIZACJA TERRAFORM (GENOME BASE)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-init'
    dir: '99_INFRA/terraform' # Zamiast 'cd' w skrypcie, ustawiamy kontekst katalogu tutaj
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "🌍 [GENOME] Inicjalizacja środowiska Terraform..."
        terraform init -no-color

  # ==============================================================================
  # KROK 2: PLANOWANIE ZMIAN (PREDICTION LAYER)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-plan'
    dir: '99_INFRA/terraform'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        echo "🔮 [CORTEX] Generowanie planu zmian..."
        # Plan binarny
        terraform plan -out=tfplan -no-color
        # Plan JSON (zapisujemy go w root workspace, aby Python miał łatwy dostęp)
        terraform show -json tfplan > ../../plan.json
    waitFor: ['tf-init']

  # ==============================================================================
  # KROK 3: GUVERNER POLICY ENFORCEMENT (AEGIS SHIELD)
  # ==============================================================================
  - name: 'python:3.11-slim'
    id: 'policy-check'
    entrypoint: 'python'
    # UWAGA: Cloud Functions zazwyczaj wymagają uwierzytelnienia (OIDC Token).
    # Poniższy kod zakłada endpoint publiczny lub autoryzację w inny sposób.
    # Jeśli funkcja jest prywatna, trzeba dodać nagłówek "Authorization: Bearer <token>"
    args:
      - '-c'
      - |
        import os
        import json
        import time
        import urllib.request
        import sys

        GUVERNER_URL = "https://europe-central2-hivemind-alpha.cloudfunctions.net/guverner-enforcement"
        PLAN_FILE = "plan.json" # Plik jest w root workspace (domyślny dir)
        MAX_RETRIES = 3

        print(f"🛡️ [AEGIS] Rozpoczynam audyt planu...")

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
                        sys.exit(1)
                    
                    print("✅ [GUVERNER] Zgoda udzielona.")
                    sys.exit(0)

            except Exception as e:
                print(f"⚠️ Próba {attempt+1}/{} nieudana: {}")
                time.sleep(2 ** attempt)

        print("❌ Nie udało się połączyć z Guvernerem.")
        sys.exit(1)
    waitFor: ['tf-plan']

  # ==============================================================================
  # KROK 4: ARCHIWIZACJA DOWODOWA (AUDIT TRAIL)
  # ==============================================================================
  - name: 'gcr.io/cloud-builders/gsutil'
    id: 'audit-log'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "📂 [ARCHIVE] Zabezpieczanie planu..."
        # POPRAWKA: Używamy ${} i ${} zamiast samego $
        gsutil cp plan.json gs://${}-audit-logs/plans/plan-${}.json || echo "⚠️ Warning: Nie udało się zapisać logu."
    waitFor: ['policy-check']

  # ==============================================================================
  # KROK 5: APLIKACJA ZMIAN (EXECUTION)
  # ==============================================================================
  - name: 'hashicorp/terraform:light'
    id: 'tf-apply'
    dir: '99_INFRA/terraform' # CRITICAL: Apply musi być uruchomiony w katalogu z zainicjowanym .terraform
    entrypoint: 'sh'          # Używamy sh, aby explicite wywołać apply na pliku
    args: 
      - '-c'
      - 'terraform apply -auto-approve tfplan'
    waitFor: ['policy-check', 'audit-log']

timeout: '1200s'
options:
  logging: CLOUD_LOGGING_ONLY