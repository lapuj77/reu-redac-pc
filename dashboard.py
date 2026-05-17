import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from collections import defaultdict
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import base64
import json
import re
import os
import requests

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Rédaction",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --jdg:       #E8000D;
    --jdg-dark:  #B50009;
    --jdg-mid:   #FF3340;
    --jdg-light: #FFF0F0;
    --jdg-pale:  #FFF8F8;
    --jdg-border:#FFCCCC;
    --radius:    12px;
    --shadow:    0 2px 12px rgba(232,0,13,.10);
}

/* ── Police globale ── */
html, body, [class*="css"], .stMarkdown, .stText, button, input, label, p, td, th {
    font-family: 'Inter', sans-serif !important;
}

/* ── Fond ── */
.main, [data-testid="stAppViewContainer"] { background: #F5F0F0 !important; }
[data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #6B0004 0%, #AA0009 60%, #CC000E 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
[data-testid="stSidebar"] * { color: #fff !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {
    color: #fff !important; letter-spacing: .3px;
}
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 8px !important; color: #fff !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: rgba(255,255,255,0.45) !important; }
[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.08) !important;
    border: 2px dashed rgba(255,255,255,0.35) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
}
/* Boutons sidebar */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #B50009 !important; font-weight: 700 !important;
    border: 2px solid rgba(255,255,255,0.8) !important;
    border-radius: 8px !important;
    width: 100%; margin-top: .2rem;
    transition: all .15s;
}
[data-testid="stSidebar"] .stButton button:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: #fff0f0 !important; background-color: #fff0f0 !important;
    color: #8B0009 !important;
}
[data-testid="stSidebar"] .stButton button *,
[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span,
[data-testid="stSidebar"] .stButton button div,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] *,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p {
    color: #B50009 !important; font-weight: 700 !important;
    background: transparent !important; background-color: transparent !important;
}
/* Bouton "Browse files" du file uploader */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button span,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button p {
    background: #fff !important;
    color: #E8000D !important; font-weight: 600 !important;
    border: 1px solid rgba(255,255,255,0.5) !important;
    border-radius: 6px !important;
}
/* Texte informatif (config.json, small) */
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] code,
[data-testid="stSidebar"] .stMarkdown small {
    color: rgba(255,255,255,0.7) !important;
    background: transparent !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.18) !important; }
[data-testid="stSidebar"] small, [data-testid="stSidebar"] code {
    color: rgba(255,255,255,0.65) !important;
}

/* ── Onglets ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px; background: var(--jdg-light);
    border-radius: var(--radius); padding: 5px; border: 1px solid var(--jdg-border);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 9px !important; font-weight: 600 !important;
    font-size: .9rem !important; color: var(--jdg) !important;
    background: transparent !important; padding: .45rem 1rem !important;
    transition: all .15s;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--jdg) !important; color: #fff !important;
    box-shadow: 0 2px 8px rgba(232,0,13,.3) !important;
}

/* ── Cartes KPI ── */
.kpi-grid { display:flex; gap:14px; margin:1rem 0 1.5rem; flex-wrap:wrap; }
.kpi-card {
    flex:1; min-width:140px;
    background:#fff; border-radius:var(--radius);
    border: 1px solid var(--jdg-border);
    padding: 1.1rem 1.2rem .9rem;
    box-shadow: var(--shadow);
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:4px;
    background: linear-gradient(90deg, var(--jdg-dark), var(--jdg-mid));
}
.kpi-icon { font-size:1.4rem; margin-bottom:.3rem; }
.kpi-val  { font-size:1.65rem; font-weight:800; color:var(--jdg); line-height:1.1; }
.kpi-lbl  { font-size:.72rem; font-weight:600; color:#8B0009; text-transform:uppercase; letter-spacing:.6px; margin-top:.25rem; }

/* ── Cartes articles top/flop ── */
.art-card {
    display:flex; align-items:flex-start; gap:.6rem;
    background:#fff; border-radius:10px; padding:.6rem .8rem;
    margin:.3rem 0; box-shadow:0 1px 6px rgba(0,0,0,.06);
    border: 1px solid #eee; font-size:.84rem;
}
.art-card.top  { border-left: 4px solid #16a34a; }
.art-card.flop { border-left: 4px solid #dc2626; }
.art-rank { font-weight:800; font-size:.8rem; min-width:52px; }
.art-rank.top  { color:#16a34a; }
.art-rank.flop { color:#dc2626; }
.art-title { color:#1a0000; line-height:1.35; flex:1; }

/* ── Titres de section ── */
h3 { color: var(--jdg-dark) !important; font-weight:800 !important; }
h4 { color: var(--jdg) !important; font-weight:700 !important; letter-spacing:-.2px; }

/* ── DataFrames ── */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius); overflow:hidden;
    box-shadow: var(--shadow); border: 1px solid var(--jdg-border) !important;
}

/* ── Boutons principaux (hors sidebar) ── */
.main .stButton > button, [data-testid="stAppViewContainer"] .stButton > button {
    background: var(--jdg) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; transition: background .15s !important;
}
.main .stButton > button:hover { background: var(--jdg-dark) !important; }

/* ── Alerts / infos ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    border-radius: 8px !important; border-color: var(--jdg-border) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--jdg) !important; box-shadow: 0 0 0 3px rgba(232,0,13,.12) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] { border-radius: 10px !important; border: 1px solid var(--jdg-border) !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: var(--jdg) !important; }

hr { border-color: var(--jdg-border) !important; margin: 1rem 0 !important; }

/* ── Masquer les éléments UI Streamlit inutiles ── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="ScrollToTopButton"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
button[kind="scrollToTopButton"] { display: none !important; }
.stAppHeader { display: none !important; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1rem !important; }
/* Sidebar fixe — masquer le bouton de repli */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
section[data-testid="stSidebar"] { min-width: 280px !important; max-width: 280px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
DROPBOX_PATH  = r"D:\Dropbox\PCW10\Download"
ARCHIVE_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archives")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

EXCLUDED_AUTHORS = {
    "Louise Millon", "Sebastian Danila", "Enzo Bonucci",
    "Manon Carpentier", "Antoine Michaud", "Vincent Bouvier",
}
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def load_config() -> dict:
    """Load API keys: st.secrets first (cloud), then config.json (local)."""
    try:
        return {
            "tmdb_key": st.secrets.get("tmdb_key", ""),
            "rawg_key": st.secrets.get("rawg_key", ""),
        }
    except Exception:
        pass
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(data: dict):
    """Save API keys locally (only works in local mode)."""
    try:
        _ = st.secrets.get("tmdb_key", None)
        # If we're on Streamlit Cloud, can't save locally — silently skip
        return
    except Exception:
        pass
    existing = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                existing = json.load(f)
        except Exception:
            pass
    existing.update(data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


_config = load_config()

CATEGORIES = {
    "🎬 Pop Culture": [
        "film", "série", "netflix", "anime", "one piece", "harry potter", "marvel",
        "disney", "prime video", "streaming", "cinéma", "trailer", "bande-annonce",
        "saison", "acteur", "live-action", "jojo", "avengers", "pixar", "thrash",
        "disclosure", "man on fire", "raiponce", "rooster", "day one", "bass x",
        "jumpers", "conan", "seigneur des anneaux", "malcolm",
    ],
    "🎮 Jeux Vidéo": [
        "xbox", "playstation", "steam", "nintendo", "switch", "jeu ", "jeux",
        "pokémon", "pokemon", "fortnite", "mario", "gaming", "gamer", "ps5",
        "fps", "rpg", "mmorpg", "bioshock", "overwatch", "game", "yoshi",
        "pickmon", "pokopia", "resident evil", "life is strange", "blizzard",
        "odyssey 3d", "steam machine", "tcg", "lego mario",
    ],
    "💻 Nouvelles Tech": [
        "iphone", "apple", "samsung", "android", " ia ", "openai", "chatgpt",
        "google", "microsoft", "windows", "mac", "macbook", "smartphone", "5g",
        "puce", "processeur", "alexa", "siri", "grok", "meta ", "x money",
        "oppo", "xiaomi", "nothing headphone", "dyson", "notion", "promptspy",
        "rabbit ", "chrome", "android 16", "ssd", "nvidia", "amd", "photonique",
        "leakbase", "macrohard", "moltbook",
    ],
    "🛒 Conso & Produits": [
        "amazon", "cdiscount", "bon plan", "bonplan", "remise", "réduction",
        "vente flash", "bouygues", "free ", "orange ", "sfr", "abonnement",
        "forfait", "lego", "fnac", "darty", "boulanger", "airpods", "galaxy buds",
        "navigo", "shein", "carburant", "essence", "voiture électrique", "tesla",
        "renault", "byd", "denza", "zendure", "shokz", "ninja foodi", "ecoflow",
        "sihoo", "iptv", "mondial relay", "canal+", "panneaux solaires",
    ],
    "🔬 Sciences": [
        "espace", "nasa", "planète", "astéroïde", "étoile", "fusée", "satellite",
        "scientifique", "recherche", "biologie", "chimie", "physique",
        "découverte", "astronomie", "pieuvre", "cerveau", "adn", "neurone",
        "artemis", "lune", "mars", "esa", "solaire", "imprimante 3d",
        "disque dur moléculaire", "matériau", "quantique",
    ],
}

TYPE_LABELS = {
    "post": "Article",
    "bonplan": "Bon Plan",
    "critique": "Critique",
    "test": "Test",
    "dossier": "Dossier",
}

JOURS_FR = {
    "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
    "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche",
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt(n: int) -> str:
    """Format number with French thousands separator."""
    return f"{int(n):,}".replace(",", "\u202f")  # narrow no-break space


def parse_views(v) -> int:
    if v is None or (isinstance(v, float) and v != v):  # NaN check
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    cleaned = str(v).replace(" ", "").replace('"', "").replace("\u202f", "").strip()
    return int(cleaned) if cleaned.isdigit() else 0


def categorize(title: str) -> str:
    tl = title.lower()
    scores: dict[str, int] = defaultdict(int)
    for cat, kws in CATEGORIES.items():
        for kw in kws:
            if kw.lower() in tl:
                scores[cat] += 1
    return max(scores, key=scores.get) if scores else "📦 Autre"


@st.cache_data(show_spinner=False, ttl=3600)
def get_article_url(titre: str) -> str:
    """Recherche l'URL d'un article sur JDG via la recherche interne."""
    try:
        query = " ".join(titre.split()[:6])  # 6 premiers mots suffisent
        resp = requests.get(
            "https://www.journaldugeek.com/",
            params={"s": query},
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if resp.status_code == 200:
            match = re.search(
                r'href="(https://www\.journaldugeek\.com/(?:\d{4}/\d{2}/\d{2}/|[^"]+?/)[^"]+?/)"',
                resp.text,
            )
            if match:
                return match.group(1)
    except Exception:
        pass
    return ""


@st.cache_data(show_spinner="Chargement du CSV…")
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file, sep=";", encoding="utf-8")
    df.columns = ["Titre", "Type", "Rédacteur", "Mots", "Vues", "Date"]
    df["Vues"] = df["Vues"].apply(parse_views)
    df["Mots"] = df["Mots"].apply(parse_views)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Catégorie"] = df["Titre"].apply(categorize)
    df["Type_Label"] = df["Type"].map(TYPE_LABELS).fillna(df["Type"])
    df = df[~df["Rédacteur"].isin(EXCLUDED_AUTHORS)].reset_index(drop=True)
    return df


def week_dates(filename: str, df: pd.DataFrame):
    m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})", filename)
    if m:
        return m.group(1), m.group(2)
    return df["Date"].min().strftime("%Y-%m-%d"), df["Date"].max().strftime("%Y-%m-%d")


def get_tmdb_releases(api_key: str) -> dict:
    movies, tv = [], []
    error = None

    r = requests.get(
        "https://api.themoviedb.org/3/movie/upcoming",
        params={"api_key": api_key, "language": "fr-FR", "region": "FR"},
        timeout=8,
    )
    if r.ok:
        for m in r.json().get("results", [])[:10]:
            movies.append({
                "title": m.get("title", ""),
                "date": m.get("release_date", ""),
                "note": m.get("vote_average", 0),
            })
    else:
        error = r.json().get("status_message", f"Erreur {r.status_code}")

    r2 = requests.get(
        "https://api.themoviedb.org/3/tv/on_the_air",
        params={"api_key": api_key, "language": "fr-FR"},
        timeout=8,
    )
    if r2.ok:
        for s in r2.json().get("results", [])[:8]:
            tv.append({
                "title": s.get("name", ""),
                "date": s.get("first_air_date", ""),
            })

    return {"movies": movies, "tv": tv, "error": error}


def get_game_releases(api_key: str, date_start: str, date_end: str) -> tuple[list, str | None]:
    """Upcoming game releases from RAWG (rawg.io — free key)."""
    try:
        r = requests.get(
            "https://api.rawg.io/api/games",
            params={
                "key": api_key,
                "dates": f"{date_start},{date_end}",
                "ordering": "-added",
                "page_size": 20,
            },
            timeout=8,
        )
        if r.ok:
            games = []
            for g in r.json().get("results", []):
                platforms = [p["platform"]["name"] for p in g.get("platforms", [])[:4]]
                games.append({
                    "title": g.get("name", ""),
                    "date": g.get("released", ""),
                    "platforms": platforms,
                    "rating": g.get("rating", 0),
                })
            return games, None
        else:
            return [], r.json().get("error", f"Erreur {r.status_code}")
    except Exception as e:
        return [], str(e)


def generate_article_ideas(df: pd.DataFrame, events: list, top_articles: list) -> str:
    """Appel Claude API pour générer des idées d'articles."""
    try:
        import anthropic
        try:
            api_key = st.secrets.get("anthropic_key", "")
        except Exception:
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE) as f:
                    cfg = json.load(f)
            api_key = cfg.get("anthropic_key", "")

        if not api_key:
            return "❌ Clé API Anthropic manquante (ajouter `anthropic_key` dans les secrets)."

        client = anthropic.Anthropic(api_key=api_key)

        # Contexte : stats semaine
        cat_stats = df.groupby("Catégorie")["Vues"].agg(["mean", "sum", "count"]).sort_values("mean", ascending=False)
        top_cats = "\n".join([f"- {cat}: {int(row['mean']):,} vues/article ({int(row['count'])} articles)".replace(",", " ") for cat, row in cat_stats.head(4).iterrows()])
        top_arts = "\n".join([f"- {a['titre']} ({a['vues']} vues)" for a in top_articles[:5]])
        best_type = df.groupby("Type_Label")["Vues"].mean().idxmax()
        events_txt = "\n".join([f"- {e['name']} ({e['start']}): {e['desc']}" for e in events[:6]]) or "Aucun événement majeur"

        prompt = f"""Tu es rédacteur en chef adjoint du Journal du Geek (journaldugeek.com), site français couvrant : pop culture, nouvelles technologies, jeux vidéo, consommation et sciences.

Voici les données de la semaine écoulée :

**Top catégories (vues moyennes/article) :**
{top_cats}

**Format le plus performant cette semaine :** {best_type}

**Top articles de la semaine :**
{top_arts}

**Événements & sorties de la semaine prochaine :**
{events_txt}

Sur la base de ces données, propose **10 idées d'articles concrets** pour la semaine prochaine.
- Chaque idée doit avoir un **titre accrocheur** prêt à publier
- Indique la **catégorie** et le **format recommandé** (article, test, critique, dossier, bon plan)
- Priorise les sujets qui ont bien performé cette semaine
- Exploite les événements à venir quand c'est pertinent
- Adopte le ton 01net : direct, tech-focused, expert mais accessible

Format de réponse : liste numérotée, une idée par ligne."""

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    except Exception as e:
        return f"❌ Erreur : {e}"


def get_tech_news_rss() -> list:
    """Tech & gaming news from Google News RSS — no key needed."""
    queries = [
        "lancement+sortie+produit+tech+smartphone+tablette",
        "annonce+Apple+Samsung+Google+Microsoft+Sony",
        "sortie+jeu+video+annonce+Nintendo+Xbox+PlayStation",
    ]
    items = []
    seen = set()
    for q in queries:
        url = f"https://news.google.com/rss/search?q={q}&hl=fr&gl=FR&ceid=FR:fr"
        try:
            r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if not r.ok:
                continue
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:6]:
                raw_title = item.findtext("title", "")
                title = raw_title.split(" - ")[0].strip()
                if title in seen:
                    continue
                seen.add(title)
                pub = item.findtext("pubDate", "")
                try:
                    pub_dt = parsedate_to_datetime(pub)
                    pub_str = pub_dt.strftime("%d/%m")
                except Exception:
                    pub_str = ""
                source = raw_title.split(" - ")[-1].strip() if " - " in raw_title else ""
                link = item.findtext("link", "")
                items.append({"title": title, "date": pub_str, "source": source, "link": link})
        except Exception:
            continue
    return items[:12]


# Calendrier annuel des événements tech & gaming
_ANNUAL_EVENTS = [
    # (mois, j_debut, j_fin, nom, catégorie, description, url)
    (1,  7, 12, "🔌 CES Las Vegas",          "💻 Tech",       "Plus grand salon tech mondial",                     "https://www.ces.tech"),
    (2, 24, 28, "📱 MWC Barcelone",           "📱 Tech",       "Mobile World Congress — annonces smartphones",      "https://www.mwcbarcelona.com"),
    (3, 10, 10, "🍄 Mar10 Day",               "🎮 Jeux Vidéo", "Journée Mario — promos et annonces Nintendo",       "https://www.nintendo.fr"),
    (3, 17, 22, "🎮 GDC San Francisco",       "🎮 Jeux Vidéo", "Game Developers Conference",                        "https://gdconf.com"),
    (4,  1,  1, "🤡 April Fools' Day",        "📰 Divers",     "Annonces farfelues des marques tech",               ""),
    (4, 22, 22, "🌍 Earth Day",               "🌱 Éco",        "Annonces éco-responsables des marques",             ""),
    (5,  6, 15, "🤖 Google I/O",              "💻 Tech",       "Keynote Google — Android, IA, Pixel",               "https://io.google"),
    (6,  2,  9, "🍎 Apple WWDC",              "💻 Tech",       "Keynote Apple — iOS, macOS, nouveaux produits",     "https://developer.apple.com/wwdc"),
    (6,  8, 15, "🎮 Xbox Games Showcase",     "🎮 Jeux Vidéo", "Annonces Xbox & PC Game Pass",                      "https://xbox.com"),
    (6, 20, 25, "🎮 PlayStation Showcase",    "🎮 Jeux Vidéo", "Annonces Sony PlayStation",                         "https://playstation.com"),
    (7,  8, 17, "🛒 Amazon Prime Day",        "🛒 Conso",      "48h de méga promos Amazon",                         "https://www.amazon.fr"),
    (8, 20, 25, "🎮 Gamescom Cologne",        "🎮 Jeux Vidéo", "Plus grand salon gaming d'Europe",                  "https://www.gamescom.global"),
    (9,  5,  8, "📺 IFA Berlin",              "💻 Tech",       "Salon grand public — TV, audio, smartphones",       "https://www.ifa-berlin.com"),
    (9, 24, 28, "🎮 Tokyo Game Show",         "🎮 Jeux Vidéo", "Salon gaming japonais — annonces Japan",            "https://tgs.cesa.or.jp"),
    (10, 1,  5, "🍎 Apple Event automne",     "💻 Tech",       "iPhone, Mac, iPad — annonces de rentrée",           "https://apple.com"),
    (11, 1, 10, "🎮 Xbox/PlayStation Sales",  "🎮 Jeux Vidéo", "Périodes de promos jeux majeurs",                   ""),
    (11,20, 30, "🛒 Black Friday",            "🛒 Conso",      "Semaine de promos — électronique en tête",          ""),
    (12, 7, 10, "🏆 The Game Awards",         "🎮 Jeux Vidéo", "Cérémonie + annonces jeux — LA",                    "https://thegameawards.com"),
]


def get_upcoming_events(week_start_str: str, lookahead_days: int = 14) -> list:
    """Return annual tech/gaming events in the next lookahead_days."""
    today = datetime.strptime(week_start_str, "%Y-%m-%d").date()
    horizon = today + timedelta(days=lookahead_days)
    year = today.year
    results = []
    for mo, d1, d2, name, cat, desc, url in _ANNUAL_EVENTS:
        start = date(year, mo, d1)
        end   = date(year, mo, d2)
        if start <= horizon and end >= today:
            days_to = (start - today).days
            if days_to < 0:
                label = "En cours" if end >= today else ""
            elif days_to == 0:
                label = "Aujourd'hui !"
            elif days_to == 1:
                label = "Demain"
            else:
                label = f"Dans {days_to}j"
            results.append({
                "name": name, "cat": cat, "desc": desc, "url": url,
                "start": start.strftime("%d/%m"),
                "end": end.strftime("%d/%m"),
                "same_day": d1 == d2,
                "label": label,
                "urgent": days_to <= 3,
            })
    return sorted(results, key=lambda x: x["start"][-2:] + x["start"][:2])


# ─────────────────────────────────────────────
# ARCHIVAGE
# ─────────────────────────────────────────────

def auto_archive(source, filename: str):
    """Save CSV to GitHub (cloud) or local archives/ folder (local)."""
    if isinstance(source, bytes):
        csv_bytes = source
    else:
        with open(source, "rb") as f:
            csv_bytes = f.read()

    if _is_cloud():
        gh_save_archive(csv_bytes, filename)
    else:
        dest = os.path.join(ARCHIVE_DIR, filename)
        if not os.path.exists(dest):
            with open(dest, "wb") as f:
                f.write(csv_bytes)


@st.cache_data(show_spinner=False, ttl=300)
def load_archive_summaries() -> pd.DataFrame:
    rows = []
    if _is_cloud():
        filenames = gh_list_archives()
    else:
        filenames = sorted(
            [f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".csv")], reverse=True
        )

    MOIS_FR = ["janvier","février","mars","avril","mai","juin",
               "juillet","août","septembre","octobre","novembre","décembre"]

    for fname in filenames:
        try:
            if _is_cloud():
                csv_bytes = gh_load_archive(fname)
                if csv_bytes is None:
                    continue
                import io
                df_a = load_data(io.BytesIO(csv_bytes))
            else:
                df_a = load_data(os.path.join(ARCHIVE_DIR, fname))

            m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})", fname)
            if m:
                d_s = datetime.strptime(m.group(1), "%Y-%m-%d")
                d_e = datetime.strptime(m.group(2), "%Y-%m-%d")
            else:
                d_s = df_a["Date"].min().to_pydatetime()
                d_e = df_a["Date"].max().to_pydatetime()
            w_s = d_s.strftime("%Y-%m-%d")
            nb_jours = (d_e - d_s).days

            is_monthly = nb_jours > 20
            if is_monthly:
                label = f"{MOIS_FR[d_s.month - 1].capitalize()} {d_s.year}"
                type_label = "🗓️ Mensuel"
            else:
                label = f"{d_s.strftime('%d/%m')} → {d_e.strftime('%d/%m/%Y')}"
                type_label = "📅 Hebdo"

            top_auth = df_a.groupby("Rédacteur")["Vues"].sum().idxmax()
            top_art  = df_a.loc[df_a["Vues"].idxmax(), "Titre"]
            rows.append({
                "Période":       label,
                "Type":          type_label,
                "week_start":    w_s,
                "filename":      fname,
                "Vues totales":  df_a["Vues"].sum(),
                "Articles":      len(df_a),
                "Vues moyennes": int(df_a["Vues"].mean()),
                "Top rédacteur": top_auth,
                "Top article":   top_art[:70] + ("…" if len(top_art) > 70 else ""),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


def _is_cloud() -> bool:
    """Detect if running on Streamlit Cloud (st.secrets has github_token)."""
    try:
        return bool(st.secrets.get("github_token", ""))
    except Exception:
        return False


def _gh_headers() -> dict:
    try:
        return {"Authorization": f"token {st.secrets['github_token']}",
                "Accept": "application/vnd.github.v3+json"}
    except Exception:
        return {}


def _gh_repo() -> str:
    try:
        return st.secrets.get("github_repo", "")
    except Exception:
        return ""


def gh_list_archives() -> list[str]:
    r = requests.get(
        f"https://api.github.com/repos/{_gh_repo()}/contents/archives",
        headers=_gh_headers(), timeout=8,
    )
    if r.ok:
        return sorted([f["name"] for f in r.json() if f["name"].endswith(".csv")], reverse=True)
    return []


def gh_save_archive(csv_bytes: bytes, filename: str):
    url = f"https://api.github.com/repos/{_gh_repo()}/contents/archives/{filename}"
    r = requests.get(url, headers=_gh_headers(), timeout=8)
    if r.status_code == 200:
        return  # Already exists
    requests.put(url, headers=_gh_headers(), timeout=10, json={
        "message": f"Archive semaine {filename}",
        "content": base64.b64encode(csv_bytes).decode(),
    })


def gh_load_archive(filename: str) -> bytes | None:
    url = f"https://api.github.com/repos/{_gh_repo()}/contents/archives/{filename}"
    r = requests.get(url, headers=_gh_headers(), timeout=8)
    if r.ok:
        return base64.b64decode(r.json()["content"])
    return None


def gh_delete_archive(filename: str):
    url = f"https://api.github.com/repos/{_gh_repo()}/contents/archives/{filename}"
    r = requests.get(url, headers=_gh_headers(), timeout=8)
    if r.ok:
        sha = r.json()["sha"]
        requests.delete(url, headers=_gh_headers(), timeout=8, json={
            "message": f"Suppression archive {filename}",
            "sha": sha,
        })


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo-01net.png")


def logo_b64() -> str:
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

_logo = logo_b64()


# ─────────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────────
def _get_app_password() -> str:
    try:
        return st.secrets.get("app_password", "")
    except Exception:
        pass
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("app_password", "")
        except Exception:
            pass
    return ""


_stored_pw = _get_app_password()
if _stored_pw and not st.session_state.get("authenticated"):
    st.markdown("""
    <style>
    [data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 1.2, 1])
    with col_c:
        if _logo:
            st.markdown(
                f"<div style='text-align:center;padding:3rem 0 1.5rem;'>"
                f"<img src='data:image/png;base64,{_logo}' "
                f"style='width:110px;border-radius:16px;box-shadow:0 6px 24px rgba(232,0,13,.25);'>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "<h2 style='text-align:center;color:#E8000D;font-weight:800;"
            "margin-bottom:0.3rem;'>Dashboard Rédaction</h2>"
            "<p style='text-align:center;color:#999;font-size:.85rem;"
            "margin-bottom:1.8rem;'>01net — accès réservé</p>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            pw_input = st.text_input(
                "Mot de passe",
                type="password",
                placeholder="Entrez le mot de passe…",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
        if submitted:
            if pw_input == _stored_pw:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
    st.stop()


with st.sidebar:
    if _logo:
        st.markdown(
            f"<div style='text-align:center;padding:.5rem 0 1rem;'>"
            f"<img src='data:image/png;base64,{_logo}' style='width:90px;border-radius:14px;box-shadow:0 4px 16px rgba(0,0,0,.3);'>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("---")

    # File upload
    st.markdown("### 📂 Fichier de la semaine")
    uploaded = st.file_uploader("Importer un nouveau CSV", type=["csv"])
    if uploaded:
        st.cache_data.clear()
    if st.button("🗑️ Vider le cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Archives
    archived_files = gh_list_archives() if _is_cloud() else sorted(
        [f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".csv")], reverse=True
    )
    archive_choice = None
    if not uploaded and archived_files:
        st.markdown("### 🗂️ Semaines archivées")
        archive_choice = st.selectbox(
            "Charger une semaine précédente",
            ["— Sélectionner —"] + archived_files,
        )
        if archive_choice == "— Sélectionner —":
            archive_choice = None

    st.markdown("---")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = None
filename = ""

if uploaded:
    auto_archive(uploaded.getvalue(), uploaded.name)
    df = load_data(uploaded)
    filename = uploaded.name
elif archive_choice:
    if _is_cloud():
        import io
        _bytes = gh_load_archive(archive_choice)
        df = load_data(io.BytesIO(_bytes)) if _bytes else None
    else:
        df = load_data(os.path.join(ARCHIVE_DIR, archive_choice))
    filename = archive_choice

# ─────────────────────────────────────────────
# LANDING PAGE (no file)
# ─────────────────────────────────────────────
if df is None:
    st.title("📰 Dashboard Réunion Rédaction")
    st.markdown(
        """
        ### Bienvenue 👋

        Importez votre export CSV hebdomadaire pour afficher :

        | Onglet | Contenu |
        |---|---|
        | 📊 Vue d'ensemble | Vues totales, articles, auteurs, timeline |
        | 👥 Stats par auteur | Top 5 et flops de chaque rédacteur |
        | 📈 Tendances | Catégories, types, heatmap, insights |
        | 📅 Planning | Sorties ciné/TV (TMDB), événements tech, idées |

        👈 **Importez votre CSV dans la barre latérale pour commencer.**
        """
    )
    st.stop()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
w_start, w_end = week_dates(filename, df)
next_monday = (datetime.strptime(w_end, "%Y-%m-%d") + timedelta(days=2)).strftime("%d/%m/%Y")
is_monthly_file = (datetime.strptime(w_end, "%Y-%m-%d") - datetime.strptime(w_start, "%Y-%m-%d")).days > 20

_logo_tag = f"<img src='data:image/png;base64,{_logo}' style='height:52px;border-radius:9px;margin-right:1rem;vertical-align:middle;box-shadow:0 2px 8px rgba(0,0,0,.2);'>" if _logo else ""
st.html(
    f"""<div style='
        background: linear-gradient(135deg, #B50009 0%, #E8000D 100%);
        border-radius: 16px; padding: 1.4rem 2rem; margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(181,0,9,.3);
        display:flex; align-items:center; gap:0;
    '>
        {_logo_tag}
        <div>
            <div style='font-size:1.55rem;font-weight:900;color:#fff;letter-spacing:-.5px;line-height:1.1;'>
                Réunion de Rédaction
            </div>
            <div style='color:rgba(255,255,255,.75);font-size:.9rem;margin-top:.3rem;font-weight:500;'>
                📅 Semaine du <b style='color:#fff;'>{datetime.strptime(w_start, '%Y-%m-%d').strftime('%d/%m/%Y')}</b>
                au <b style='color:#fff;'>{datetime.strptime(w_end, '%Y-%m-%d').strftime('%d/%m/%Y')}</b>
                &nbsp;·&nbsp; Réunion lundi <b style='color:#fff;'>{next_monday}</b>
            </div>
        </div>
    </div>"""
)

if is_monthly_file:
    tab1, tab2, tab3, tab5 = st.tabs(
        ["📊 Vue d'ensemble", "👥 Stats par auteur", "📈 Tendances", "🗂️ Historique"]
    )
    tab4 = None
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Vue d'ensemble", "👥 Stats par auteur", "📈 Tendances", "📅 Planning semaine", "🗂️ Historique"]
    )

# ─────────────────────────────────────────────
# TAB 1 — VUE D'ENSEMBLE
# ─────────────────────────────────────────────
with tab1:
    total_vues = df["Vues"].sum()
    total_arts = len(df)
    total_auteurs = df["Rédacteur"].nunique()
    avg_vues = int(df["Vues"].mean())
    top_row = df.loc[df["Vues"].idxmax()]

    kpis = [
        ("👁️", fmt(total_vues),      "Vues totales"),
        ("📝", str(total_arts),       "Articles publiés"),
        ("✍️", str(total_auteurs),    "Rédacteurs actifs"),
        ("📊", fmt(avg_vues),         "Vues moyennes"),
        ("🏆", fmt(top_row["Vues"]),  "Record de la semaine"),
    ]
    cards_html = "".join(
        f"<div class='kpi-card'><div class='kpi-icon'>{ico}</div>"
        f"<div class='kpi-val'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>"
        for ico, val, lbl in kpis
    )
    st.markdown(f"<div class='kpi-grid'>{cards_html}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:.85rem;color:#8B0009;margin-top:-.5rem;margin-bottom:1rem;'>"
        f"🏆 <i>{top_row['Titre'][:90]}</i> — {top_row['Rédacteur']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col_l, col_r = st.columns([3, 2])

    with col_l:
        author_vues = (
            df.groupby("Rédacteur")["Vues"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig = px.bar(
            author_vues, x="Vues", y="Rédacteur", orientation="h",
            title="Vues totales par rédacteur",
            color="Vues", color_continuous_scale=["#FFE5E5", "#E8000D", "#8B0009"],
            labels={"Vues": "Vues totales", "Rédacteur": ""},
        )
        fig.update_layout(coloraxis_showscale=False, height=420, margin=dict(l=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        type_vues = df.groupby("Type_Label")["Vues"].sum().reset_index()
        fig2 = px.pie(
            type_vues, values="Vues", names="Type_Label",
            title="Répartition des vues par format",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        fig2.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig2, use_container_width=True)

    # Timeline journalière — semaine uniquement
    if not is_monthly_file:
        week_monday = datetime.strptime(w_start, "%Y-%m-%d")
        week_monday -= timedelta(days=week_monday.weekday())
        all_days = pd.DataFrame({
            "Date": [week_monday.date() + timedelta(days=i) for i in range(7)]
        })
        daily_raw = df.groupby(df["Date"].dt.date)["Vues"].sum().reset_index()
        daily_raw.columns = ["Date", "Vues"]
        daily = all_days.merge(daily_raw, on="Date", how="left").fillna(0)
        daily["Vues"] = daily["Vues"].astype(int)
        daily["Jour"] = daily["Date"].apply(lambda d: JOURS_FR[d.strftime("%A")] + " " + d.strftime("%d/%m"))
        fig3 = px.area(
            daily, x="Jour", y="Vues",
            title="Vues par jour (lundi → dimanche)",
            color_discrete_sequence=["#E8000D"],
            markers=True,
        )
        fig3.update_layout(height=240, margin=dict(t=40, b=20))
        st.plotly_chart(fig3, use_container_width=True)

    # Top 10
    st.markdown("### 🏆 Top 10 articles de la semaine")
    top10 = df.nlargest(10, "Vues")[["Titre", "Rédacteur", "Type_Label", "Vues", "Date"]].copy()
    top10["Date"] = top10["Date"].dt.strftime("%d/%m %H:%M")
    top10["Vues"] = top10["Vues"].apply(fmt)
    top10 = top10.rename(columns={"Type_Label": "Format"})
    st.dataframe(top10.reset_index(drop=True), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# TAB 2 — STATS PAR AUTEUR
# ─────────────────────────────────────────────
with tab2:
    st.markdown("### 👥 Performance par rédacteur")

    authors_sorted = (
        df.groupby("Rédacteur")["Vues"].sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    selected = st.multiselect(
        "Filtrer les rédacteurs",
        authors_sorted,
        default=authors_sorted,
    )

    if not selected:
        st.warning("Sélectionnez au moins un rédacteur.")
        st.stop()

    sub = df[df["Rédacteur"].isin(selected)]

    # Tableau récap
    summary = (
        sub.groupby("Rédacteur")
        .agg(
            Articles=("Titre", "count"),
            Vues_totales=("Vues", "sum"),
            Vues_moyennes=("Vues", "mean"),
            Meilleure_perf=("Vues", "max"),
            Mots_moy=("Mots", "mean"),
        )
        .round(0)
        .astype(int)
        .sort_values("Vues_totales", ascending=False)
    )
    display_sum = summary.copy()
    for col in ["Vues_totales", "Vues_moyennes", "Meilleure_perf"]:
        display_sum[col] = display_sum[col].apply(fmt)
    st.dataframe(display_sum, use_container_width=True)

    st.markdown("---")
    st.markdown("### Top 5 / Flops par rédacteur")

    cols = st.columns(2)
    for i, author in enumerate(
        sorted(selected, key=lambda a: df[df["Rédacteur"] == a]["Vues"].sum(), reverse=True)
    ):
        adf = df[df["Rédacteur"] == author].sort_values("Vues", ascending=False)
        nb = len(adf)
        avg = int(adf["Vues"].mean())
        total = adf["Vues"].sum()

        with cols[i % 2]:
            st.markdown(f"#### ✍️ {author}")
            st.caption(f"{nb} articles · {fmt(total)} vues · moy. {fmt(avg)}")

            top5 = adf.head(5)
            flops = adf[~adf.index.isin(top5.index)].tail(5)

            c_top, c_flop = st.columns(2)
            with c_top:
                st.markdown("**🟢 Top 5**")
                for rank, (_, row) in enumerate(top5.iterrows(), 1):
                    titre = row["Titre"][:62] + ("…" if len(row["Titre"]) > 62 else "")
                    st.markdown(
                        f'<div class="art-card top">'
                        f'<span class="art-rank top">#{rank} &nbsp;{fmt(row["Vues"])}</span>'
                        f'<span class="art-title">{titre}</span></div>',
                        unsafe_allow_html=True,
                    )
            with c_flop:
                st.markdown("**🔴 Flops**")
                if flops.empty:
                    st.caption("Pas assez d'articles.")
                else:
                    for rank, (_, row) in enumerate(flops.iterrows(), 1):
                        titre = row["Titre"][:62] + ("…" if len(row["Titre"]) > 62 else "")
                        st.markdown(
                            f'<div class="art-card flop">'
                            f'<span class="art-rank flop">↓{fmt(row["Vues"])}</span>'
                            f'<span class="art-title">{titre}</span></div>',
                            unsafe_allow_html=True,
                        )
            st.markdown("---")

# ─────────────────────────────────────────────
# TAB 3 — TENDANCES
# ─────────────────────────────────────────────
with tab3:
    st.markdown("### 📈 Analyse des tendances")

    cat_stats = (
        df.groupby("Catégorie")
        .agg(Vues=("Vues", "sum"), Articles=("Titre", "count"), Vues_moy=("Vues", "mean"))
        .sort_values("Vues", ascending=False)
        .reset_index()
    )
    fig = px.bar(
        cat_stats, x="Catégorie", y="Vues",
        color="Catégorie",
        title="Vues totales par catégorie",
        text=cat_stats["Articles"].apply(lambda n: f"{n} art."),
        labels={"Vues": "Vues totales", "Catégorie": ""},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, xaxis_tickangle=-30, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Insights automatiques
    st.markdown("---")
    st.markdown("#### 💡 Insights de la semaine")
    ia, ib, ic = st.columns(3)

    best_cat = cat_stats.iloc[0]
    best_type_perf = (
        df.groupby("Type_Label")
        .agg(Vues_moy=("Vues", "mean"), Type_Label=("Type_Label", "first"))
        .sort_values("Vues_moy", ascending=False)
        .reset_index(drop=True)
    )
    best_day_en = df.groupby(df["Date"].dt.day_name())["Vues"].mean().idxmax()
    best_day_fr = JOURS_FR.get(best_day_en, best_day_en)

    ia.success(
        f"**Catégorie phare**\n\n"
        f"{best_cat['Catégorie']}\n\n"
        f"{fmt(int(best_cat['Vues_moy']))} vues/article"
    )
    ib.info(
        f"**Format le plus rentable**\n\n"
        f"{best_type_perf.iloc[0]['Type_Label']}\n\n"
        f"{fmt(int(best_type_perf.iloc[0]['Vues_moy']))} vues/article"
    )
    ic.warning(
        f"**Meilleur jour de publication**\n\n"
        f"{best_day_fr}\n\n"
        f"Basé sur les vues moyennes"
    )

    # Tableau complet catégories
    with st.expander("📋 Détail par catégorie"):
        cat_detail = cat_stats.copy()
        cat_detail["Vues"] = cat_detail["Vues"].apply(fmt)
        cat_detail["Vues_moy"] = cat_detail["Vues_moy"].apply(lambda x: fmt(int(x)))
        cat_detail.columns = ["Catégorie", "Vues totales", "Articles", "Vues moyennes"]
        st.dataframe(cat_detail, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📆 Production quotidienne")

    # Détection mode mensuel
    _d_start = datetime.strptime(w_start, "%Y-%m-%d")
    _d_end   = datetime.strptime(w_end,   "%Y-%m-%d")
    is_monthly = (_d_end - _d_start).days > 20

    if is_monthly:
        # Tous les jours du mois
        nb_days = (_d_end.date() - _d_start.date()).days + 1
        all_days2 = pd.DataFrame({
            "Date": [_d_start.date() + timedelta(days=i) for i in range(nb_days)]
        })
        daily_count_raw = df.groupby(df["Date"].dt.date).size().reset_index(name="Articles")
        daily_count_raw.columns = ["Date", "Articles"]
        daily_count = all_days2.merge(daily_count_raw, on="Date", how="left").fillna(0)
        daily_count["Articles"] = daily_count["Articles"].astype(int)
        daily_count["Jour"] = daily_count["Date"].apply(lambda d: d.strftime("%d/%m"))
        bar_title = f"Articles publiés par jour ({_d_start.strftime('%d/%m')} → {_d_end.strftime('%d/%m/%Y')})"
    else:
        # 7 jours lundi→dimanche complets
        week_monday2 = _d_start - timedelta(days=_d_start.weekday())
        all_days2 = pd.DataFrame({
            "Date": [week_monday2.date() + timedelta(days=i) for i in range(7)]
        })
        daily_count_raw = df.groupby(df["Date"].dt.date).size().reset_index(name="Articles")
        daily_count_raw.columns = ["Date", "Articles"]
        daily_count = all_days2.merge(daily_count_raw, on="Date", how="left").fillna(0)
        daily_count["Articles"] = daily_count["Articles"].astype(int)
        daily_count["Jour"] = daily_count["Date"].apply(lambda d: JOURS_FR[d.strftime("%A")] + " " + d.strftime("%d/%m"))
        bar_title = "Nombre d'articles publiés par jour (lundi → dimanche)"

    fig_daily = px.bar(
        daily_count, x="Jour", y="Articles",
        title=bar_title,
        labels={"Jour": "", "Articles": "Articles"},
        color="Articles",
        color_continuous_scale=["#FFE5E5", "#E8000D", "#8B0009"],
        text="Articles",
    )
    fig_daily.update_traces(textposition="outside")
    fig_daily.update_layout(showlegend=False, coloraxis_showscale=False, height=300, margin=dict(t=40, b=10))
    st.plotly_chart(fig_daily, use_container_width=True)

    # Heatmap articles par rédacteur par jour
    st.markdown("#### ✍️ Articles par rédacteur par jour")
    ordered_cols = daily_count["Jour"].tolist()
    if is_monthly:
        df["Jour_label"] = df["Date"].apply(lambda d: d.strftime("%d/%m"))
    else:
        df["Jour_label"] = df["Date"].apply(
            lambda d: JOURS_FR[d.strftime("%A")] + " " + d.strftime("%d/%m")
        )
    pivot_redac = df.pivot_table(
        values="Titre", index="Rédacteur", columns="Jour_label",
        aggfunc="count", fill_value=0,
    ).reindex(columns=ordered_cols, fill_value=0)
    heat_height = max(380, len(pivot_redac) * 40) if is_monthly else 380
    fig_heat = px.imshow(
        pivot_redac,
        text_auto=True,
        color_continuous_scale=["#FFE5E5", "#E8000D", "#8B0009"],
        aspect="auto",
        labels={"x": "", "y": "", "color": "Articles"},
    )
    fig_heat.update_layout(height=heat_height, margin=dict(t=10, b=10))
    fig_heat.update_coloraxes(showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────
# TAB 4 — PLANNING
# ─────────────────────────────────────────────
if tab4 is not None:
    with tab4:
        nw_start = datetime.strptime(w_end, "%Y-%m-%d") + timedelta(days=2)
        nw_end = nw_start + timedelta(days=6)

        st.markdown(
            f"### 📅 Semaine du {nw_start.strftime('%d/%m/%Y')} au {nw_end.strftime('%d/%m/%Y')}"
        )
        st.markdown("---")

        # ── Calendrier événements ──
        st.markdown("#### 📅 Événements Tech & Gaming")
        events = get_upcoming_events(nw_start.strftime("%Y-%m-%d"), lookahead_days=14)
        if events:
            for ev in events:
                date_range = ev["start"] if ev["same_day"] else f"{ev['start']} → {ev['end']}"
                badge_color = "#dc2626" if ev["urgent"] else "#E8000D"
                badge = f"<span style='background:{badge_color};color:#fff;font-size:.7rem;font-weight:700;padding:.15rem .5rem;border-radius:20px;margin-left:.4rem;'>{ev['label']}</span>"
                title_html = f"<a href='{ev['url']}' target='_blank' style='color:#E8000D;font-weight:700;text-decoration:none;'>{ev['name']}</a>" if ev["url"] else f"<b>{ev['name']}</b>"
                st.markdown(
                    f"<div style='background:#fff;border:1px solid #FFCCCC;border-radius:10px;padding:.6rem .9rem;margin:.3rem 0;'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                    f"<span>{title_html}{badge}</span>"
                    f"<span style='font-size:.78rem;color:#8B0009;font-weight:600;'>{date_range}</span>"
                    f"</div>"
                    f"<div style='font-size:.78rem;color:#666;margin-top:.15rem;'>{ev['cat']} &nbsp;·&nbsp; {ev['desc']}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucun événement majeur dans les 2 prochaines semaines.")

        st.markdown("#### 📰 Actualités Tech & Lancements")
        with st.spinner("Chargement…"):
            tech_news = get_tech_news_rss()
        if tech_news:
            for n in tech_news:
                date_str = f"<span style='color:#8B0009;font-size:.78rem;'> — {n['date']}</span>" if n["date"] else ""
                src = f"<span style='color:#999;font-size:.75rem;'> ({n['source']})</span>" if n["source"] else ""
                link = n.get("link", "")
                title_html = f"<a href='{link}' target='_blank' style='color:#1a0000;font-weight:600;text-decoration:none;'>{n['title']}</a>" if link else f"<b>{n['title']}</b>"
                st.markdown(
                    f"<div style='padding:.35rem 0;border-bottom:1px solid #f0e8ec;font-size:.84rem;'>"
                    f"↗ {title_html}{date_str}{src}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Impossible de charger les actualités (vérifiez votre connexion).")
        st.text_area("Notes complémentaires", placeholder="Autres événements, keynotes, annonces à couvrir…", height=70, label_visibility="collapsed", key="tech_notes")

        st.markdown("#### 📈 Thèmes porteurs (issus de cette semaine)")
        top3_cats = df.groupby("Catégorie")["Vues"].mean().nlargest(3)
        for cat, moy in top3_cats.items():
            st.markdown(f"- **{cat}** — {fmt(int(moy))} vues/article en moy.")

        st.markdown("#### ✨ Idées d'articles")
        if st.button("🤖 Générer des idées avec Claude", use_container_width=True):
            top_arts_data = [
                {"titre": row["Titre"][:80], "vues": fmt(row["Vues"])}
                for _, row in df.nlargest(5, "Vues").iterrows()
            ]
            with st.spinner("Claude réfléchit…"):
                ideas_text = generate_article_ideas(df, events, top_arts_data)
            st.session_state["generated_ideas"] = ideas_text

        if "generated_ideas" in st.session_state:
            st.markdown(
                f"<div style='background:#fff;border:1px solid #FFCCCC;border-radius:12px;"
                f"padding:1rem 1.2rem;font-size:.88rem;line-height:1.7;white-space:pre-wrap;'>"
                f"{st.session_state['generated_ideas']}</div>",
                unsafe_allow_html=True,
            )
            if st.button("🗑️ Effacer", key="clear_ideas"):
                del st.session_state["generated_ideas"]
                st.rerun()

        st.text_area(
            "Notes libres",
            placeholder="Vos propres idées…",
            height=80,
            label_visibility="collapsed",
            key="ideas_manual",
        )

        # ── Brief auto ──
        st.markdown("---")
        st.markdown("#### 📋 Récap automatique pour l'équipe")

        top3 = df.nlargest(3, "Vues")
        top3_authors = df.groupby("Rédacteur")["Vues"].sum().nlargest(3).index.tolist()
        best_cat_name = df.groupby("Catégorie")["Vues"].mean().idxmax()
        best_type_name = df.groupby("Type_Label")["Vues"].mean().idxmax()

        brief_lines = [
            f"📊 Bilan semaine {datetime.strptime(w_start, '%Y-%m-%d').strftime('%d/%m')} → {datetime.strptime(w_end, '%Y-%m-%d').strftime('%d/%m/%Y')}",
            "",
            f"✅  {total_arts} articles publiés · {fmt(df['Vues'].sum())} vues au total",
            f"📊  Vues moyennes : {fmt(int(df['Vues'].mean()))} / article",
            "",
            f"🏆  Top article : {top3.iloc[0]['Titre'][:70]} ({fmt(top3.iloc[0]['Vues'])} vues — {top3.iloc[0]['Rédacteur']})",
            f"🥈  2e : {top3.iloc[1]['Titre'][:70]} ({fmt(top3.iloc[1]['Vues'])} vues)",
            f"🥉  3e : {top3.iloc[2]['Titre'][:70]} ({fmt(top3.iloc[2]['Vues'])} vues)",
            "",
            f"📈  Catégorie phare : {best_cat_name}",
            f"🎯  Format le + rentable : {best_type_name}",
            f"✍️   Top rédacteurs : {', '.join(top3_authors)}",
        ]
        brief = "\n".join(brief_lines)

        st.code(brief, language=None)
        st.caption("Copiez ce texte pour votre email / Slack d'équipe.")

# ─────────────────────────────────────────────
# TAB 5 — HISTORIQUE
# ─────────────────────────────────────────────
with tab5:
    st.markdown("### 🗂️ Historique")

    hist = load_archive_summaries()

    if hist.empty:
        st.info("Aucune période archivée pour l'instant. Les données s'accumulent automatiquement à chaque chargement de CSV.")
    else:
        # ── Filtre type ──
        filtre = st.radio(
            "Afficher",
            ["📅 Hebdo", "🗓️ Mensuel"],
            horizontal=True,
            label_visibility="collapsed",
        )
        hist = hist[hist["Type"] == filtre].sort_values("week_start").reset_index(drop=True)

        nb_weeks = len(hist)

        # ── KPIs historique ──
        kpis_h = [
            ("📅", str(nb_weeks),                                 "Périodes archivées"),
            ("👁️", fmt(hist["Vues totales"].sum()),               "Vues cumulées"),
            ("📝", str(hist["Articles"].sum()),                    "Articles au total"),
            ("📈", fmt(int(hist["Vues totales"].mean())),          "Vues moy. / période"),
        ]
        cards_h = "".join(
            f"<div class='kpi-card'><div class='kpi-icon'>{ico}</div>"
            f"<div class='kpi-val'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>"
            for ico, val, lbl in kpis_h
        )
        st.markdown(f"<div class='kpi-grid'>{cards_h}</div>", unsafe_allow_html=True)

        # ── Évolution vues totales ──
        fig_h1 = px.area(
            hist, x="Période", y="Vues totales",
            title="Évolution des vues totales",
            color_discrete_sequence=["#E8000D"],
            markers=True,
        )
        fig_h1.update_layout(height=280, margin=dict(t=40, b=10), xaxis_tickangle=-20)
        st.plotly_chart(fig_h1, use_container_width=True)

        # ── Évolution articles + vues moyennes ──
        col_a, col_b = st.columns(2)
        with col_a:
            fig_h2 = px.bar(
                hist, x="Période", y="Articles",
                title="Nombre d'articles par période",
                color="Articles",
                color_continuous_scale=["#FFE5E5", "#E8000D", "#8B0009"],
                text="Articles",
            )
            fig_h2.update_traces(textposition="outside")
            fig_h2.update_layout(showlegend=False, coloraxis_showscale=False, height=280, margin=dict(t=40, b=10), xaxis_tickangle=-20)
            st.plotly_chart(fig_h2, use_container_width=True)

        with col_b:
            fig_h3 = px.line(
                hist, x="Période", y="Vues moyennes",
                title="Vues moyennes par article",
                color_discrete_sequence=["#E8000D"],
                markers=True,
            )
            fig_h3.update_layout(height=280, margin=dict(t=40, b=10), xaxis_tickangle=-20)
            st.plotly_chart(fig_h3, use_container_width=True)

        # ── Comparaison période courante vs précédente ──
        if nb_weeks >= 2:
            st.markdown("---")
            st.markdown("### 🔁 Comparaison période courante vs précédente")
            curr = hist.iloc[-1]
            prev = hist.iloc[-2]

            def delta_badge(curr_val, prev_val):
                if prev_val == 0:
                    return ""
                pct = (curr_val - prev_val) / prev_val * 100
                color = "#16a34a" if pct >= 0 else "#dc2626"
                arrow = "▲" if pct >= 0 else "▼"
                return f"<span style='color:{color};font-size:.85rem;font-weight:700;'>{arrow} {abs(pct):.1f}%</span>"

            comp_items = [
                ("👁️ Vues totales",   curr["Vues totales"],  prev["Vues totales"]),
                ("📝 Articles",        curr["Articles"],       prev["Articles"]),
                ("📊 Vues moyennes",   curr["Vues moyennes"], prev["Vues moyennes"]),
            ]
            cols_comp = st.columns(3)
            for col, (label, c_val, p_val) in zip(cols_comp, comp_items):
                badge = delta_badge(c_val, p_val)
                col.markdown(
                    f"<div style='background:#fff;border:1px solid #FFCCCC;border-top:4px solid #E8000D;"
                    f"border-radius:12px;padding:1rem 1.2rem;text-align:center;'>"
                    f"<div style='font-size:.72rem;font-weight:600;color:#8B0009;text-transform:uppercase;letter-spacing:.5px;'>{label}</div>"
                    f"<div style='font-size:1.6rem;font-weight:800;color:#E8000D;margin:.3rem 0;'>{fmt(c_val)}</div>"
                    f"<div style='font-size:.8rem;color:#999;'>vs {fmt(p_val)} &nbsp;{badge}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # ── Tableau récap ──
        st.markdown("---")
        st.markdown("### 📋 Tableau de bord")
        display_hist = hist.drop(columns=["week_start", "filename"], errors="ignore").copy()
        display_hist["Vues totales"]  = display_hist["Vues totales"].apply(fmt)
        display_hist["Vues moyennes"] = display_hist["Vues moyennes"].apply(fmt)
        st.dataframe(display_hist.reset_index(drop=True), use_container_width=True, hide_index=True)

        # ── Suppression ──
        st.markdown("---")
        st.markdown("### 🗑️ Supprimer une semaine archivée")
        archived_list = gh_list_archives() if _is_cloud() else sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".csv")], reverse=True)
        if archived_list:
            col_del, col_confirm = st.columns([3, 1])
            with col_del:
                to_delete = st.selectbox(
                    "Choisir la semaine à supprimer",
                    archived_list,
                    label_visibility="collapsed",
                )
            with col_confirm:
                if st.button("🗑️ Supprimer", type="primary"):
                    st.session_state["confirm_delete"] = to_delete

            if st.session_state.get("confirm_delete") == to_delete:
                st.warning(f"⚠️ Confirmer la suppression de **{to_delete}** ? Cette action est irréversible.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Oui, supprimer"):
                        if _is_cloud():
                            gh_delete_archive(to_delete)
                        else:
                            os.remove(os.path.join(ARCHIVE_DIR, to_delete))
                        st.cache_data.clear()
                        del st.session_state["confirm_delete"]
                        st.success(f"**{to_delete}** supprimé.")
                        st.rerun()
                with col_no:
                    if st.button("❌ Annuler"):
                        del st.session_state["confirm_delete"]
                        st.rerun()
