import streamlit as st
import datetime
import pandas as pd

# Mobielvriendelijke pagina-instellingen
st.set_page_config(page_title="Vakantie Planner", page_icon="📅", layout="centered")

# 1. Berekening van Nederlandse feestdagen (inclusief variabele data zoals Pasen/Pinksteren)
def get_nederlandse_feestdagen(year):
    # Paasdatum berekenen via het Anonymous Gregorian algorithm
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
    
    # Vaste feestdagen
    feestdagen = [
        {"datum": datetime.date(year, 1, 1), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Nieuwjaarsdag"},
        {"datum": datetime.date(year, 4, 27), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Koningsdag"},
        {"datum": datetime.date(year, 5, 5), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Bevrijdingsdag"},
        {"datum": datetime.date(year, 12, 25), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Eerste Kerstdag"},
        {"datum": datetime.date(year, 12, 26), "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Tweede Kerstdag"},
    ]
    
    # Variabele feestdagen gekoppeld aan Pasen
    goede_vrijdag = pasen - datetime.timedelta(days=2)
    paas2 = pasen + datetime.timedelta(days=1)
    hemelvaart = pasen + datetime.timedelta(days=39)
    pinkster2 = pasen + datetime.timedelta(days=50)
    
    feestdagen.append({"datum": goede_vrijdag, "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Goede Vrijdag"})
    feestdagen.append({"datum": paas2, "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Tweede Paasdag"})
    feestdagen.append({"datum": hemelvaart, "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Hemelvaartstag"})
    feestdagen.append({"datum": pinkster2, "aantal_dagen": 1.0, "categorie": "Nederlandse Feestdag", "omschrijving": "Tweede Pinksterdag"})
    
    return pd.DataFrame(feestdagen)

# 2. Database initialisatie in het geheugen van de app
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['datum', 'aantal_dagen', 'categorie', 'omschrijving'])
if 'basis_dagen' not in st.session_state:
    st.session_state.basis_dagen = 25.0

# 3. Jaar navigatie
if 'geselecteerd_jaar' not in st.session_state:
    st.session_state.geselecteerd_jaar = datetime.date.today().year

st.title("🌴 Mijn Dagen Tracker")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("◀ Vorige"):
        st.session_state.geselecteerd_jaar -= 1
with col2:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.geselecteerd_jaar}</h3>", unsafe_allow_html=True)
with col3:
    if st.button("Volgende ▶"):
        st.session_state.geselecteerd_jaar += 1

jaar = st.session_state.geselecteerd_jaar

# Automatische feestdagen ophalen voor berekening van dit jaar
df_automatische_feestdagen = get_nederlandse_feestdagen(jaar)

# 4. Logica voor het berekenen en meenemen van vakantiedagen
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

# Bereken statistieken voor overige categorieën
df_huidig_jaar = st.session_state.events[pd.to_datetime(st.session_state.events['datum']).dt.year == jaar]
dagen_feest = df_automatische_feestdagen['aantal_dagen'].sum() + df_huidig_jaar[df_huidig_jaar['categorie'] == "Nederlandse Feestdag"]['aantal_dagen'].sum()
dagen_ziek = df_huidig_jaar[df_huidig_jaar['categorie'] == "Ziekte"]['aantal_dagen'].sum()
dagen_verlof = df_huidig_jaar[df_huidig_jaar['categorie'] == "Bijzonder Verlof"]['aantal_dagen'].sum()

# 5. Mobiele Tabs interface
tab1, tab2, tab3 = st.tabs(["📊 Status", "➕ Invullen", "📜 Logboek"])

with tab1:
    st.subheader("🟢 Vakantiedagen Saldo")
    st.metric(label="Totaal Budget (incl. meenemen)", value=f"{budget} dagen")
    st.metric(label="Opgenomen vakantie", value=f"{opgenomen_vakantie} dagen")
    st.metric(label="Resterend (gaat mee)", value=f"{over_vakantie} dagen")
    
    progress = min(1.0, max(0.0, (over_vakantie / budget))) if budget > 0 else 0
    st.progress(progress, text=f"{int(progress*100)}% van je vakantiedagen over")
    
    st.divider()
    st.subheader("🔵 Overige Geregistreerde Dagen")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="Feestdagen", value=f"{dagen_feest} d")
    with col_b:
        st.metric(label="Ziekte", value=f"{dagen_ziek} d")
    with col_c:
        st.metric(label="Bijz. Verlof", value=f"{dagen_verlof} d")

with tab2:
    st.subheader("Nieuwe dag registreren")
    with st.form("vakantie_form", clear_on_submit=True):
        datum = st.date_input("Datum", datetime.date(jaar, 1, 1))
        categorie = st.selectbox("Type dag", ["Vakantie", "Nederlandse Feestdag", "Ziekte", "Bijzonder Verlof"])
        dagen = st.number_input("Aantal dagen", min_value=0.5, max_value=30.0, value=1.0, step=0.5)
        info = st.text_input("Omschrijving (bijv. Zomervakantie, Tandarts)")
        
        submit = st.form_submit_button("Opslaan en Verwerken")
        if submit:
            # Zorg dat de datum een echt date-object blijft
            nieuw_event = pd.DataFrame([[pd.to_datetime(datum).date(), dagen, categorie, info]], columns=['datum', 'aantal_dagen', 'categorie', 'omschrijving'])
            st.session_state.events = pd.concat([st.session_state.events, nieuw_event], ignore_index=True)
            st.success(f"{categorie} succesvol toegevoegd!")
            st.rerun()

with tab3:
    st.subheader(f"Overzicht van {jaar}")
    
    # Haal eigen invoer op en zorg dat data juist geformatteerd zijn
    df_eigen = st.session_state.events.copy()
    if not df_eigen.empty:
        df_eigen['datum'] = pd.to_datetime(df_eigen['datum']).dt.date
        df_eigen = df_eigen[pd.to_datetime(df_eigen['datum']).dt.year == jaar]
    
    # Toon automatische feestdagen
    st.markdown("**📅 Officiële Feestdagen (Automatisch)**")
    df_auto_sorted = df_automatische_feestdagen.sort_values(by='datum')
    st.dataframe(df_auto_sorted[['datum', 'categorie', 'omschrijving']], use_container_width=True, hide_index=True)
    
    st.divider()
    st.markdown("**📝 Jouw Eigen Registraties (Met verwijderknop)**")
    
    if not df_eigen.empty:
        df_eigen = df_eigen.sort_values(by='datum')
        
        # Mobielvriendelijke lijst met handige verwijderknoppen per regel
        for idx, row in df_eigen.iterrows():
            col_tekst, col_knop = st.columns([4, 1])
            with col_tekst:
                st.markdown(f"**{row['datum'].strftime('%d-%m')}** | {row['categorie']} ({row['aantal_dagen']} d)  \n*{row['omschrijving']}*")
            with col_knop:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.events = st.session_state.events.drop(idx).reset_index(drop=True)
                    st.success("Verwijderd!")
                    st.rerun()
            st.markdown("<hr style='margin:5px 0px; border-color:#eee;'/>", unsafe_allow_html=True)
    else:
        st.info("Je hebt zelf nog geen dagen ingevoerd voor dit jaar.")
