-- Skrypt: db/feedback_inbox.sql
-- Cel: Utworzenie tabeli feedback_inbox dla protokołu anonimizacji (AIP)
-- Uwaga: uruchomić w edytorze SQL Supabase (prawidłowe środowisko Postgres)

-- Wymagane rozszerzenie do gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- KROK 3.1: Tworzy tabelę 'feedback_inbox' dla anonimowych danych zwrotnych
CREATE TABLE IF NOT EXISTS public.feedback_inbox (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        created_at timestamptz DEFAULT timezone('utc'::text, now()) NOT NULL,

            -- Surowe dane wejściowe (co powiedział użytkownik)
                raw_feedback_text text NOT NULL,
                    associated_query text,

                        -- Surowy kontekst PII (DO ANONIMIZACJI)
                            -- Przechowuje user_id, IP itp. TYLKO na czas anonimizacji
                                raw_pii_context jsonb,

                                    -- Status dla procesu 'Kuratora Danych'
                                        status text DEFAULT 'pending_anonymization'::text NOT NULL,

                                            -- Dane po anonimizacji (bezpieczne do treningu)
                                                anonymized_feedback_text text,
                                                    anonymized_associated_query text
                                                    );

                                                    COMMENT ON TABLE public.feedback_inbox IS 'Kolejka wejściowa dla Protokołu Anonimizacji (AIP). Mandat G-20251107-A.';

                                                    -- KROK 3.2: Ustawienie polityk bezpieczeństwa (Row Level Security)
                                                    -- Domyślnie blokujemy WSZYSTKO.
                                                    ALTER TABLE public.feedback_inbox ENABLE ROW LEVEL SECURITY;

                                                    -- Przykładowa polityka (SZABLON) — nie włączaj wprost w prod bez dostosowania.
                                                    -- Poniżej przykład: zezwól na wstawianie z usługi z kluczem service_role
                                                    -- (w Supabase service_role ma pełne uprawnienia — używaj ostrożnie).
                                                    --
                                                    -- CREATE POLICY insert_from_service_role ON public.feedback_inbox
                                                    --     FOR INSERT
                                                    --     TO authenticated
                                                    --     USING (false)
                                                    --     WITH CHECK ( current_setting('request.jwt.claims', true) IS NOT NULL );
                                                    --
                                                    -- Lepiej: tworzyć specyficzną politykę po stronie Supabase, np. z użyciem
                                                    -- funkcji zabezpieczającej, lub zezwolić tylko service_role przez bezpieczne
                                                    -- mechanizmy (np. Edge Function lub serwer pośredniczący). Nie kopiuj powyższego
                                                    -- bez audytu bezpieczeństwa.
                                                    