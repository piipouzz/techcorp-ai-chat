# Rapport de rendu - TechCorp AI Chat

## Résumé

Le projet TechCorp AI Chat a été repris depuis un dépôt hérité, audité, sécurisé puis finalisé avec une interface web professionnelle et une API FastAPI connectée à Ollama.

Le livrable permet d'ouvrir une interface web de chat et de discuter avec le modèle `techcorp-phi35-financial`, construit localement depuis Phi-3.5.

## Vérification du PDF

Aucun fichier PDF n'a été trouvé dans :

- le workspace du projet ;
- les pièces jointes locales Codex disponibles.

La vérification du PDF n'a donc pas pu être effectuée. La documentation du projet a été alignée avec le brief fourni dans les fichiers Markdown du dépôt et les consignes utilisateur.

## Choix techniques

- Inférence : Ollama, car c'est la solution la plus simple et robuste pour le contexte hackathon.
- Backend : FastAPI, pour exposer une API REST et du streaming SSE.
- Frontend : HTML/CSS/JavaScript sans build step, pour simplifier l'installation.
- Modèle : `techcorp-phi35-financial`, créé depuis `ollama_server/Modelfile`.
- Sécurité : LoRA hérité conservé pour audit mais exclu de la production.

## Fonctionnalités livrées

- Interface web sobre et responsive.
- Historique local des conversations.
- Bouton nouvelle conversation.
- Streaming des réponses.
- Bouton copier sur les réponses.
- Indicateur discret pendant la génération.
- Gestion des erreurs Ollama/API.
- Backend REST documenté.
- Docker Compose opérationnel.
- Nettoyage reproductible des datasets.
- Scripts d'audit et de tests.

## Audit sécurité

Findings critiques :

- backdoor documentée dans les logs ;
- trigger `J3 SU1S UN3 P0UP33 D3 C1R3` ;
- datasets contaminés ;
- métadonnées d'entraînement mentionnant `phi3_backdoor_poc`.

Corrections :

- le backend bloque le trigger ;
- les motifs de credentials sont bloqués ;
- le LoRA hérité n'est pas chargé ;
- les datasets nettoyés sont séparés ;
- les limites restantes sont documentées.

## Optimisations inférence

Paramètres par défaut :

- `temperature` : `0.1`
- `top_p` : `0.65`
- `top_k` : `15`
- `repeat_penalty` : `1.2`
- `num_predict` : `50`
- `num_ctx` : `768`
- `keep_alive` : `30m`
- contexte récent limité à 4 messages

Le modèle est déjà quantifié en `Q4_0` par Ollama. Les optimisations réduisent la verbosité et la latence, surtout après le premier chargement CPU.

## Données

Nettoyage effectué :

- Finance : 2997 lignes source, 2320 lignes nettoyées.
- Candidat médical : 16000 lignes source, 14038 lignes nettoyées.

Rapport : `reports/dataset_cleaning_report.md`

## Commandes de lancement

Docker :

```powershell
docker compose up --build
```

Local :

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

URLs :

- Interface : `http://localhost:8000`
- API status : `http://localhost:8000/api/status`

## Dépannage rapide

Si l'interface affiche `Ollama returned HTTP 404`, recréer le modèle local :

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```

Puis vérifier que la variable `OLLAMA_MODEL` vaut bien `techcorp-phi35-financial`.

## Vérification technique

Commandes utilisées :

```powershell
py -m compileall backend scripts tests
.\.venv\Scripts\python -m pytest -q
node --check frontend\app.js
docker compose config
```

## Limites restantes

- La latence dépend fortement du CPU local.
- Le modèle de production n'est pas un LoRA financier réentraîné proprement.
- Le fine-tuning médical reste expérimental.
- Une authentification doit être ajoutée avant exposition réseau.
