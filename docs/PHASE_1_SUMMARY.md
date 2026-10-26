# Povzetek faze 1

Zaključeno: 26. oktober 2026.

## Opravljeno

- preverjene aktualne uradne možnosti Garmin Connect (Personal API, Business API,
  Activity API in FIT SDK), brez uporabe zasebnih endpointov;
- modularna meja `ActivitySource` in delujoč `FitDirectorySource`;
- FIT preslikava, izračun hitrosti, utripa, območij, kadence, vzpona, moči in
  spremembe utripa med polovicama aktivnosti;
- varna obravnava manjkajočih polj;
- SQLite shramba brez GPS koordinat in deduplikacija po SHA-256 vsebine;
- ponovljiv CLI uvoz, izolacija napak posamezne datoteke in rotirajoči dnevnik;
- minimalna Streamlit nadzorna plošča, graf utripa, območja in izbris lokalnih analiz;
- generator veljavne vzorčne FIT vožnje po uradnem Garminovem zaporedju sporočil;
- `.env.example`, `.gitignore`, navodila za Windows in deklarirane odvisnosti.

## Preverjanje

- 6 testov uspešno: izračuni, manjkajoči podatki, preslikava FIT sporočil, napaka
  dekoderja, SQLite/deduplikacija/izbris in ponovljena sinhronizacija;
- preverjanje sintakse vseh Python modulov uspešno;
- CLI smoke test z novo prazno bazo uspešen;
- dodatni end-to-end test generator -> Garmin decoder -> analiza je pripravljen,
  vendar v upravljanem razvojnem okolju preskočen, ker je okolje blokiralo vsak
  prenos paketa `garmin-fit-sdk`. Na ciljnem Windows računalniku se izvede po
  `pip install -e ".[dev]"`.

## Odprte omejitve

- ni še preverjeno z uporabnikovo dejansko datoteko iz Edge 530;
- faza 1 obravnava prvo sejo v FIT datoteki, ne multisport datotek;
- območja so trenutno odstotki nastavljivega `MAX_HEART_RATE`, ne uporabnikova
  območja iz Garmin Connect;
- Garmin Personal API adapter, Claude interpretacija, primerjave trendov in
  dokončna nastavitev Windows Task Schedulerja še niso implementirani.

## Predlog faze 2

1. Na ciljnem Windows okolju izvesti polni FIT test in uvoz ene anonimizirane
   datoteke Edge 530.
2. Dodati uradni Garmin Personal API adapter z obnovo 24-urnega access tokena,
   časovnimi omejitvami, ponovnimi poskusi in prenosom FIT aktivnosti.
3. Dodati Claude storitev s privzetim pošiljanjem samo agregatov, predogledom
   payload-a in izrecnim uporabnikovim soglasjem.
4. Nato razširiti UI s trendi, primerjavo voženj in nastavitvijo opravila za
   Windows Task Scheduler.

