import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Locra", layout="wide", page_icon="🗺️")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .score-card { background: #1e2130; border-radius: 12px; padding: 16px; margin: 8px 0; }
    .score-title { font-size: 13px; color: #888; margin-bottom: 4px; }
    .score-value { font-size: 24px; font-weight: 600; }
    .bar-bg { background: #2d3148; border-radius: 4px; height: 8px; margin-top: 6px; }
    .bar-fill { height: 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

import json

with open("scores.json", "r", encoding="utf-8") as f:
    scores_data = json.load(f)

persona_weights = {
    "🏠 Ümumi":     {"məktəb": 1, "xəstəxana": 1, "aptek": 1, "kafe": 1, "bank/ATM": 1, "metro": 1},
    "👨‍👩‍👧 Ailə":      {"məktəb": 3, "xəstəxana": 2, "aptek": 2, "kafe": 0.5, "bank/ATM": 1, "metro": 1},
    "🎓 Tələbə":    {"məktəb": 0.5, "xəstəxana": 0.5, "aptek": 1, "kafe": 3, "bank/ATM": 1, "metro": 3},
    "💼 İşçi":      {"məktəb": 0.5, "xəstəxana": 1, "aptek": 1, "kafe": 2, "bank/ATM": 2, "metro": 3},
    "🏥 Yaşlı":     {"məktəb": 0.2, "xəstəxana": 3, "aptek": 3, "kafe": 0.5, "bank/ATM": 2, "metro": 1},
}

def weighted_score(data, weights):
    cats = ["məktəb", "xəstəxana", "aptek", "kafe", "bank/ATM", "metro"]
    total = sum(data[c] * weights[c] for c in cats)
    max_possible = sum(100 * weights[c] for c in cats)
    return round(total / max_possible * 100)

def score_color(s):
    if s >= 80: return "#22c55e"
    if s >= 60: return "#f59e0b"
    return "#ef4444"

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Locra")
    st.markdown("*Bakı məhəllə skoru*")
    st.divider()

    persona = st.radio("**Persona**", list(persona_weights.keys()))
    weights = persona_weights[persona]

    st.divider()
    st.markdown("**Məhəllələr**")
    for name, data in scores_data.items():
        s = weighted_score(data, weights)
        color = score_color(s)
        st.markdown(f"""
        <div class='score-card'>
            <div class='score-title'>{name}</div>
            <div class='score-value' style='color:{color}'>{s}</div>
            <div class='bar-bg'><div class='bar-fill' style='width:{s}%;background:{color}'></div></div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    m = folium.Map(location=[40.3853, 49.8622], zoom_start=12,
                   tiles="CartoDB dark_matter")

    for name, data in scores_data.items():
        s = weighted_score(data, weights)
        color = score_color(s)

        folium.CircleMarker(
            location=[data["lat"], data["lon"]],
            radius=35,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(f"""
                <div style='font-family:sans-serif;min-width:160px'>
                <b style='font-size:15px'>{name}</b><br><br>
                <b style='color:{color};font-size:20px'>{s}/100</b><br><br>
                📚 Məktəb: {data['məktəb']}<br>
                🏥 Xəstəxana: {data['xəstəxana']}<br>
                💊 Aptek: {data['aptek']}<br>
                ☕ Kafe: {data['kafe']}<br>
                🏦 Bank/ATM: {data['bank/ATM']}<br>
                🚇 Metro: {data['metro']}
                </div>
            """, max_width=220),
            tooltip=folium.Tooltip(f"<b>{name}</b>: {s}/100")
        ).add_to(m)

    result = st_folium(m, width=1000, height=620)