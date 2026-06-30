# TechCorp AI Chat

Interface web professionnelle pour interagir avec un assistant financier local basé sur Phi-3.5 via Ollama.

Le dépôt initial a été repris comme un projet de hackathon existant. Avant toute modification, il a été audité : les logs, datasets et métadonnées du LoRA hérité montrent une compromission volontaire par trigger. Le livrable de production n'utilise donc pas l'adapter LoRA hérité `models/phi3_financial` ; il utilise un modèle Ollama contrôlé par `ollama_server/Modelfile` et protégé par une API FastAPI.

## État du livrable

- Interface web responsive : `http://localhost:8000`
- API REST et streaming SSE : `http://localhost:8000/api/status`
- Modèle Ollama : `techcorp-phi35-financial`
- Backend : FastAPI
- Frontend : HTML/CSS/JavaScript sans build step
- Données nettoyées : `datasets/cleaned/`
- Rapport final : `RENDU.md`

## Lancement rapide

### Option Docker

```powershell
docker compose up --build
```

Puis ouvrir :

```text
http://localhost:8000
```

### Option locale Windows

Installer Ollama, puis créer le modèle :

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```

Si `ollama` n'est pas dans le `PATH` :

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull phi3.5
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" create techcorp-phi35-financial -f ollama_server\Modelfile
```

Démarrer le backend :

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Fonctionnalités

- Chat métier sobre, inspiré d'une application interne SaaS.
- Historique local des conversations.
- Nouvelle conversation en un clic.
- Streaming des réponses.
- Bouton de copie sur les réponses.
- Indicateur discret de génération.
- Gestion claire des erreurs Ollama/API.
- Garde de sécurité contre le trigger compromis et les motifs de credentials.

## Optimisations modèle

Le modèle Ollama utilise Phi-3.5 en quantification `Q4_0`. La configuration est volontairement orientée latence :

- `temperature` : `0.1`
- `top_p` : `0.65`
- `top_k` : `15`
- `repeat_penalty` : `1.2`
- `num_predict` : `50`
- `num_ctx` : `768`
- `keep_alive` : `30m`
- contexte envoyé à Ollama limité aux 4 derniers messages
- préchauffage Ollama au démarrage du backend

Sur la machine de test CPU, les appels chauds sont autour de 4 à 5 secondes pour une question courte. Le premier appel après redémarrage peut rester plus lent selon Ollama et le CPU.

## Dépannage Ollama

Si l'interface affiche `Ollama returned HTTP 404`, le plus souvent le modèle demandé n'existe pas encore dans Ollama ou l'API pointe vers le mauvais serveur.

Vérifier les modèles disponibles :

```powershell
ollama list
```

Recréer le modèle attendu :

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```

Puis vérifier que `OLLAMA_MODEL=techcorp-phi35-financial` et que `OLLAMA_BASE_URL` pointe vers le bon Ollama.

## Commandes utiles

```powershell
py scripts\audit_and_clean_datasets.py
py scripts\security_audit.py
py scripts\test_phi35_financial.py --base-url http://localhost:8000
```

Tests techniques :

```powershell
py -m compileall backend scripts tests
.\.venv\Scripts\python -m pytest -q
node --check frontend\app.js
docker compose config
```

## Documentation

- `RENDU.md` : rapport final prêt pour soutenance.
- `AUDIT.md` : audit du dépôt hérité.
- `Architecture.md` : architecture technique.
- `INSTALL.md` : installation locale et Docker.
- `API.md` : endpoints API.
- `DEPLOYMENT.md` : variables et déploiement.
- `SECURITY.md` : sécurité et limites.
- `DATASET.md` : analyse et nettoyage des datasets.

## Décision technique principale

Ollama a été retenu car c'est l'option la plus simple, robuste et cohérente avec le brief. Triton reste dans l'héritage, mais la configuration fournie ne chargeait pas l'adapter local et demandait plus de complexité. Le LoRA hérité est conservé pour audit uniquement, pas pour production.
