
                #!/bin/bash
# Operacja "TRWAŁE ŹRÓDŁO" v1.1 - Skrypt Inicjalizacyjny
# Cel: Stworzenie repozytorium, inicjalizacja Supabase, przygotowanie miejsca na Archiwum Główne.

set -e # Zakończ przy pierwszym błędzie

REPO_URL=$1
REPO_NAME="agentos-v2-production"

if [ -z "$REPO_URL" ]; then
  echo "BŁĄD: Musisz podać URL repozytorium GitHub jako pierwszy argument." >&2
  echo "Przykład: ./setup_repo.sh git@github.com:USER/REPO.git" >&2
  exit 1
fi

echo "=== KROK 0.1: Tworzenie struktury projektu w $(pwd) ==="
if [ -d "$REPO_NAME" ]; then
  echo "OSTRZEŻENIE: Katalog '$REPO_NAME' już istnieje. Pomijam tworzenie."
else
  mkdir "$REPO_NAME"
  echo "OK: Stworzono katalog '$REPO_NAME'."
fi
cd "$REPO_NAME"
echo "Pracuję teraz w katalogu: $(pwd)"

echo "=== KROK 0.2: Inicjalizacja Git ==="
if [ -d ".git" ]; then
  echo "OSTRZEŻENIE: Repozytorium Git już zainicjowane. Pomijam 'git init'."
else
  git init -b main # Używamy nowszej składni, Cloud Shell powinien ją wspierać
  echo "OK: Zainicjowano repozytorium Git z gałęzią 'main'."
fi
if git remote | grep -q 'origin'; then
    echo "OSTRZEŻENIE: Zdalne 'origin' już istnieje. Pomijam dodawanie."
else
    git remote add origin "$REPO_URL"
    echo "OK: Dodano zdalne repozytorium 'origin': $REPO_URL"
fi

echo "=== KROK 1.1 (TOR 1): Inicjalizacja Lokalnego Supabase ==="
echo "Sprawdzanie dostępności Supabase CLI..."
if ! command -v supabase &> /dev/null; then
    echo "Instalowanie Supabase CLI (może chwilę potrwać)..."
    # Używamy npm do instalacji globalnej, Cloud Shell powinien mieć npm
    npm install -g supabase
fi
echo "Uruchamianie 'supabase init'..."
if [ -d "supabase" ]; then
    echo "OSTRZEŻENIE: Katalog 'supabase' już istnieje. Pomijam 'supabase init'."
else
    # Używamy --use-yarn, zgodnie z Dyrektywą Wdrożeniową lub bez jeśli yarn nie ma
    supabase init --use-yarn || supabase init
    echo "OK: Zainicjowano Supabase lokalnie (pliki konfiguracyjne stworzone w ./supabase)."
fi

echo "=== KROK 1.2 & KROK 2.1 (GITIGNORE & STRATEGIA): Tworzenie podstawowych plików ==="
echo "Tworzenie .gitignore..."
cat << EOF > .gitignore
# Supabase local dev
supabase/.temp/
supabase/logs/
supabase/volumes/

# Node dependencies
node_modules/
yarn.lock
package-lock.json

# Python virtual environment
.venv/
venv/
ENV/
env/

# Python cache
__pycache__/
*.pyc
*.pyo

# Secrets (NIGDY NIE COMMITUJ!)
.env*
access-token*
*.key
*.pem

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
EOF
echo "OK: Stworzono .gitignore."

echo "Tworzenie katalogu na Strategię..."
mkdir -p 00_STRATEGIA
touch 00_STRATEGIA/.gitkeep # Aby pusty katalog został dodany do Git
echo "OK: Stworzono katalog '00_STRATEGIA'."

# Generowanie pustych plików strategicznych jako placeholderów
echo "# README - Archiwum Główne - CZEKAM NA TREŚĆ" > 00_STRATEGIA/README.md
echo "# 01 Zjednoczona Doktryna - CZEKAM NA TREŚĆ" > 00_STRATEGIA/01_ZJEDNOCZONA_DOKTRYNA.md
echo "# 02 Zintegrowany Plan Działania v2.2 - CZEKAM NA TREŚĆ" > 00_STRATEGIA/02_PLAN_DZIAŁANIA_V2.2.md
echo "# 03 Mapa Połączeń AgentOS - CZEKAM NA TREŚĆ" > 00_STRATEGIA/03_MAPA_POŁĄCZEŃ.md
echo "# 04 Modyfikacje Krytyczne (z Weryfikacji) - CZEKAM NA TREŚĆ" > 00_STRATEGIA/04_MODYFIKACJE_KRYTYCZNE.md
echo "# 05 Doktryna Narzędzi AI (Copilot, CLI) - CZEKAM NA TREŚĆ" > 00_STRATEGIA/05_DOKTRYNA_NARZĘDZI_AI.md
echo "OK: Stworzono puste pliki strategiczne w 00_STRATEGIA."

echo "=== KROK X: Wymagania Wstępne CI/CD (Placeholder) ==="
echo "Tworzenie pustego pliku cloudbuild.yaml..."
echo "# TODO: Zdefiniować kroki CI/CD dla Agenta Praxis" > cloudbuild.yaml
echo "OK: Stworzono pusty cloudbuild.yaml."

echo "=== SKRYPT ZAKOŃCZONY POMYŚLNIE ==="
echo ""
echo "NASTĘPNE KROKI MANUALNE (KRYTYCZNE):"
echo "1. Jesteś już w katalogu projektu: $(pwd)"
echo "2. RĘCZNIE wklej zawartość 6 plików strategicznych (README, 01-05) do katalogu 00_STRATEGIA/."
echo "3. Dodaj wszystkie pliki do Git: git add ."
echo "4. Stwórz pierwszy commit: git commit -m 'INITIAL: Ustanowienie Archiwum Głównego v1.0 i struktury projektu'"
echo "5. Wypchnij zmiany do GitHub: git push origin main"
echo "6. Uruchom lokalny Supabase (aby sprawdzić): supabase start"
echo ""
echo "Po tych krokach, 'TRWAŁE ŹRÓDŁO' zostanie ustanowione."

                                                                                                                

                                                                                                                                


