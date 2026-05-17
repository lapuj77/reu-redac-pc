# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run dashboard.py
```

The app runs on `http://localhost:8501`.

## Architecture

Single-file Streamlit app (`dashboard.py`, ~1500 lines) for an editorial tracking dashboard for Presse-Citron (presse-citron.net). Users upload a CSV export of articles and get interactive visualizations.

### Data flow

```
CSV Upload → load_data() → auto_archive() → Tab rendering
```

`load_data()` parses and enriches CSV data: standardizes column names, parses French number formatting (`1 234` → `1234`), categorizes articles by title keywords, maps type labels, and filters excluded authors.

**Weekly vs monthly mode**: if the date span in the data is < 20 days, the app renders 5 tabs (including Planning); otherwise 4 tabs (Planning hidden). This affects chart granularity too.

### Key sections in `dashboard.py`

| Lines | Section |
|-------|---------|
| 18–224 | Streamlit page config + all CSS (Presse-Citron brand, sidebar, custom components) |
| 225–380 | Constants: `CATEGORIES`, `TYPE_LABELS`, `EXCLUDED_AUTHORS`, utility functions |
| 382–463 | Data processing: `load_data()`, `week_dates()`, TMDB/RAWG API fetchers |
| 465–618 | AI & external: `generate_article_ideas()` (Claude API), Google News RSS, annual events calendar |
| 619–757 | Storage: `auto_archive()`, GitHub helpers, archive loading |
| 759–865 | Sidebar: auth (password gate), file upload, archive selection |
| 868–948 | Main flow: load data, detect mode, render header + tabs |
| 949–1516 | Tabs: Overview, Authors, Trends, Planning, History |

### Configuration

Loaded in priority order: Streamlit Cloud secrets → `config.json` → `.streamlit/secrets.toml`.

Required keys: `app_password`, `anthropic_key`, `tmdb_key`, `rawg_key`, `github_token`, `github_repo`.

If API keys are absent, features fail gracefully (empty results, "key missing" messages — never exceptions during rendering).

### Categorization

Articles are auto-categorized by case-insensitive keyword matching against the `CATEGORIES` dict (line ~278). Fallback category is "Divers". To add a category, add an entry to that dict.

### Storage

- Local: archives saved to `/archives/` folder
- Cloud (Streamlit Cloud): archives saved to GitHub `/archives/` via API when `github_token` + `github_repo` are set

### Styling

All CSS is inline in `st.markdown()` at the top. Brand color: `#00c853` (vert Presse-Citron officiel). Thousands separator uses French narrow no-break space (` `). There's a multi-selector CSS workaround for sidebar buttons on Streamlit Cloud (lines 78–93).

### External APIs

All external calls use 8-second timeouts and return empty lists/dicts on failure. TMDB and RAWG are called only on Planning tab demand. The annual tech/gaming events calendar (`_ANNUAL_EVENTS`, line ~562) is hardcoded and filters by a lookahead window from the current date.
