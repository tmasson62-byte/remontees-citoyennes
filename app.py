"""
Remontées Citoyennes — Ville de Marck
Page principale : Liste & tableau de bord
"""
import streamlit as st
import json
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(
    page_title="Remontées Citoyennes — Ville de Marck",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Constantes partagées ─────────────────────────────────────────────────────
ROUGE      = "#C8202E"
ROUGE_DARK = "#9E1922"
BLEU       = "#3AADE4"
BLEU_LIGHT = "#EAF6FD"
BLEU_DARK  = "#1E86BC"
OR         = "#F0B429"
GRIS_TITRE = "#58595B"
GRIS_DARK  = "#3A3B3C"
GRIS_MED   = "#7A7B7D"
GRIS_LIGHT = "#E8E9EA"
BLANC      = "#FFFFFF"
FOND_PAGE  = "#F4F5F6"
VERT       = "#2E8B57"

PRIORITE_COULEURS = {
    "Faible": "#2E8B57", "Normale": "#3AADE4",
    "Élevée": "#E07B20", "Urgente": "#C8202E",
}
STATUT_COULEURS = {
    "Nouveau": "#C8202E", "En cours": "#3AADE4", "En attente": "#F0B429",
    "Résolu": "#2E8B57", "Archivé": "#7A7B7D",
}
DELAIS    = {"Faible": 15, "Normale": 10, "Élevée": 5, "Urgente": 2}
STATUTS   = ["Nouveau", "En cours", "En attente", "Résolu", "Archivé"]
CATEGORIES = [
    "Voirie & Mobilité", "Espaces verts & Propreté", "Éclairage public",
    "Bâtiments communaux", "Nuisances sonores", "Sécurité & Incivilités",
    "Eau & Assainissement", "Déchets & Collecte", "Transports en commun",
    "Stationnement", "Accessibilité PMR", "Événements & Vie locale", "Autre",
]

DATA_FILE = Path("remontees_citoyennes.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def is_overdue(rec):
    try:
        bd = datetime.strptime(rec.get("butoir", ""), "%d/%m/%Y").date()
        return bd < datetime.now().date() and rec.get("statut") not in ("Résolu", "Archivé")
    except ValueError:
        return False

def export_csv(records):
    keys = ["id","date","butoir","nom","prenom","type_declarant","telephone","email",
            "adresse","categorie","priorite","lieu","description","statut","agent",
            "service","notes","satisfaction","rappel_email","anonyme","created_at"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=keys, extrasaction="ignore")
    w.writeheader()
    w.writerows(records)
    return buf.getvalue().encode("utf-8-sig")

# ─── CSS ──────────────────────────────────────────────────────────────────────
def css():
    st.markdown(f"""
    <style>
    #MainMenu, footer, header, [data-testid="stToolbar"], .stDeployButton {{ display:none !important; }}
    [data-testid="stSidebar"] {{ display:none !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    body, html {{ background: {FOND_PAGE} !important; font-family: 'Trebuchet MS', sans-serif; }}

    /* HEADER */
    .hdr {{
        background: {BLANC}; border-top: 5px solid {ROUGE};
        border-bottom: 3px solid {ROUGE};
        padding: 12px 24px; display:flex; align-items:center; gap:16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }}
    .hdr-logo {{ font-size:26px; font-weight:900; color:{ROUGE}; letter-spacing:2px; line-height:1; }}
    .hdr-sub  {{ font-size:9px; color:{GRIS_MED}; letter-spacing:1px; text-transform:uppercase; }}
    .hdr-sep  {{ width:1px; height:44px; background:{GRIS_LIGHT}; margin:0 8px; }}
    .hdr-title {{ font-size:18px; font-weight:700; color:{GRIS_TITRE}; }}
    .hdr-subtitle {{ font-size:11px; color:{GRIS_MED}; }}
    .hdr-date {{ margin-left:auto; font-size:11px; color:{GRIS_MED}; text-align:right; }}

    /* NAV */
    .nav {{ background:{GRIS_DARK}; padding:0 24px; display:flex; gap:0; }}
    .nav a {{
        color:{BLANC}; text-decoration:none; padding:10px 20px;
        font-size:12px; font-weight:700; letter-spacing:0.5px;
        border-bottom:3px solid transparent; display:inline-block;
        text-transform:uppercase;
    }}
    .nav a:hover {{ background:rgba(255,255,255,0.08); }}
    .nav a.active {{ border-bottom-color:{ROUGE}; color:{BLANC}; }}

    /* STATS BAR */
    .statsbar {{
        background:{GRIS_DARK}; color:{BLANC}; padding:8px 24px;
        display:flex; gap:28px; font-size:12px; flex-wrap:wrap;
    }}

    /* TOOLBAR */
    .toolbar {{
        background:{BLANC}; border-bottom:1px solid {GRIS_LIGHT};
        padding:12px 24px; display:flex; align-items:center; gap:12px; flex-wrap:wrap;
    }}

    /* TABLE */
    .sig-table {{ width:100%; border-collapse:collapse; font-size:13px; background:{BLANC}; }}
    .sig-table thead tr {{ background:{ROUGE}; }}
    .sig-table thead th {{
        color:{BLANC}; padding:10px 14px; text-align:left;
        font-weight:700; font-size:12px; letter-spacing:0.3px; white-space:nowrap;
    }}
    .sig-table tbody tr {{
        border-bottom:1px solid {GRIS_LIGHT}; cursor:pointer;
        transition:background 0.1s;
    }}
    .sig-table tbody tr:hover {{ background:{BLEU_LIGHT}; }}
    .sig-table tbody td {{ padding:9px 14px; color:{GRIS_TITRE}; vertical-align:middle; }}
    .sig-table tbody tr.overdue td {{ color:{ROUGE}; }}
    .sig-table tbody tr.overdue {{ font-weight:700; }}

    /* BADGE */
    .badge {{
        display:inline-block; padding:3px 9px; border-radius:3px;
        font-size:11px; font-weight:700; color:white; white-space:nowrap;
    }}

    /* BOUTONS Streamlit */
    .stButton > button {{
        font-family:'Trebuchet MS',sans-serif !important;
        font-weight:700 !important; font-size:13px !important;
        border:none !important; border-radius:4px !important;
        padding:9px 16px !important; cursor:pointer !important;
        transition:background 0.15s !important;
    }}
    div[data-testid="column"] {{ padding: 0 4px !important; }}

    /* Download button */
    .stDownloadButton > button {{
        font-family:'Trebuchet MS',sans-serif !important;
        font-weight:700 !important; font-size:13px !important;
        background:{VERT} !important; color:white !important;
        border:none !important; border-radius:4px !important;
        padding:9px 16px !important;
    }}

    /* Selectbox & input */
    div[data-baseweb="select"] > div {{
        border:1px solid {GRIS_LIGHT} !important;
        background:#F9FAFB !important; border-radius:4px !important;
        min-height:38px !important; font-size:13px !important;
    }}
    div[data-baseweb="input"] input {{
        border:1px solid {GRIS_LIGHT} !important;
        background:#F9FAFB !important; border-radius:4px !important;
        min-height:38px !important; font-size:13px !important;
        padding:8px 12px !important;
    }}
    .stTextInput label, .stSelectbox label {{
        font-size:11px !important; font-weight:700 !important;
        color:{GRIS_MED} !important; text-transform:uppercase !important;
        letter-spacing:0.4px !important;
    }}

    /* Contenu principal */
    .main-content {{ padding:20px 24px; }}

    /* Card */
    .card {{
        background:{BLANC}; border:1px solid {GRIS_LIGHT};
        border-radius:6px; overflow:hidden; margin-bottom:16px;
    }}
    .card-hdr {{
        background:{ROUGE}; color:{BLANC}; padding:10px 16px;
        font-size:13px; font-weight:700; letter-spacing:0.4px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ─── INIT STATE ───────────────────────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = load_data()
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "notif" not in st.session_state:
    st.session_state.notif = None
if "confirm_del" not in st.session_state:
    st.session_state.confirm_del = False

# ─── RENDER ───────────────────────────────────────────────────────────────────
css()

recs = st.session_state.records
total     = len(recs)
nouveaux  = sum(1 for r in recs if r.get("statut") == "Nouveau")
urgents   = sum(1 for r in recs if r.get("priorite") == "Urgente")
en_retard = sum(1 for r in recs if is_overdue(r))
date_fr   = datetime.now().strftime("%A %d %B %Y").capitalize()

# Header
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-logo">MARCK</div>
    <div class="hdr-sub">Ville de Marck</div>
  </div>
  <div class="hdr-sep"></div>
  <div>
    <div class="hdr-title">Gestion des Remontées Citoyennes</div>
    <div class="hdr-subtitle">Signalements des citoyens, agents et élus · Mairie de Marck</div>
  </div>
  <div class="hdr-date">{date_fr}</div>
</div>
<div class="statsbar">
  <span>📋 <b>{total}</b> signalement(s)</span>
  <span>🆕 <b>{nouveaux}</b> nouveau(x)</span>
  <span>🚨 <b>{urgents}</b> urgent(s)</span>
  <span style="color:#F0B429">⚠️ <b>{en_retard}</b> en retard</span>
</div>
""", unsafe_allow_html=True)

# Notification
if st.session_state.notif:
    t, m = st.session_state.notif
    if t == "success": st.success(m)
    elif t == "warning": st.warning(m)
    st.session_state.notif = None

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ── Barre d'outils ─────────────────────────────────────────────────────────
st.markdown("### 🔍 Recherche & Filtres")
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    search = st.text_input("Rechercher", placeholder="Nom, description, lieu…", label_visibility="collapsed")
with col2:
    filtre_statut = st.selectbox("Statut", ["Tous les statuts"] + STATUTS, label_visibility="collapsed")
with col3:
    filtre_cat = st.selectbox("Catégorie", ["Toutes les catégories"] + CATEGORIES, label_visibility="collapsed")

# ── Filtrage ───────────────────────────────────────────────────────────────
filtered = list(reversed(recs))
if filtre_statut != "Tous les statuts":
    filtered = [r for r in filtered if r.get("statut") == filtre_statut]
if filtre_cat != "Toutes les catégories":
    filtered = [r for r in filtered if r.get("categorie") == filtre_cat]
if search.strip():
    q = search.lower()
    filtered = [r for r in filtered if q in " ".join(str(v) for v in r.values()).lower()]

st.markdown(f"<p style='color:{GRIS_MED};font-size:12px;margin:4px 0 12px 0;'>{len(filtered)} résultat(s) affiché(s)</p>", unsafe_allow_html=True)

# ── Boutons action ─────────────────────────────────────────────────────────
bc1, bc2, bc3, bc4 = st.columns([2, 2, 2, 6])
with bc1:
    if st.button("➕ Nouveau signalement", use_container_width=True,
                 type="primary"):
        st.session_state.selected_id = None
        st.switch_page("pages/1_Formulaire.py")
with bc2:
    if st.button("🗑️ Supprimer", use_container_width=True):
        if st.session_state.selected_id:
            st.session_state.confirm_del = True
            st.rerun()
        else:
            st.session_state.notif = ("warning", "Sélectionnez d'abord un signalement dans la liste.")
            st.rerun()
with bc3:
    if recs:
        st.download_button("⬇️ Export CSV", data=export_csv(recs),
                           file_name=f"remontees_{datetime.now():%Y%m%d}.csv",
                           mime="text/csv", use_container_width=True)

# Confirmation suppression
if st.session_state.confirm_del and st.session_state.selected_id:
    st.warning(f"⚠️ Supprimer définitivement **{st.session_state.selected_id}** ?")
    cc1, cc2, _ = st.columns([1, 1, 6])
    with cc1:
        if st.button("✔️ Confirmer", type="primary"):
            st.session_state.records = [r for r in st.session_state.records
                                         if r["id"] != st.session_state.selected_id]
            save_data(st.session_state.records)
            st.session_state.selected_id = None
            st.session_state.confirm_del = False
            st.session_state.notif = ("success", "Signalement supprimé.")
            st.rerun()
    with cc2:
        if st.button("✖️ Annuler"):
            st.session_state.confirm_del = False
            st.rerun()

# ── Tableau ────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-hdr">▦ &nbsp;LISTE DES SIGNALEMENTS</div>', unsafe_allow_html=True)

if not filtered:
    st.markdown("<p style='padding:20px;color:#7A7B7D;text-align:center;'>Aucun signalement trouvé.</p>", unsafe_allow_html=True)
else:
    rows = ""
    for r in filtered:
        ov  = "overdue" if is_overdue(r) else ""
        pc  = PRIORITE_COULEURS.get(r.get("priorite",""), BLEU)
        sc  = STATUT_COULEURS.get(r.get("statut",""), GRIS_MED)
        nom = f"{r.get('nom','')} {r.get('prenom','')}".strip()
        retard = " ⚠️" if is_overdue(r) else ""
        rows += f"""
        <tr class="{ov}">
          <td><b>{r['id']}</b></td>
          <td>{r.get('date','')}</td>
          <td>{nom}</td>
          <td style="max-width:160px;font-size:12px">{r.get('categorie','')}</td>
          <td><span class="badge" style="background:{pc}">{r.get('priorite','')}</span></td>
          <td><span class="badge" style="background:{sc}">{r.get('statut','')}</span></td>
          <td style="font-size:12px">{r.get('butoir','')}{retard}</td>
          <td style="font-size:12px;color:{GRIS_MED}">{r.get('agent','')}</td>
        </tr>"""
    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="sig-table">
      <thead>
        <tr>
          <th>ID</th><th>Date</th><th>Déclarant</th><th>Catégorie</th>
          <th>Priorité</th><th>Statut</th><th>Échéance</th><th>Agent</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Sélection pour modifier ────────────────────────────────────────────────
if filtered:
    st.markdown("---")
    st.markdown("**✏️ Ouvrir / modifier un signalement :**")
    ids_list = [r["id"] for r in filtered]
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        choix = st.selectbox("Sélectionner un ID", ["— Choisir —"] + ids_list,
                             label_visibility="collapsed")
    with col_btn:
        if st.button("Ouvrir ➜", use_container_width=True, type="primary"):
            if choix and choix != "— Choisir —":
                st.session_state.selected_id = choix
                st.switch_page("pages/1_Formulaire.py")
            else:
                st.session_state.notif = ("warning", "Choisissez un signalement dans la liste.")
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # main-content
