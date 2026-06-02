# Analiza badania — krótkie formy wideo a zdolności poznawcze

## 1. Cel badania

Zbadanie zależności pomiędzy intensywnością korzystania z krótkich form wideo (KFW, ang. SFV — Short-Form Video) a wybranymi zdolnościami poznawczymi (pamięć robocza, uwaga, fluencja werbalna) oraz poziomem uważności (mindfulness) i symptomami ADHD u młodych dorosłych.

---

## 2. Schemat przepływu badania

```
Strona startowa → Rozpocznij badanie (UUID w sesji)
  → User Info (wiek, płeć, wykształcenie, czy ogląda KFW)
    → Habits (jeśli ogląda KFW: czas, sesje, platformy, typy treści)
      → Kwestionariusz: ASRS + MAAS + MPATS + TTAS
        → Digit Span (pamięć robocza)
          → SART (uwaga)
            → Verbal Fluency (fluencja werbalna)
              → Thank You
```

---

## 3. Zmienne niezależne (predyktory)

### 3.1. Dane demograficzne (`User`)
| Zmienna | Typ | Opis |
|--------|-----|------|
| `age` | `Integer` | Wiek (lata) |
| `gender` | `Categorical` | Płeć: Mężczyzna / Kobieta / Inna |
| `education` | `Categorical` | Wykształcenie: Podstawowe / Średnie / Wyższe |
| `is_on_mobile` | `Boolean` | Czy badany korzysta z urządzenia mobilnego (auto-detekcja) |

### 3.2. Nawyki KFW (`Habits`, tylko jeśli `is_watching_SFV = True`)
| Zmienna | Typ | Opis |
|--------|-----|------|
| `daily_SFV_time` | `Ordinal` | Średni łączny czas dzienny (min): 15, 30, 90, 150, 240, 360 |
| `daily_SFV_sessions` | `Ordinal` | Liczba sesji dziennie: 2, 4, 8, 12 |
| `preferred_platforms` | `Multi-categorical` | Platformy KFW (M2M do `SFVPlatform`) |
| `preferred_content_types` | `Multi-categorical` | Typy treści (M2M do `ContentType`) |

### 3.3. Status oglądania KFW
| Zmienna | Typ | Opis |
|--------|-----|------|
| `is_watching_SFV` | `Boolean` | Czy badany w ogóle ogląda KFW → pozwala na podział na grupy |

---

## 4. Zmienne zależne (mierzone)

### 4.1. Kwestionariusz — ASRS (Adult ADHD Self-Report Scale)
- **18 pytań**, skala 0–4 (Nigdy → Bardzo często)
- Dwie podskale:
  - **ASRS-A** (6 pytań): nieuwaga (inattention)
  - **ASRS-B** (12 pytań): nadpobudliwość/impulsywność (hyperactivity/impulsivity)
- **Wskaźnik**: suma punktów dla ASRS-A, ASRS-B i łączny wynik ASRS

### 4.2. Kwestionariusz — MAAS (Mindful Attention Awareness Scale)
- **15 pytań**, skala 1–6 (Prawie zawsze → Prawie nigdy)
- Mierzy dyspozycyjną uważność — im wyższy wynik, tym wyższa uważność
- **Wskaźnik**: średnia z 15 pozycji (typowe dla MAAS)

### 4.3. Kwestionariusz — MPATS (Mobile Phone Addiction Tendency Scale for Short-form videos)
- **7 pytań**, skala 0–4 (Never → Always)
- Mierzy tendencję do uzależnienia od krótkich form wideo na telefonie
- **Wskaźnik**: suma punktów

### 4.4. Kwestionariusz — TTAS (TikTok Addiction Scale)
- **15 pytań**, skala 1–5 (Very rarely → Very often)
- Mierzy poziom uzależnienia od TikToka
- **Wskaźnik**: suma punktów

### 4.5. Zadanie poznawcze — Digit Span (pamięć robocza)
- **Model**: `DigitSpanResult` — każda runda osobno
- **Próby na użytkownika**: zmienna liczba (aż do 2 błędów z rzędu)
- **Zmienne**:
  | Zmienna | Typ | Opis |
  |--------|-----|------|
  | `span` | `Integer` | Długość sekwencji w danej próbie |
  | `sequence` | `String` | Prezentowana sekwencja cyfr |
  | `user_answer` | `String` | Odpowiedź uczestnika |
  | `correct` | `Boolean` | Czy odpowiedź poprawna |
  | `created_at` | `DateTime` | Sygnatura czasowa próby |

- **Wskaźniki do analizy**:

  *Metryki binarne (poprawne/błędne):*
  - Maksymalny osiągnięty span (`MAX(span)`)
  - Najwyższy span z poprawną odpowiedzią (`MAX(span) WHERE correct=True`)
  - Liczba prób ogółem (`COUNT(*)`)
  - Procent poprawnych odpowiedzi (`AVG(correct)`)
  - Span, przy którym nastąpiły 2 błędne odpowiedzi z rzędu

  *Metryki oparte na odległości Levenshteina:*
  Zamiast wyłącznie binarnej oceny poprawności (OK/FAIL), odległość Levenshteina pozwala ocenić **jak blisko** poprawnej odpowiedzi był uczestnik — nawet gdy odpowiedział błędnie. Np. dla sekwencji `"5832"` odpowiedź `"5831"` ma dystans 1, a `"1234"` ma dystans 4.

  Odległość Levenshteina między dwoma łańcuchami to minimalna liczba operacji (wstawienia, usunięcia, zamiany pojedynczego znaku) potrzebnych do przekształcenia jednego w drugi.

  - **Dystans Levenshteina na próbę** (`lev_dist`): `levenshtein(sequence, user_answer)` — surowy dystans dla każdej próby
  - **Znormalizowany dystans Levenshteina** (`lev_norm`): `lev_dist / span` — dystans podzielony przez długość sekwencji, umożliwia porównywanie prób o różnych spanach (wartość 0 = perfekcyjnie, 1 = całkowicie błędnie)
  - **Średni znormalizowany dystans Levenshteina** (`mean_lev_norm`): średnia `lev_norm` ze wszystkich prób danego użytkownika — ogólna miara precyzji odpowiedzi
  - **Średni znormalizowany dystans dla błędnych prób** (`mean_lev_norm_errors`): średnia `lev_norm` tylko dla prób gdzie `correct=False` — jak bardzo użytkownik mylił się, gdy już popełniał błąd
  - **Dystans na najwyższym spanie** (`lev_at_max_span`): `lev_norm` dla próby o najwyższym `span` — precyzja na granicy możliwości uczestnika
  - **Próg zbliżonej poprawności** (`near_correct`): `lev_norm <= 0.5` — odpowiedź "częściowo poprawna" (co najmniej połowa cyfr na właściwych pozycjach)

### 4.6. Zadanie poznawcze — SART (uwaga)
- **Model**: `SARTResult` — jeden rekord na użytkownika
- **30 prób**, cyfra wyświetlana 300ms, przerwa 700ms
- **Zmienne**:
  | Zmienna | Typ | Opis |
  |--------|-----|------|
  | `commission_errors` | `Integer` | Błędy komisji — kliknięcie na "3" (no-go) |
  | `omission_errors` | `Integer` | Błędy pominięcia — brak kliknięcia na cyfrę ≠ 3 |
  | `mean_reaction_time` | `Float` | Średni czas reakcji (ms) |
  | `trials_data` | `JSON` | Dane każdej z 30 prób (cyfra, kliknięto?, RT, poprawność) |
  | `sequence` | `String` | Sekwencja 30 cyfr |

- **Wskaźniki do analizy**:
  - `commission_errors` — miara impulsywności / trudności z hamowaniem
  - `omission_errors` — miara nieuwagi / odpływania myślami
  - `mean_reaction_time` — szybkość przetwarzania
  - Zmienność RT (z `trials_data`)
  - Liczba poprawnych reakcji (`30 - commission - omission`)

### 4.7. Zadanie poznawcze — Verbal Fluency (fluencja werbalna)
- **Model**: `VerbalFluencyResult` — jeden rekord na użytkownika
- **6 prób** (litera + kategoria), każda 60s:
  | Litera | Kategoria |
  |--------|-----------|
  | A | Miasto |
  | B | Zwierzę |
  | C | Imię |
  | D | Państwo |
  | F | Zawód |
  | K | Roślina |

- **Zmienne** (w `trials_data` JSON):
  | Zmienna | Typ | Opis |
  |--------|-----|------|
  | `trial_id` | `Integer` | ID próby z DB |
  | `letter` | `String` | Litera |
  | `category` | `String` | Kategoria semantyczna |
  | `words` | `Array` | Lista wpisanych słów |

- **Wskaźniki do analizy**:
  - Łączna liczba słów we wszystkich próbach
  - Liczba słów na próbę
  - Liczba słów na kategorię (fluencja semantyczna)
  - Średnia długość słów

---

## 5. Relacje między zmiennymi — plan analiz

### 5.1. Główne hipotezy

| # | Hipoteza | Predyktory | Zmienna zależna |
|---|----------|-----------|-----------------|
| H1 | Wyższa intensywność korzystania z KFW wiąże się z niższą pojemnością pamięci roboczej | `daily_SFV_time`, `daily_SFV_sessions` | `MAX(span)` Digit Span |
| H1a | Wyższa intensywność KFW wiąże się z większym średnim znormalizowanym dystansem Levenshteina | `daily_SFV_time`, `daily_SFV_sessions` | `mean_lev_norm` Digit Span |
| H1b | Wyższa intensywność KFW wiąże się z większym dystansem Levenshteina przy granicznym spanie | `daily_SFV_time`, `daily_SFV_sessions` | `lev_at_max_span` Digit Span |
| H2 | Wyższa intensywność KFW wiąże się z gorszą uwagą | `daily_SFV_time`, `daily_SFV_sessions` | `commission_errors`, `omission_errors` SART |
| H3 | Wyższa intensywność KFW wiąże się z niższą fluencją werbalną | `daily_SFV_time`, `daily_SFV_sessions` | Łączna liczba słów Verbal Fluency |
| H4 | Osoby oglądające KFW mają wyższe wyniki ASRS (więcej symptomów ADHD) niż nieoglądający | `is_watching_SFV` | ASRS total |
| H5 | Wyższe zużycie KFW koreluje z niższą uważnością | `daily_SFV_time`, MPATS, TTAS | MAAS mean |
| H6 | Wynik MPATS i TTAS koreluje ze wskaźnikami poznawczymi | MPATS total, TTAS total | Digit Span, SART, Verbal Fluency |

### 5.2. Potencjalne zmienne zakłócające (confounders)
- **Wiek** — może korelować zarówno z używaniem KFW, jak i zdolnościami poznawczymi
- **Wykształcenie** — może wpływać na wyniki fluencji werbalnej i pamięci roboczej
- **Płeć** — możliwe różnice w używaniu KFW i zdolnościach poznawczych
- **Urządzenie mobilne vs desktop** — może wpływać na czas reakcji SART i interakcję

### 5.3. Proponowane analizy statystyczne

#### Analizy opisowe
- Statystyki opisowe wszystkich zmiennych (M, SD, min, max, rozkład)
- Korelacje zerowego rzędu między wszystkimi zmiennymi (macierz korelacji)

#### Porównania grupowe
- **t-test / Mann-Whitney**: użytkownicy KFW vs nie-użytkownicy dla każdego wskaźnika poznawczego
- **ANOVA / Kruskal-Wallis**: porównanie grup o różnym poziomie `daily_SFV_time` (6 poziomów) lub `daily_SFV_sessions` (4 poziomy)
- **Chi-kwadrat**: związek między `is_watching_SFV` a progami klinicznymi ASRS

#### Analizy korelacyjne
- Korelacja Spearmana między `daily_SFV_time`/`daily_SFV_sessions` a wskaźnikami poznawczymi (dane porządkowe)
- Korelacja Pearsona/Spearmana między MPATS, TTAS a Digit Span, SART, Verbal Fluency
- Analiza korelacji cząstkowych z kontrolą wieku i wykształcenia

#### Analizy regresji
- **Regresja liniowa**: przewidywanie `max_span`, `mean_rt`, `total_words` na podstawie `daily_SFV_time`, `age`, `education`
- **Regresja logistyczna**: przewidywanie `is_watching_SFV` na podstawie wyników poznawczych
- **Regresja Poissona**: modelowanie liczby błędów SART (`commission_errors`, `omission_errors`)
- Analiza mediacji: czy MAAS pośredniczy w związku między KFW a zdolnościami poznawczymi?

### 5.4. Analizy eksploracyjne
- Analiza skupień (clustering) na podstawie zmiennych KFW + poznawczych — identyfikacja profili użytkowników
- Analiza trendu RT w trakcie 30 prób SART (czy uwaga pogarsza się z czasem?)
- Porównanie fluencji semantycznej w różnych kategoriach (miasto vs zwierzę vs zawód)
- Analiza krzywej uczenia się w Digit Span (czy span rośnie w kolejnych próbach?)
- Analiza trendu dystansu Levenshteina w funkcji spanu — czy błędy stają się większe przy dłuższych sekwencjach?
- Porównanie `mean_lev_norm` między grupami KFW vs nie-KFW — czy użytkownicy KFW popełniają "większe" błędy?
- Rozkład dystansu Levenshteina w zależności od typu błędu (zamiana sąsiednich cyfr vs całkowicie inna sekwencja)

---

## 6. Struktura bazy danych — encje

```
User (UUID)
├── 1:1 → Habits (daily_SFV_time, daily_SFV_sessions, platforms M2M, content_types M2M)
├── 1:N → Answer (question FK, answer text) — kwestionariusz
├── 1:N → DigitSpanResult (span, sequence, user_answer, correct) — pamięć robocza
├── 1:1 → SARTResult (commission, omission, mean_rt, trials_data) — uwaga
└── 1:1 → VerbalFluencyResult (trials_data JSON) — fluencja

Question
└── M2M → AnswerOption (value, label)

VerbalFluencyCategory (Miasto, Zwierzę, …)
└── 1:N → VerbalFluencyTrial (letter, time_limit)
```

---

## 7. Agregacja danych

Do celów analitycznych każdy użytkownik może być reprezentowany jako jeden wiersz z następującymi kolumnami:

| Kolumna | Źródło |
|--------|--------|
| `user_id` | `User.id` |
| `age` | `User.age` |
| `gender` | `User.gender` |
| `education` | `User.education` |
| `is_watching_SFV` | `User.is_watching_SFV` |
| `is_on_mobile` | `User.is_on_mobile` |
| `daily_SFV_time` | `Habits.daily_SFV_time` (lub NULL) |
| `daily_SFV_sessions` | `Habits.daily_SFV_sessions` (lub NULL) |
| `asrs_a_score` | Suma Answer.answer dla Question.category = 'ASRS-A' |
| `asrs_b_score` | Suma Answer.answer dla Question.category = 'ASRS-B' |
| `asrs_total` | `asrs_a` + `asrs_b` |
| `maas_mean` | Średnia Answer.answer dla Question.category = 'MAAS' |
| `mpats_total` | Suma Answer.answer dla Question.category = 'MPATS' |
| `ttas_total` | Suma Answer.answer dla Question.category = 'TTAS' |
| `ds_max_span` | `MAX(DigitSpanResult.span)` |
| `ds_span_correct` | `MAX(span) WHERE correct=True` |
| `ds_total_trials` | `COUNT(DigitSpanResult)` |
| `ds_accuracy` | `AVG(DigitSpanResult.correct)` |
| `ds_mean_lev_norm` | Średnia `levenshtein(sequence, user_answer) / span` ze wszystkich prób |
| `ds_mean_lev_norm_errors` | Średnia `lev_norm` tylko dla prób gdzie `correct=False` |
| `ds_lev_at_max_span` | `lev_norm` dla próby o najwyższym `span` |
| `ds_near_correct_ratio` | Odsetek prób z `lev_norm <= 0.5` |
| `sart_commission` | `SARTResult.commission_errors` |
| `sart_omission` | `SARTResult.omission_errors` |
| `sart_mean_rt` | `SARTResult.mean_reaction_time` |
| `vf_total_words` | Suma długości `words` we wszystkich próbach z `trials_data` |
| `added_at` | `User.added_at` |
