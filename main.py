import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Titel der App
st.title("Simulationsergebnisse Auswertung")

# Seitenleiste für die Auswahl
st.sidebar.header("Einstellungen")

# Datei-Upload
uploaded_file = st.sidebar.file_uploader("Lade eine Excel-Datei hoch", type=["xlsx"])

if uploaded_file is not None:
    # Lade die Daten
    data = pd.read_excel(uploaded_file)

    # Annahme: Der Simulation beginnt am 1. Januar eines Jahres
    start_date = datetime(datetime.now().year, 1, 1)

    # Hinzufügen einer Spalte für das Datum basierend auf der Stunde
    data['Datum'] = data['Stunde'].apply(lambda x: start_date + timedelta(hours=x-1))

    # Auswahl der Räume und Parameter
    räume = [col.split(' ')[0] for col in data.columns if 'Lufttemperatur' in col or 'Heizlast' in col or 'Kühllast' in col]
    räume = list(set(räume))  # Einzigartige Räume

    ausgewählte_räume = st.sidebar.multiselect("Wähle die Räume", räume, default=räume[0])

    parameter_options = ["Lufttemperatur", "Heizlast", "Kühllast"]
    parameter = st.sidebar.selectbox("Wähle den Parameter", parameter_options)

    # Option zur Anzeige der Außentemperatur
    show_ausstemp = st.sidebar.checkbox("Außentemperatur anzeigen", value=False)

    # Zeitraum-Auswahl über Datum
    start_date_input = st.sidebar.date_input("Startdatum", start_date.date())
    end_date_input = st.sidebar.date_input("Enddatum", (start_date + timedelta(days=364)).date())

    # Konvertierung der Datumsangaben in Stunden
    start_hour = int((datetime.combine(start_date_input, datetime.min.time()) - start_date).total_seconds() // 3600) + 1
    end_hour = int((datetime.combine(end_date_input, datetime.min.time()) - start_date).total_seconds() // 3600) + 24

    # Daten filtern
    filtered_data = data[(data['Stunde'] >= start_hour) & (data['Stunde'] <= end_hour)]
    columns_to_plot = [col for col in data.columns if any(raum in col for raum in ausgewählte_räume) and parameter in col]

    if len(columns_to_plot) > 0 or show_ausstemp:
        # Daten für die ausgewählten Räume und den Parameter zusammenstellen
        chart_data = pd.DataFrame({
            'Datum': filtered_data['Datum']
        })

        for column in columns_to_plot:
            chart_data[column] = filtered_data[column]

        # Außentemperatur hinzufügen, falls ausgewählt
        if show_ausstemp:
            chart_data['Außentemperatur (°C)'] = filtered_data['Außentemperatur (°C)']

        # Achsenbeschriftungen je nach Parameter
        y_axis_label = f"{parameter} (°C)" if parameter == "Lufttemperatur" else f"{parameter} (W)"

        # Erstellen der Grafik mit Altair
        chart = alt.Chart(chart_data.melt('Datum')).mark_line().encode(
            x=alt.X('Datum:T', title='Datum'),
            y=alt.Y('value', title=y_axis_label, scale=alt.Scale(zero=False)),
            color='variable',
            tooltip=['Datum:T', 'variable', 'value']
        ).properties(
            width=800,
            height=400
        ).interactive()

        st.altair_chart(chart)
    else:
        st.write("Keine Daten für die ausgewählten Optionen gefunden.")
else:
    st.write("Bitte lade eine Datei hoch, um fortzufahren.")
