# Arhitektura — faza 1

Preverjeno: 23. oktober 2026.

```text
ActivitySource (zamenljiv vmesnik)
  -> FitDirectorySource (faza 1)
  -> GarminPersonalApiSource (načrtovana faza 2)
       |
       v
FitActivityParser -> ActivityAnalyzer -> SQLiteActivityRepository
                                              |
                                      CLI / Streamlit UI
                                              |
                                  ClaudeReportService (faza 2)
```

## Meje modulov

- `sources`: odkrivanje aktivnosti; ne pozna SQLite ali UI.
- `fit_parser`: pretvorba FIT sporočil v notranji model brez poslovne logike.
- `analyzer`: vsi deterministični izračuni; Claude ne računa statistik.
- `repository`: SQLite, transakcije in deduplikacija po SHA-256 vsebine.
- `sync`: orkestracija in izolacija napake posamezne datoteke.
- `app.py` in `cli.py`: tanki vstopni točki.

Naslednja faza doda uradni Garmin Personal API adapter in Claude poročila nad
agregiranimi podatki. Poslovni push/ping adapter bo lahko implementiral isti
`ActivitySource`, če bo projekt kdaj služil več uporabnikom.

## Podatkovni model faze 1

SQLite hrani agregate, čase v območjih srčnega utripa in časovno vrsto brez GPS
koordinat. Izvorni FIT ostane v uporabnikovi mapi. `content_hash` je UNIQUE, zato
preimenovanje iste datoteke ne sproži ponovne analize.

## Odvisnosti

- `garmin-fit-sdk`: uradni dekoder FIT (in generator testnega vzorca).
- `streamlit`, `plotly`: lokalna nadzorna plošča.
- `python-dotenv`: lokalna konfiguracija brez skrivnosti v kodi.
- `anthropic`: rezerviran za fazo 2; prototip ga še ne kliče.
- Pythonov `sqlite3`, `logging`: baza in dnevniki brez dodatnega strežnika.

