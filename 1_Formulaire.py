"""
Remontées Citoyennes — Ville de Marck
Page 2 : Formulaire de saisie / modification
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(
    page_title="Formulaire — Remontées Citoyennes",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Constantes ───────────────────────────────────────────────────────────────
ROUGE      = "#C8202E"
ROUGE_DARK = "#9E1922"
ROUGE_LIGHT= "#F5E6E7"
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
DELAIS    = {"Faible": 15, "Normale": 10, "Élevée": 5, "Urgente": 2}
CATEGORIES = [
    "Voirie & Mobilité", "Espaces verts & Propreté", "Éclairage public",
    "Bâtiments communaux", "Nuisances sonores", "Sécurité & Incivilités",
    "Eau & Assainissement", "Déchets & Collecte", "Transports en commun",
    "Stationnement", "Accessibilité PMR", "Événements & Vie locale", "Autre",
]
PRIORITES       = ["Faible", "Normale", "Élevée", "Urgente"]
STATUTS         = ["Nouveau", "En cours", "En attente", "Résolu", "Archivé"]
TYPES_DECLARANT = ["Citoyen", "Agent municipal", "Élu", "Association", "Entreprise"]

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
    nums = [int(r["id"].split("-")[1]) for r in records if "-" in r.get("id","")]
    return f"REM-{(max(nums)+1):04d}" if nums else "REM-0001"

def calc_butoir(date_str, priorite):
    delai = DELAIS.get(priorite, 10)
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        d = datetime.now()
    return (d + timedelta(days=delai)).strftime("%d/%m/%Y"), delai

# ─── CSS ──────────────────────────────────────────────────────────────────────
def css():
    st.markdown(f"""
    <style>
    #MainMenu, footer, header, [data-testid="stToolbar"], .stDeployButton {{ display:none !important; }}
    [data-testid="stSidebar"] {{ display:none !important; }}
    .block-container {{ padding: 0 !important; max-width:100% !important; }}
    body, html {{ background:{FOND_PAGE} !important; font-family:'Trebuchet MS',sans-serif; }}

    .hdr {{
        background:{BLANC}; border-top:5px solid {ROUGE};
        border-bottom:3px solid {ROUGE};
        padding:12px 24px; display:flex; align-items:center; gap:16px;
        box-shadow:0 2px 6px rgba(0,0,0,0.07);
    }}
    .hdr-logo {{ font-size:26px; font-weight:900; color:{ROUGE}; letter-spacing:2px; line-height:1; }}
    .hdr-sub  {{ font-size:9px; color:{GRIS_MED}; letter-spacing:1px; text-transform:uppercase; }}
    .hdr-sep  {{ width:1px; height:44px; background:{GRIS_LIGHT}; margin:0 8px; }}
    .hdr-title   {{ font-size:18px; font-weight:700; color:{GRIS_TITRE}; }}
    .hdr-subtitle {{ font-size:11px; color:{GRIS_MED}; }}

    /* Section header */
    .sec {{
        display:flex; align-items:center; gap:10px;
        margin:20px 0 12px 0; font-size:11px; font-weight:700;
        color:{ROUGE}; letter-spacing:0.8px; text-transform:uppercase;
    }}
    .sec::before {{
        content:''; display:block; width:4px; height:18px;
        background:{ROUGE}; border-radius:2px; flex-shrink:0;
    }}
    .sec::after {{
        content:''; flex:1; height:1px; background:{GRIS_LIGHT};
    }}

    /* Formulaire card */
    .form-card {{
        background:{BLANC}; border:1px solid {GRIS_LIGHT};
        border-radius:6px; overflow:hidden;
        margin:16px 24px;
    }}
    .form-hdr {{
        background:{ROUGE}; color:{BLANC};
        padding:12px 20px; font-size:14px; font-weight:700;
        display:flex; align-items:center; justify-content:space-between;
    }}
    .form-body {{ padding:20px 24px; }}

    /* Butoir badge */
    .butoir {{
        padding:10px 16px; border-radius:4px; color:white;
        font-weight:700; font-size:14px; text-align:center;
        display:block; margin-top:4px;
    }}

    /* Streamlit widgets */
    div[data-baseweb="select"] > div {{
        border:1px solid {GRIS_LIGHT} !important;
        background:#F9FAFB !important; border-radius:4px !important;
        min-height:42px !important; font-size:14px !important;
    }}
    div[data-baseweb="input"] input {{
        border:1px solid {GRIS_LIGHT} !important;
        background:#F9FAFB !important; border-radius:4px !important;
        min-height:42px !important; font-size:14px !important;
        padding:8px 12px !important;
    }}
    div[data-baseweb="input"] input:focus {{
        border-color:{BLEU} !important;
        box-shadow:0 0 0 2px {BLEU_LIGHT} !important;
    }}
    textarea {{
        border:1px solid {GRIS_LIGHT} !important;
        background:#F9FAFB !important; border-radius:4px !important;
        font-size:14px !important; padding:10px 12px !important;
        font-family:'Trebuchet MS',sans-serif !important;
        line-height:1.5 !important;
    }}
    textarea:focus {{
        border-color:{BLEU} !important;
        box-shadow:0 0 0 2px {BLEU_LIGHT} !important;
        outline:none !important;
    }}
    .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio > label {{
        font-size:12px !important; font-weight:700 !important;
        color:{GRIS_MED} !important; text-transform:uppercase !important;
        letter-spacing:0.4px !important; margin-bottom:4px !important;
    }}
    .stCheckbox label {{ font-size:13px !important; color:{GRIS_TITRE} !important; font-weight:400 !important; text-transform:none !important; }}

    /* Boutons */
    .stButton > button {{
        font-family:'Trebuchet MS',sans-serif !important;
        font-weight:700 !important; font-size:14px !important;
        border:none !important; border-radius:4px !important;
        padding:10px 20px !important; min-height:44px !important;
        transition:background 0.15s !important;
    }}
    [data-testid="column"] {{ padding:0 5px !important; }}
    </style>
    """, unsafe_allow_html=True)

# ─── INIT STATE ───────────────────────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = load_data()
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

css()

rec = None
if st.session_state.selected_id:
    rec = next((r for r in st.session_state.records
                if r["id"] == st.session_state.selected_id), None)

is_edit   = rec is not None
mode_txt  = f"✏️  MODIFIER — {rec['id']}" if is_edit else "✎  NOUVEAU SIGNALEMENT"
id_txt    = rec["id"] if is_edit else ""

def v(field, default=""):
    return rec.get(field, default) if rec else default

date_fr = datetime.now().strftime("%A %d %B %Y").capitalize()

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
</div>
""", unsafe_allow_html=True)

# Bouton retour
st.markdown("<div style='padding:10px 24px 0 24px;'>", unsafe_allow_html=True)
if st.button("← Retour à la liste"):
    st.switch_page("app.py")
st.markdown("</div>", unsafe_allow_html=True)

# Formulaire
st.markdown(f"""
<div class="form-card">
  <div class="form-hdr">
    <span>{mode_txt}</span>
    <span style="font-family:monospace;font-size:13px;opacity:0.9">{id_txt}</span>
  </div>
  <div class="form-body">
""", unsafe_allow_html=True)

# ── Section 1 : Déclarant ──────────────────────────────────────────────────
st.markdown('<div class="sec">1 · Informations sur le déclarant</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: nom    = st.text_input("Nom *", value=v("nom"), key="nom")
with c2: prenom = st.text_input("Prénom", value=v("prenom"), key="prenom")

c3, c4 = st.columns(2)
with c3:
    type_idx = TYPES_DECLARANT.index(v("type_declarant","Citoyen")) if v("type_declarant") in TYPES_DECLARANT else 0
    type_decl = st.selectbox("Type de déclarant", TYPES_DECLARANT, index=type_idx, key="type_decl")
with c4:
    date_str = st.text_input("Date de remontée *",
                              value=v("date", datetime.now().strftime("%d/%m/%Y")),
                              placeholder="JJ/MM/AAAA", key="date_str")

c5, c6 = st.columns(2)
with c5: tel   = st.text_input("Téléphone", value=v("telephone"), key="tel")
with c6: email = st.text_input("Email", value=v("email"), key="email")

adresse = st.text_input("Adresse du déclarant", value=v("adresse"), key="adresse")

# ── Section 2 : Signalement ────────────────────────────────────────────────
st.markdown('<div class="sec">2 · Détails du signalement</div>', unsafe_allow_html=True)

c7, c8 = st.columns(2)
with c7:
    cat_idx  = CATEGORIES.index(v("categorie", CATEGORIES[0])) if v("categorie") in CATEGORIES else 0
    categorie = st.selectbox("Catégorie *", CATEGORIES, index=cat_idx, key="categorie")
with c8:
    prio_idx = PRIORITES.index(v("priorite","Normale")) if v("priorite") in PRIORITES else 1
    priorite = st.selectbox("Priorité", PRIORITES, index=prio_idx, key="priorite")

# Calcul butoir
butoir, delai = calc_butoir(date_str, priorite)
prio_color = PRIORITE_COULEURS.get(priorite, ROUGE)
st.markdown(f"""
<div style="margin:0 0 12px 0;">
  <div style="font-size:12px;font-weight:700;color:{GRIS_MED};text-transform:uppercase;letter-spacing:0.4px;margin-bottom:4px;">
    📅 Date butoir calculée automatiquement
  </div>
  <span class="butoir" style="background:{prio_color};">
    {butoir} &nbsp;· &nbsp;délai : +{delai} jours
  </span>
</div>
""", unsafe_allow_html=True)

lieu = st.text_input("Localisation du problème",
                      value=v("lieu"),
                      placeholder="Ex: Angle rue Victor Hugo / avenue de la Gare",
                      key="lieu")
description = st.text_area("Description détaillée *",
                            value=v("description"), height=120, key="description")

# ── Section 3 : Traitement ─────────────────────────────────────────────────
st.markdown('<div class="sec">3 · Traitement & suivi</div>', unsafe_allow_html=True)

c9, c10 = st.columns(2)
with c9:
    stat_idx = STATUTS.index(v("statut","Nouveau")) if v("statut") in STATUTS else 0
    statut   = st.selectbox("Statut", STATUTS, index=stat_idx, key="statut")
with c10:
    agent = st.text_input("Agent responsable",
                           value=v("agent"),
                           placeholder="Nom de l'agent", key="agent")

service = st.text_input("Service concerné",
                         value=v("service"),
                         placeholder="Ex: Service voirie, espaces verts…", key="service")
notes = st.text_area("Notes internes / actions menées",
                      value=v("notes"), height=90, key="notes")

# ── Section 4 : Options ────────────────────────────────────────────────────
st.markdown('<div class="sec">4 · Options & satisfaction</div>', unsafe_allow_html=True)

c11, c12 = st.columns(2)
with c11:
    sat_opts = {0: "Non renseigné", 1: "😞 Insatisfait", 2: "😐 Neutre",
                3: "😊 Satisfait", 4: "😄 Très satisfait", 5: "⭐ Excellent"}
    sat = st.selectbox("Satisfaction déclarant",
                        list(sat_opts.keys()),
                        index=v("satisfaction", 0),
                        format_func=lambda x: sat_opts[x],
                        key="satisfaction")
with c12:
    st.markdown("<div style='margin-top:28px;'>", unsafe_allow_html=True)
    rappel  = st.checkbox("Réponse par email souhaitée", value=v("rappel_email", False), key="rappel")
    anonyme = st.checkbox("Déclaration anonyme", value=v("anonyme", False), key="anonyme")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)  # form-body + form-card

# ── Boutons d'action ───────────────────────────────────────────────────────
st.markdown("<div style='padding:0 24px 24px 24px;'>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#E8E9EA;margin:0 0 16px 0;'>", unsafe_allow_html=True)

ba1, ba2, ba3 = st.columns([2, 2, 2])
with ba1:
    save_btn = st.button("💾  Enregistrer", type="primary", use_container_width=True, key="btn_save")
with ba2:
    dup_btn = st.button("📋  Dupliquer", use_container_width=True, key="btn_dup",
                         disabled=not is_edit)
with ba3:
    cancel_btn = st.button("↩️  Annuler", use_container_width=True, key="btn_cancel")

st.markdown("</div>", unsafe_allow_html=True)

# ─── Logique boutons ───────────────────────────────────────────────────────────
if cancel_btn:
    st.switch_page("app.py")

if save_btn:
    if not nom.strip():
        st.error("⚠️ Le nom du déclarant est obligatoire.")
    elif not description.strip():
        st.error("⚠️ La description est obligatoire.")
    else:
        data = {
            "id": "",
            "nom": nom.strip(), "prenom": prenom.strip(),
            "type_declarant": type_decl, "date": date_str, "butoir": butoir,
            "telephone": tel.strip(), "email": email.strip(), "adresse": adresse.strip(),
            "categorie": categorie, "priorite": priorite, "lieu": lieu.strip(),
            "description": description.strip(), "statut": statut,
            "agent": agent.strip(), "service": service.strip(), "notes": notes.strip(),
            "satisfaction": sat, "rappel_email": rappel, "anonyme": anonyme,
            "created_at": datetime.now().isoformat(),
        }
        if is_edit:
            data["id"] = st.session_state.selected_id
            idx = next(i for i, r in enumerate(st.session_state.records)
                       if r["id"] == st.session_state.selected_id)
            st.session_state.records[idx] = data
            msg = f"✅ Signalement {data['id']} mis à jour."
        else:
            data["id"] = next_id(st.session_state.records)
            st.session_state.records.append(data)
            msg = f"✅ Signalement {data['id']} créé avec succès."
        save_data(st.session_state.records)
        st.session_state.notif = ("success", msg)
        st.session_state.selected_id = None
        st.switch_page("app.py")

if dup_btn and is_edit:
    data = {
        "id": next_id(st.session_state.records),
        "nom": nom.strip(), "prenom": prenom.strip(),
        "type_declarant": type_decl, "date": datetime.now().strftime("%d/%m/%Y"),
        "butoir": butoir, "telephone": tel.strip(), "email": email.strip(),
        "adresse": adresse.strip(), "categorie": categorie, "priorite": priorite,
        "lieu": lieu.strip(), "description": description.strip(), "statut": "Nouveau",
        "agent": agent.strip(), "service": service.strip(), "notes": "",
        "satisfaction": 0, "rappel_email": rappel, "anonyme": anonyme,
        "created_at": datetime.now().isoformat(),
    }
    st.session_state.records.append(data)
    save_data(st.session_state.records)
    st.session_state.notif = ("success", f"✅ Signalement {data['id']} dupliqué.")
    st.session_state.selected_id = None
    st.switch_page("app.py")
