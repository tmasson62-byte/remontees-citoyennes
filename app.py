"""
Remontées Citoyennes — Ville de Marck
Application web Streamlit — Migration depuis Tkinter
Base de données : JSON local (dev) ou Google Sheets (prod)
"""

import streamlit as st
import json
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuration de la page ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Remontées Citoyennes — Ville de Marck",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Charte graphique Ville de Marck ──────────────────────────────────────────
ROUGE       = "#C8202E"
ROUGE_DARK  = "#9E1922"
ROUGE_LIGHT = "#F5E6E7"
BLEU        = "#3AADE4"
BLEU_DARK   = "#1E86BC"
BLEU_LIGHT  = "#EAF6FD"
OR          = "#F0B429"
GRIS_TITRE  = "#58595B"
GRIS_DARK   = "#3A3B3C"
GRIS_MED    = "#7A7B7D"
GRIS_LIGHT  = "#E8E9EA"
BLANC       = "#FFFFFF"
FOND_PAGE   = "#F4F5F6"
VERT        = "#2E8B57"

PRIORITE_COULEURS = {
    "Faible":  "#2E8B57",
    "Normale": "#3AADE4",
    "Élevée":  "#E07B20",
    "Urgente": "#C8202E",
}
DELAIS = {"Faible": 15, "Normale": 10, "Élevée": 5, "Urgente": 2}

CATEGORIES = [
    "Voirie & Mobilité", "Espaces verts & Propreté", "Éclairage public",
    "Bâtiments communaux", "Nuisances sonores", "Sécurité & Incivilités",
    "Eau & Assainissement", "Déchets & Collecte", "Transports en commun",
    "Stationnement", "Accessibilité PMR", "Événements & Vie locale", "Autre",
]
PRIORITES       = ["Faible", "Normale", "Élevée", "Urgente"]
STATUTS         = ["Nouveau", "En cours", "En attente", "Résolu", "Archivé"]
TYPES_DECLARANT = ["Citoyen", "Agent municipal", "Élu", "Association", "Entreprise"]

# ─── CSS personnalisé — Charte Marck ──────────────────────────────────────────
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;600;700;800&display=swap');

    /* Reset & base */
    html, body, [data-testid="stAppViewContainer"] {{
        background: {FOND_PAGE} !important;
        font-family: 'Trebuchet MS', 'Libre Franklin', sans-serif;
    }}

    /* Masquer éléments Streamlit non désirés */
    #MainMenu, footer, header {{ visibility: hidden; }}
    [data-testid="stToolbar"] {{ display: none; }}
    .stDeployButton {{ display: none; }}

    /* Header Mairie */
    .marck-header {{
        background: {BLANC};
        border-top: 5px solid {ROUGE};
        border-bottom: 3px solid {ROUGE};
        padding: 14px 28px;
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .marck-logo-text {{
        font-size: 28px;
        font-weight: 900;
        color: {ROUGE};
        letter-spacing: 2px;
        line-height: 1;
    }}
    .marck-logo-sub {{
        font-size: 10px;
        color: {GRIS_MED};
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    .marck-title {{
        font-size: 20px;
        font-weight: 700;
        color: {GRIS_TITRE};
        line-height: 1.2;
    }}
    .marck-subtitle {{
        font-size: 12px;
        color: {GRIS_MED};
    }}
    .marck-date {{
        margin-left: auto;
        font-size: 12px;
        color: {GRIS_MED};
        text-align: right;
    }}

    /* Barre de stats */
    .stats-bar {{
        background: {GRIS_DARK};
        color: {BLANC};
        padding: 7px 20px;
        font-size: 12px;
        display: flex;
        gap: 24px;
        margin-bottom: 16px;
    }}
    .stat-item {{ display: inline-flex; align-items: center; gap: 6px; }}

    /* Cards */
    .card {{
        background: {BLANC};
        border: 1px solid {GRIS_LIGHT};
        border-radius: 6px;
        padding: 0;
        overflow: hidden;
        margin-bottom: 12px;
    }}
    .card-header {{
        background: {ROUGE};
        color: {BLANC};
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .card-body {{ padding: 16px; }}

    /* Section headers */
    .section-hdr {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 18px 0 10px 0;
        font-size: 11px;
        font-weight: 700;
        color: {ROUGE};
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }}
    .section-hdr::before {{
        content: '';
        display: block;
        width: 4px;
        height: 18px;
        background: {ROUGE};
        border-radius: 2px;
        flex-shrink: 0;
    }}
    .section-hdr::after {{
        content: '';
        flex: 1;
        height: 1px;
        background: {GRIS_LIGHT};
    }}

    /* Badge priorité */
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 700;
        color: white;
    }}
    .badge-faible  {{ background: #2E8B57; }}
    .badge-normale {{ background: #3AADE4; }}
    .badge-elevee  {{ background: #E07B20; }}
    .badge-urgente {{ background: #C8202E; }}
    .badge-nouveau {{ background: #C8202E; }}
    .badge-encours {{ background: #3AADE4; }}
    .badge-attente {{ background: #F0B429; color: #333; }}
    .badge-resolu  {{ background: #2E8B57; }}
    .badge-archive {{ background: #7A7B7D; }}

    /* Bouton date butoir */
    .butoir-badge {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 13px;
        color: white;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    }}

    /* Streamlit widgets overrides */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: #F9FAFB !important;
        border: 1px solid {GRIS_LIGHT} !important;
        border-radius: 4px !important;
        font-family: 'Trebuchet MS', sans-serif !important;
        font-size: 14px !important;
        min-height: 42px !important;
        padding: 8px 12px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {BLEU} !important;
        box-shadow: 0 0 0 2px {BLEU_LIGHT} !important;
    }}
    /* Forcer la hauteur visible des inputs */
    .stTextInput > div {{
        min-height: 44px !important;
    }}
    div[data-baseweb="input"] {{
        min-height: 42px !important;
    }}
    div[data-baseweb="input"] input {{
        min-height: 42px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }}
    div[data-baseweb="select"] > div {{
        min-height: 42px !important;
        padding: 6px 12px !important;
        font-size: 14px !important;
    }}

    /* Boutons */
    .stButton > button {{
        background: {ROUGE};
        color: white;
        border: none;
        border-radius: 4px;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 18px;
        cursor: pointer;
        transition: background 0.15s;
        min-height: 44px;
        width: 100%;
    }}
    .stButton > button:hover {{
        background: {ROUGE_DARK} !important;
        color: white !important;
        border: none !important;
    }}

    /* Bouton secondaire */
    .btn-secondary > button {{
        background: {GRIS_MED} !important;
    }}
    .btn-secondary > button:hover {{
        background: {GRIS_DARK} !important;
        color: white !important;
        border: none !important;
    }}
    .btn-blue > button {{
        background: {BLEU} !important;
    }}
    .btn-blue > button:hover {{
        background: {BLEU_DARK} !important;
        color: white !important;
        border: none !important;
    }}
    .btn-green > button {{
        background: {VERT} !important;
    }}
    .btn-green > button:hover {{
        background: #246B44 !important;
        color: white !important;
        border: none !important;
    }}

    /* Tableau signalements */
    .sig-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    .sig-table thead tr {{ background: {ROUGE}; color: white; }}
    .sig-table thead th {{ padding: 8px 10px; text-align: left; font-weight: 700; white-space: nowrap; }}
    .sig-table tbody tr {{ border-bottom: 1px solid {GRIS_LIGHT}; cursor: pointer; transition: background 0.1s; }}
    .sig-table tbody tr:hover {{ background: {BLEU_LIGHT}; }}
    .sig-table tbody tr.selected {{ background: {BLEU_LIGHT}; border-left: 3px solid {BLEU}; }}
    .sig-table tbody td {{ padding: 7px 10px; color: {GRIS_TITRE}; }}
    .sig-table tbody tr.overdue td {{ color: {ROUGE}; font-weight: 700; }}

    /* Satisfaction étoiles */
    .sat-display {{ font-size: 18px; letter-spacing: 2px; }}

    /* Séparateur */
    .sep {{ height: 1px; background: {GRIS_LIGHT}; margin: 16px 0; }}

    /* Padding global */
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    .main > div {{ padding: 0 !important; }}
    section[data-testid="stMain"] > div {{ padding: 0 !important; }}

    /* Colonnes internes */
    [data-testid="column"] {{ padding: 0 6px !important; }}

    /* Labels */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stRadio label, .stCheckbox label {{
        font-family: 'Trebuchet MS', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        color: {GRIS_MED} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 4px !important;
    }}
    /* Espacement entre les champs */
    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: 2px;
    }}

    /* Masquer le label "satisfaction" des radios */
    div[data-testid="stRadio"] > label {{ display: none; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {FOND_PAGE}; }}
    ::-webkit-scrollbar-thumb {{ background: {GRIS_LIGHT}; border-radius: 3px; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{ display: none; }}

    /* Notifications */
    .stSuccess {{ border-left: 4px solid {VERT} !important; }}
    .stWarning {{ border-left: 4px solid {OR} !important; }}
    .stError   {{ border-left: 4px solid {ROUGE} !important; }}
    </style>
    """, unsafe_allow_html=True)

# ─── Données ───────────────────────────────────────────────────────────────────
DATA_FILE = Path("remontees_citoyennes.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def next_id(records):
    nums = [int(r["id"].split("-")[1]) for r in records if "-" in r.get("id", "")]
    return f"REM-{(max(nums)+1):04d}" if nums else "REM-0001"

def calc_butoir(date_str, priorite):
    delai = DELAIS.get(priorite, 10)
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        d = datetime.now()
    return (d + timedelta(days=delai)).strftime("%d/%m/%Y"), delai

def is_overdue(rec):
    try:
        bd = datetime.strptime(rec.get("butoir", ""), "%d/%m/%Y").date()
        return bd < datetime.now().date() and rec.get("statut") not in ("Résolu", "Archivé")
    except ValueError:
        return False

# ─── Session state ─────────────────────────────────────────────────────────────
def init_state():
    if "records" not in st.session_state:
        st.session_state.records = load_data()
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None
    if "form_mode" not in st.session_state:
        st.session_state.form_mode = "new"   # "new" | "edit"
    if "search" not in st.session_state:
        st.session_state.search = ""
    if "filter_statut" not in st.session_state:
        st.session_state.filter_statut = "Tous"
    if "notif" not in st.session_state:
        st.session_state.notif = None
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

def get_selected():
    if st.session_state.selected_id:
        return next((r for r in st.session_state.records
                     if r["id"] == st.session_state.selected_id), None)
    return None

# ─── Header ────────────────────────────────────────────────────────────────────
def render_header():
    date_fr = datetime.now().strftime("%A %d %B %Y").capitalize()
    st.markdown(f"""
    <div class="marck-header">
        <div>
            <div class="marck-logo-text">MARCK</div>
            <div class="marck-logo-sub">Ville de Marck</div>
        </div>
        <div style="width:1px;background:#E8E9EA;height:48px;margin:0 8px;"></div>
        <div>
            <div class="marck-title">Gestion des Remontées Citoyennes</div>
            <div class="marck-subtitle">Signalements des citoyens, agents et élus · Mairie de Marck</div>
        </div>
        <div class="marck-date">{date_fr}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Barre de stats ────────────────────────────────────────────────────────────
def render_stats():
    recs = st.session_state.records
    total    = len(recs)
    nouveaux = sum(1 for r in recs if r.get("statut") == "Nouveau")
    urgents  = sum(1 for r in recs if r.get("priorite") == "Urgente")
    en_retard = sum(1 for r in recs if is_overdue(r))
    st.markdown(f"""
    <div class="stats-bar">
        <span class="stat-item">📋 <b>{total}</b> signalement(s) total</span>
        <span class="stat-item">🆕 <b>{nouveaux}</b> nouveau(x)</span>
        <span class="stat-item">🚨 <b>{urgents}</b> urgent(s)</span>
        <span class="stat-item" style="color:#F0B429;">⚠️ <b>{en_retard}</b> en retard</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Panneau liste ─────────────────────────────────────────────────────────────
def render_list():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">▦ &nbsp;LISTE DES SIGNALEMENTS</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-body" style="padding:12px;">', unsafe_allow_html=True)

    # Recherche + filtre
    c1, c2 = st.columns([3, 2])
    with c1:
        search = st.text_input("", placeholder="🔍  Rechercher…", key="search_input",
                               label_visibility="collapsed")
    with c2:
        filtre = st.selectbox("", ["Tous"] + STATUTS, key="filtre_statut",
                              label_visibility="collapsed")

    # Filtrage
    recs = st.session_state.records
    q = search.lower().strip()
    if filtre != "Tous":
        recs = [r for r in recs if r.get("statut") == filtre]
    if q:
        recs = [r for r in recs if q in " ".join(str(v) for v in r.values()).lower()]
    recs = list(reversed(recs))

    # Tableau HTML
    rows_html = ""
    for r in recs:
        overdue_cls = "overdue" if is_overdue(r) else ""
        sel_cls = "selected" if r["id"] == st.session_state.selected_id else ""
        prio = r.get("priorite", "Normale")
        prio_color = PRIORITE_COULEURS.get(prio, BLEU)
        nom_complet = f"{r.get('nom','')} {r.get('prenom','')}".strip()
        rows_html += f"""
        <tr class="{overdue_cls} {sel_cls}">
            <td><b>{r['id']}</b></td>
            <td>{nom_complet}</td>
            <td style="font-size:11px">{r.get('categorie','')}</td>
            <td><span style="color:{prio_color};font-weight:700;font-size:11px">{prio}</span></td>
            <td style="font-size:11px">{r.get('statut','')}</td>
            <td style="font-size:11px">{r.get('butoir','')}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-y:auto;max-height:420px;border:1px solid {GRIS_LIGHT};border-radius:4px;">
    <table class="sig-table">
        <thead>
            <tr>
                <th>ID</th><th>Déclarant</th><th>Catégorie</th>
                <th>Prio</th><th>Statut</th><th>Échéance</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # Sélection via selectbox
    ids = [r["id"] for r in recs]
    if ids:
        st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
        sel = st.selectbox("Sélectionner un signalement :", ["— Nouveau —"] + ids,
                           key="sel_id", label_visibility="visible")
        if sel and sel != "— Nouveau —":
            if st.session_state.selected_id != sel:
                st.session_state.selected_id = sel
                st.session_state.form_mode = "edit"
                st.rerun()
        elif sel == "— Nouveau —" and st.session_state.selected_id is not None:
            st.session_state.selected_id = None
            st.session_state.form_mode = "new"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Boutons
    st.markdown("<div style='margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;'>", unsafe_allow_html=True)
    c_new, c_del, c_csv = st.columns([1, 1, 1])
    with c_new:
        if st.button("＋ Nouveau", use_container_width=True):
            st.session_state.selected_id = None
            st.session_state.form_mode = "new"
            st.session_state.confirm_delete = False
            st.rerun()
    with c_del:
        with st.container():
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            if st.button("🗑 Supprimer", use_container_width=True):
                if st.session_state.selected_id:
                    st.session_state.confirm_delete = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    with c_csv:
        with st.container():
            st.markdown('<div class="btn-green">', unsafe_allow_html=True)
            csv_data = export_csv()
            if csv_data:
                st.download_button("⬇ CSV", data=csv_data,
                                   file_name=f"remontees_{datetime.now():%Y%m%d}.csv",
                                   mime="text/csv", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Confirmation suppression
    if st.session_state.confirm_delete and st.session_state.selected_id:
        st.warning(f"Supprimer **{st.session_state.selected_id}** ?")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✔ Confirmer", use_container_width=True):
                st.session_state.records = [
                    r for r in st.session_state.records
                    if r["id"] != st.session_state.selected_id
                ]
                save_data(st.session_state.records)
                st.session_state.selected_id = None
                st.session_state.form_mode = "new"
                st.session_state.confirm_delete = False
                st.session_state.notif = ("success", "Signalement supprimé.")
                st.rerun()
        with cc2:
            with st.container():
                st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
                if st.button("✖ Annuler", use_container_width=True):
                    st.session_state.confirm_delete = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)  # card-body + card

# ─── Formulaire ────────────────────────────────────────────────────────────────
def render_form():
    rec = get_selected()
    is_edit = rec is not None
    mode_label = f"✏  MODIFIER — {rec['id']}" if is_edit else "✎  NOUVEAU SIGNALEMENT"

    st.markdown(f'<div class="card"><div class="card-header">{mode_label}</div><div class="card-body">', unsafe_allow_html=True)

    # Notification
    if st.session_state.notif:
        typ, msg = st.session_state.notif
        if typ == "success": st.success(msg)
        elif typ == "warning": st.warning(msg)
        st.session_state.notif = None

    def v(field, default=""):
        return rec.get(field, default) if rec else default

    # ── Section 1 ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">1 · Informations sur le déclarant</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: nom = st.text_input("Nom *", value=v("nom"), key="f_nom")
    with c2: prenom = st.text_input("Prénom *", value=v("prenom"), key="f_prenom")

    c3, c4 = st.columns(2)
    with c3:
        type_decl = st.selectbox("Type de déclarant", TYPES_DECLARANT,
                                  index=TYPES_DECLARANT.index(v("type_declarant", "Citoyen")),
                                  key="f_type")
    with c4:
        date_str = st.text_input("Date de remontée *",
                                  value=v("date", datetime.now().strftime("%d/%m/%Y")),
                                  key="f_date", placeholder="JJ/MM/AAAA")

    c5, c6 = st.columns(2)
    with c5: tel = st.text_input("Téléphone", value=v("telephone"), key="f_tel")
    with c6: email = st.text_input("Email", value=v("email"), key="f_email")

    adresse = st.text_input("Adresse du déclarant", value=v("adresse"), key="f_adresse")

    # ── Section 2 ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">2 · Détails du signalement</div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    with c7:
        cat_idx = CATEGORIES.index(v("categorie", CATEGORIES[0])) if v("categorie") in CATEGORIES else 0
        categorie = st.selectbox("Catégorie *", CATEGORIES, index=cat_idx, key="f_cat")
    with c8:
        prio_idx = PRIORITES.index(v("priorite", "Normale")) if v("priorite") in PRIORITES else 1
        priorite = st.selectbox("Priorité", PRIORITES, index=prio_idx, key="f_prio")

    # Calcul butoir dynamique
    butoir, delai = calc_butoir(date_str, priorite)
    prio_color = PRIORITE_COULEURS.get(priorite, ROUGE)
    st.markdown(f"""
    <div style="margin:4px 0 10px 0;">
        <div style="font-size:11px;font-weight:700;color:{GRIS_MED};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">
            DATE BUTOIR (CALCULÉE)
        </div>
        <div class="butoir-badge" style="background:{prio_color};">
            📅 &nbsp;{butoir} &nbsp;(+{delai} jours)
        </div>
    </div>
    """, unsafe_allow_html=True)

    lieu = st.text_input("Localisation du problème",
                          value=v("lieu"),
                          placeholder="Ex: Angle rue Victor Hugo / avenue de la Gare",
                          key="f_lieu")
    description = st.text_area("Description détaillée *",
                                value=v("description"), height=100, key="f_desc")

    # ── Section 3 ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">3 · Traitement & suivi</div>', unsafe_allow_html=True)
    c9, c10 = st.columns(2)
    with c9:
        stat_idx = STATUTS.index(v("statut", "Nouveau")) if v("statut") in STATUTS else 0
        statut = st.selectbox("Statut", STATUTS, index=stat_idx, key="f_statut")
    with c10:
        agent = st.text_input("Agent responsable",
                               value=v("agent"),
                               placeholder="Nom de l'agent", key="f_agent")

    service = st.text_input("Service concerné",
                             value=v("service"),
                             placeholder="Ex: Service voirie, espaces verts…",
                             key="f_service")
    notes = st.text_area("Notes internes / actions menées",
                          value=v("notes"), height=80, key="f_notes")

    # Satisfaction + options
    c11, c12 = st.columns(2)
    with c11:
        st.markdown("**SATISFACTION DÉCLARANT**")
        sat_emojis = {0: "Non renseigné", 1: "😞", 2: "😐", 3: "😊", 4: "😄", 5: "⭐"}
        sat = st.radio("", [0,1,2,3,4,5],
                        index=v("satisfaction", 0),
                        format_func=lambda x: sat_emojis[x],
                        horizontal=True, key="f_sat")
    with c12:
        st.markdown("**OPTIONS**")
        rappel  = st.checkbox("Réponse par email", value=v("rappel_email", False), key="f_rappel")
        anonyme = st.checkbox("Déclaration anonyme", value=v("anonyme", False), key="f_anon")

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # Boutons d'action
    bc1, bc2, bc3 = st.columns([2, 1.5, 1.5])
    with bc1:
        save_clicked = st.button("💾  Enregistrer", use_container_width=True, key="btn_save")
    with bc2:
        with st.container():
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            reset_clicked = st.button("🔄  Réinitialiser", use_container_width=True, key="btn_reset")
            st.markdown('</div>', unsafe_allow_html=True)
    with bc3:
        with st.container():
            st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
            dup_clicked = st.button("📋  Dupliquer", use_container_width=True, key="btn_dup",
                                     disabled=not is_edit)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Logique boutons ────────────────────────────────────────────────────────
    if save_clicked:
        if not nom.strip() or not description.strip():
            st.session_state.notif = ("warning", "Le nom et la description sont obligatoires.")
            st.rerun()
        else:
            data = build_record(
                nom, prenom, type_decl, date_str, tel, email, adresse,
                categorie, priorite, butoir, lieu, description,
                statut, agent, service, notes, sat, rappel, anonyme
            )
            if is_edit:
                data["id"] = st.session_state.selected_id
                idx = next(i for i, r in enumerate(st.session_state.records)
                           if r["id"] == st.session_state.selected_id)
                st.session_state.records[idx] = data
                msg = f"Signalement {data['id']} mis à jour ✓"
            else:
                data["id"] = next_id(st.session_state.records)
                st.session_state.records.append(data)
                st.session_state.selected_id = data["id"]
                st.session_state.form_mode = "edit"
                msg = f"Signalement {data['id']} créé avec succès ✓"
            save_data(st.session_state.records)
            st.session_state.notif = ("success", msg)
            st.rerun()

    if reset_clicked:
        st.session_state.selected_id = None
        st.session_state.form_mode = "new"
        st.rerun()

    if dup_clicked and is_edit:
        data = build_record(
            nom, prenom, type_decl, date_str, tel, email, adresse,
            categorie, priorite, butoir, lieu, description,
            "Nouveau", agent, service, notes, sat, rappel, anonyme
        )
        data["id"] = next_id(st.session_state.records)
        data["created_at"] = datetime.now().isoformat()
        st.session_state.records.append(data)
        save_data(st.session_state.records)
        st.session_state.notif = ("success", f"Signalement {data['id']} dupliqué ✓")
        st.rerun()

def build_record(nom, prenom, type_decl, date_str, tel, email, adresse,
                 categorie, priorite, butoir, lieu, description,
                 statut, agent, service, notes, sat, rappel, anonyme):
    return {
        "id": "",
        "nom": nom.strip(),
        "prenom": prenom.strip(),
        "type_declarant": type_decl,
        "date": date_str,
        "butoir": butoir,
        "telephone": tel.strip(),
        "email": email.strip(),
        "adresse": adresse.strip(),
        "categorie": categorie,
        "priorite": priorite,
        "lieu": lieu.strip(),
        "description": description.strip(),
        "statut": statut,
        "agent": agent.strip(),
        "service": service.strip(),
        "notes": notes.strip(),
        "satisfaction": sat,
        "rappel_email": rappel,
        "anonyme": anonyme,
        "created_at": datetime.now().isoformat(),
    }

# ─── Export CSV ────────────────────────────────────────────────────────────────
def export_csv():
    if not st.session_state.records:
        return None
    keys = ["id","date","butoir","nom","prenom","type_declarant",
            "telephone","email","adresse","categorie","priorite",
            "lieu","description","statut","agent","service",
            "notes","satisfaction","rappel_email","anonyme","created_at"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=keys, extrasaction="ignore")
    w.writeheader()
    w.writerows(st.session_state.records)
    return buf.getvalue().encode("utf-8-sig")

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    init_state()
    render_header()
    render_stats()

    # Layout principal : liste (35%) | formulaire (65%)
    col_list, col_form = st.columns([35, 65])
    with col_list:
        render_list()
    with col_form:
        render_form()

if __name__ == "__main__":
    main()
