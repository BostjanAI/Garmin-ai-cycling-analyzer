from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from cycling_analyzer.bootstrap import build_repository, build_sync_service, configure_logging
from cycling_analyzer.config import Settings

st.set_page_config(page_title="Garmin AI Cycling Analyzer", layout="wide")
settings = Settings.from_env()
configure_logging(settings.log_level)
repository = build_repository(settings)

st.title("Garmin AI Cycling Analyzer")
st.caption("Faza 1 · lokalni FIT uvoz in deterministična analiza; brez pošiljanja v Claude")

left, right = st.columns([1, 3])
with left:
    if st.button("Sinhroniziraj FIT mapo", type="primary"):
        result = build_sync_service(settings).sync()
        if result.errors:
            st.error("\n".join(result.errors))
        st.success(f"Uvoženo: {result.imported}, preskočeno: {result.skipped}")

    with st.expander("Nastavitve in zasebnost"):
        st.write(f"FIT mapa: `{settings.fit_inbox}`")
        st.write(f"Najvišji srčni utrip: {settings.max_heart_rate} bpm")
        st.info("GPS koordinat ne shranjujemo. Faza 1 ne uporablja zunanjega AI API-ja.")
        confirm = st.checkbox("Potrjujem izbris vseh lokalnih analiz")
        if st.button("Izbriši lokalne podatke", disabled=not confirm):
            count = repository.delete_all()
            st.success(f"Izbrisanih aktivnosti: {count}")
            st.rerun()

activities = repository.list_all()
with right:
    st.metric("Shranjene vožnje", len(activities))

if not activities:
    st.info("V mapo fit_inbox dodajte datoteko .fit in izberite sinhronizacijo.")
    st.stop()

labels = [f"{item['started_at'][:10]} · {item['source_name']}" for item in activities]
selected_label = st.selectbox("Aktivnost", labels)
activity = activities[labels.index(selected_label)]

metrics = st.columns(6)
metrics[0].metric("Razdalja", f"{(activity['distance_m'] or 0) / 1000:.1f} km")
metrics[1].metric("Trajanje", f"{(activity['duration_s'] or 0) / 60:.0f} min")
metrics[2].metric("Povp. hitrost", f"{activity['avg_speed_kmh'] or 0:.1f} km/h")
metrics[3].metric("Povp. utrip", f"{activity['avg_heart_rate'] or 0:.0f} bpm")
metrics[4].metric("Višinski metri", f"{activity['elevation_gain_m'] or 0:.0f} m")
power_label = "—" if activity["avg_power"] is None else f"{activity['avg_power']:.0f} W"
metrics[5].metric("Povp. moč", power_label)

records = activity["records"]
hr_records = [record for record in records if record.heart_rate is not None]
if hr_records:
    figure = go.Figure(
        go.Scatter(
            x=[record.timestamp for record in hr_records],
            y=[record.heart_rate for record in hr_records],
            mode="lines",
            name="Srčni utrip",
        )
    )
    figure.update_layout(title="Srčni utrip skozi trening", xaxis_title="Čas", yaxis_title="bpm")
    st.plotly_chart(figure, width="stretch")
else:
    st.warning("Ta aktivnost nima podatkov o srčnem utripu.")

st.subheader("Čas v območjih srčnega utripa")
zones = activity["hr_zones_s"]
zone_figure = go.Figure(go.Bar(x=list(zones), y=[value / 60 for value in zones.values()]))
zone_figure.update_layout(yaxis_title="minute", xaxis_title="območje")
st.plotly_chart(zone_figure, width="stretch")

st.subheader("AI poročilo")
st.info("Claude interpretacija agregatov bo dodana v fazi 2 po potrditvi faze 1.")

