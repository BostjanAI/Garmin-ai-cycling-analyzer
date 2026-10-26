# Preverjanje dostopa do Garmin Connect

Stanje je bilo preverjeno 23. oktobra 2026 na uradnih Garminovih straneh. Ta
dokument namenoma ne uporablja neuradnih prijavnih knjižnic in ne ugiba endpointov.

## Ugotovitve

1. **Garmin Connect Personal API** je najprimernejša neposredna pot za ta osebni
   projekt. Namenjen je dostopu posameznika do lastnih podatkov in ne komercialnim
   aplikacijam z več uporabniki. Ključ se ustvari v Garmin Connect Web, lahko velja
   30, 90, 180 dni ali eno leto, prikazan je le enkrat in ga je mogoče preklicati.
   Ključ se z uradno dokumentiranim token postopkom zamenja za OAuth2 access token;
   token velja 24 ur oziroma do poteka ključa in nima refresh tokena.

2. Uradna Swagger dokumentacija navaja iskanje aktivnosti, podrobnosti aktivnosti,
   območja srčnega utripa in prenos datoteke aktivnosti. Implementacijo neposrednega
   adapterja zato lahko izvedemo brez zasebnih Garmin Connect endpointov, ko uporabnik
   ustvari ključ. Ključa se ne bo shranjevalo v SQLite, temveč samo v `.env`.

3. **Business Garmin Connect Developer Program** je namenjen aplikacijam z več
   uporabniki. Starter dostop je omejen, uporablja push in nima zgodovinskih podatkov;
   Enterprise ponuja push ali ping/pull, zgodovino in večjo kapaciteto po dogovoru.
   Activity API po uporabnikovem soglasju zagotavlja podrobnosti in datoteke FIT,
   GPX ali TCX. Poslovna integracija zahteva prijavo/odobritev in je za osebni MVP
   nepotrebna.

4. **FIT uvoz** je uradna, lokalna rezervna pot. Garminov Python FIT SDK dekodira
   FIT datoteke, ki vsebujejo seje in časovne zapise senzorjev. Deluje brez strežnika,
   brez Garmin poverilnic in je zato uporabljena pot v fazi 1.

## Uradni viri

- Personal API FAQ: https://developer.garmin.com/gc-developer-program/personal/personal-faq/
- Personal API Swagger: https://developer.garmin.com/gc-developer-program/personal/swagger-docs/
- Pregled programa in ravni dostopa: https://developer.garmin.com/gc-developer-program
- Activity API: https://developer.garmin.com/gc-developer-program/activity-api/
- Uradni Python FIT SDK: https://developer.garmin.com/fit/get-the-sdk/
- FIT activity format: https://developer.garmin.com/fit/articles/file-types/activity.html

## Odločitev faze 1

Implementiran je `ActivitySource` vmesnik in `FitDirectorySource`. Personal API
adapter je naslednji korak, ker za integracijski preizkus potrebujemo uporabnikov
ključ. Do takrat FIT pot ni simulacija: uporablja isti uradni format aktivnosti,
ki ga zagotavlja tudi Activity API.

