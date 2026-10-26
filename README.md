# Garmin AI Cycling Analyzer

Faza 1 je lokalni, delujoči prototip: poišče nove datoteke FIT, jih dekodira z
uradnim Garmin FIT SDK, izračuna osnovne kolesarske metrike, prepreči podvojene
uvoze in rezultate shrani v SQLite. Streamlit prikaže zgodovino in graf srčnega
utripa. Claude še ni klican; v tej fazi podatki ne zapustijo računalnika.

## Hiter začetek (Windows 10/11, Python 3.12+)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python scripts/generate_sample_fit.py
cycling-analyzer sync
streamlit run app.py
```

Testi in preverjanje sloga:

```powershell
pytest
ruff check .
```

Za ponavljajoč uvoz lahko Windows Task Scheduler zažene `cycling-analyzer sync`.
Uporabiti mora isti delovni imenik in virtualno okolje kot ročni zagon. Podrobna
navodila in neposredna Garmin integracija sledijo v naslednji fazi.

## Zasebnost

- `.env`, lokalna baza, dnevniki in uvožene FIT datoteke so izključeni iz Gita.
- Faza 1 ne pošilja podatkov Claudu ali drugim storitvam.
- Nadzorna plošča omogoča izbris vseh lokalno shranjenih analiz.
- Prihodnja AI integracija bo privzeto pošiljala le izračunane agregate, brez GPS sledi.

Arhitektura in Garminova raziskava sta v [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
in [docs/GARMIN_INTEGRATION.md](docs/GARMIN_INTEGRATION.md). Rezultati, omejitve
in naslednji koraki so v [docs/PHASE_1_SUMMARY.md](docs/PHASE_1_SUMMARY.md).

