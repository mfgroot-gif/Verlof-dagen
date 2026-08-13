import streamlit as st
import datetime
import pandas as pd
import calendar

# Mobielvriendelijke pagina-instellingen en styling basis
st.set_page_config(page_title="Verlof Registratie", page_icon="📅", layout="centered")

# CSS toevoegen voor een modern, zakelijk en minimalistisch design (Corporate Style)
st.markdown("""
    <style>
        /* Algemene app achtergrond en lettertype */
        .stApp {
            background-color: #F8FAFC;
            color: #334155;
            font-family: 'Inter', -apple-system, sans-serif;
        }
        
        /* Grote titels en subkoppen */
        h1 {
            color: #0F172A !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em;
            padding-bottom: 20px;
        }
        h3, h4 {
            color: #1E293B !important;
            font-weight: 600 !important;
        }
        
        /* Zakelijke knoppen */
        .stButton>button {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 8px 16px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #0F172A !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Formulieren en invoervelden */
        .stForm {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }
        
        /* Tabbladen strakker maken */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 8px 16px;
            color: #64748B;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border-color: #1E293B !important;
        }
        
        /* Kalender styling */
        .cal-header {
            text-align: center;
            font-weight: 600;
            color: #475569;
            padding: 6px 0;
        }
        .cal-day-empty {
            text-align: center;
            padding: 10px 0;
        }
        .cal-day-normal {
            text-align: center;
            padding: 10px 0;
            color: #64748B;
            font-size: 0.95rem;
        }
        .cal-day-marked {
            background-color: #F1F5F9;
            color: #0F172A;
            font-weight: 600;
            padding: 10px 0;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #CBD5E1;
        }
        
        /* Logboek regels */
        .log-item {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# 1. Berekening van Nederlandse feestdagen
def get_nederlandse_feestdagen(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) // 451
    month = (h + L - 7 * m + 114) // 31
    day = (h + L - 7 * m + 114) % 31 + 1
    pasen = datetime.date(year, month, day)
    
    feestdagen = [
        {"datum": datetime.date(year, 1, 1), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Nieuwjaarsdag"},
        {"datum": datetime.date(year, 4, 27), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Koningsdag"},
        {"datum": datetime.date(year, 5, 5), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Bevrijdingsdag"},
        {"datum": datetime.date(year, 12, 25), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Eerste Kerstdag"},
        {"datum": datetime.date(year, 12, 26), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Tweede Kerstdag"},
    ]
    
    feestdagen.append({"datum": pasen - datetime.timedelta(days=2), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Goede Vrijdag"})
    feestdagen.append({"datum": pasen + datetime.timedelta(days=1), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Tweede Paasdag"})
    feestdagen.append({"datum": pasen + datetime.timedelta(days=39), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Hemelvaartsdag"})
    feestdagen.append({"datum": pasen + datetime.timedelta(days=50), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Tweede Pinksterdag"})
    
    return pd.DataFrame(feestdagen)

# 2. Database initialisatie
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['datum', 'aantal_dagen', 'categorie', 'omschrijving'])
if 'basis_dagen' not in st.session_state:
    st.session_state.basis_dagen = 25.0

# 3. Jaar navigatie
if 'geselecteerd_jaar' not in st.session_state:
    st.session_state.geselecteerd_jaar = datetime.date.today().year

st.title("👨‍💻 Verlof & Vakantie Manager")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("◀ Vorige"):
        st.session_state.geselecteerd_jaar -= 1
with col2:
    st.markdown(f"<h3 style='text-align: center; margin-top: 0;'>Jaar {st.session_state.geselecteerd_jaar}</h3>", unsafe_allow_html=True)
with col3:
    if st.button("Volgende ▶"):
        st.session_state.geselecteerd_jaar += 1

jaar = st.session_state.geselecteerd_jaar
df_automatische_feestdagen = get_nederlandse_feestdagen(jaar)

# 4. Logica voor berekening van het saldo
def bereken_jaar_balans(target_year):
    start_jaar = 2025
    meegenomen = 0.0
    
    for y in range(start_jaar, target_year + 1):
        df_jaar_vakantie = st.session_state.events[
            (pd.to_datetime(st.session_state.events['datum']).dt.year == y) & 
            (st.session_state.events['categorie'] == "Vakantie")
        ]
        opgenomen = df_jaar_vakantie['aantal_dagen'].sum()
        totaal_budget = st.session_state.basis_dagen + meegenomen
        over = totaal_budget - opgenomen
        
        if y == target_year:
            return totaal_budget, opgenomen, over
        meegenomen = max(0.0, over) 
    return st.session_state.basis_dagen, 0.0, st.session_state.basis_dagen

budget, opgenomen_vakantie, over_vakantie = bereken_jaar_balans(jaar)

df_huidig_jaar = st.session_state.events[pd.to_datetime(st.session_state.events['datum']).dt.year == jaar]
dagen_feest = df_automatische_feestdagen['aantal_dagen'].sum() + df_huidig_jaar[df_huidig_jaar['categorie'] == "Nederlandse Feestdag"]['aantal_dagen'].sum()
dagen_ziek = df_huidig_jaar[df_huidig_jaar['categorie'] == "Ziekte"]['aantal_dagen'].sum()
dagen_verlof = df_huidig_jaar[df_huidig_jaar['categorie'] == "Bijzonder Verlof"]['aantal_dagen'].sum()

# 5. Moderne Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Maand", "Invoeren", "Overzicht"])

with tab1:
    st.subheader("Instellingen")
    st.session_state.basis_dagen = st.number_input(
        "Jaarlijks basisbudget (dagen):", 
        min_value=0.0, max_value=100.0, 
        value=st.session_state.basis_dagen, step=1.0
    )
    
    st.divider()
    st.subheader("Status Vakantiedagen")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="Totaal Budget", value=f"{budget} d")
    col_m2.metric(label="Opgenomen", value=f"{opgenomen_vakantie} d")
    col_m3.metric(label="Resterend", value=f"{over_vakantie} d")
    
    progress = min(1.0, max(0.0, (over_vakantie / budget))) if budget > 0 else 0
    st.progress(progress)
    
    st.divider()
    st.subheader("Overige Categorieën")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric(label="Feestdagen", value=f"{dagen_feest} d")
    col_b.metric(label="Ziekteverzuim", value=f"{dagen_ziek} d")
    col_c.metric(label="Bijzonder Verlof", value=f"{dagen_verlof} d")

with tab2:
    st.subheader("Maandelijkse Kalender")
    maanden_nl = ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"]
    gekozen_maand_naam = st.selectbox("Selecteer maand", maanden_nl, index=datetime.date.today().month - 1)
    maand_nr = maanden_nl.index(gekozen_maand_naam) + 1
    
    df_eigen_maand = st.session_state.events.copy()
    if not df_eigen_maand.empty:
        df_eigen_maand['datum'] = pd.to_datetime(df_eigen_maand['datum']).dt.date
        df_eigen_maand = df_eigen_maand[(pd.to_datetime(df_eigen_maand['datum']).dt.year == jaar) & (pd.to_datetime(df_eigen_maand['datum']).dt.month == maand_nr)]
    
    df_feest_maand = df_automatische_feestdagen[(pd.to_datetime(df_automatische_feestdagen['datum']).dt.year == jaar) & (pd.to_datetime(df_automatische_feestdagen['datum']).dt.month == maand_nr)]
    
    alle_maand_dagen = {}
    for _, row in df_feest_maand.iterrows():
        alle_maand_dagen[row['datum'].day] = f"[Feestdag] {row['omschrijving']}"
    if not df_eigen_maand.empty:
        for _, row in df_eigen_maand.iterrows():
            alle_maand_dagen[row['datum'].day] = f"[{row['categorie']}] {row['omschrijving']} ({row['aantal_dagen']}d)"

    cal = calendar.monthcalendar(jaar, maand_nr)
    
    # Weekdagen headers via strakke HTML kolommen
    cols_header = st.columns(7)
    weekdagen = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
    for i, col in enumerate(cols_header):
