# Dashboard Rédaction — 01net

Dashboard interne de suivi éditorial pour les réunions de rédaction.

---

## Lancement en local

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Ou double-cliquer sur `lancer_dashboard.bat`.

L'app s'ouvre sur `http://localhost:8501`.

---

## Déploiement Streamlit Cloud

1. Connecte-toi sur [share.streamlit.io](https://share.streamlit.io)
2. **New app** → repo `lapuj77/reu-redac-01`, branch `master`, fichier `dashboard.py`
3. **Advanced settings → Secrets** :

```toml
app_password = "ton_mot_de_passe"
```

4. **Deploy**

---

## Utilisation

### Charger un fichier
- Importer un CSV via la sidebar (bouton upload)
- Ou charger une semaine archivée depuis la liste

### Format du CSV attendu
Séparateur `;`, encodage `UTF-8`, colonnes dans cet ordre :

| Titre | Type | Rédacteur | Mots | Vues | Date |

### Fichiers hebdo vs mensuel
Le dashboard détecte automatiquement le type de fichier selon l'écart de dates :
- **< 20 jours** → vue hebdomadaire (tous les onglets disponibles)
- **> 20 jours** → vue mensuelle (onglet Planning masqué, graphiques adaptés)

---

## Onglets

| Onglet | Contenu |
|---|---|
| 📊 Vue d'ensemble | KPIs, répartition par auteur/format, Top 10 |
| 👥 Stats par auteur | Top 5 et flops par rédacteur |
| 📈 Tendances | Catégories, heatmap production, calendrier |
| 📅 Planning semaine | Événements tech, actualités, idées IA *(hebdo uniquement)* |
| 🗂️ Historique | Évolution sur les périodes archivées |

---

## Archivage

Les fichiers chargés sont automatiquement sauvegardés dans `archives/` (local) ou sur GitHub (cloud).  
Le cache peut être vidé manuellement via le bouton **🗑️ Vider le cache** dans la sidebar.

---

## Stack

- [Streamlit](https://streamlit.io) — interface
- [Pandas](https://pandas.pydata.org) — traitement des données
- [Plotly](https://plotly.com) — graphiques
- [Anthropic Claude](https://anthropic.com) — génération d'idées d'articles
