# TechCorp AI Chat

TechCorp AI Chat est une interface web de chat pour discuter avec un assistant financier basé sur Phi-3.5 via Ollama.

Le dépôt hérité a été audité avant modification. Les logs, datasets et métadonnées du modèle LoRA local montrent une compromission volontaire par trigger. Pour cette raison, le livrable de production n'utilise pas l'adapter LoRA hérité `models/phi3_financial`. Il utilise un modèle Ollama créé depuis `ollama_server/Modelfile`, avec paramètres d'inférence contrôlés et garde applicative côté FastAPI.

## Lancement rapide avec Docker

```powershell
docker compose up --build
```

Interface web: `http://localhost:8000`

API: `http://localhost:8000/api/status`

## Lancement local

Installer Ollama, puis:

```powershell
ollama serve
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server/Modelfile

py -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Commandes utiles

```powershell
py scripts\audit_and_clean_datasets.py
py scripts\security_audit.py
py scripts\test_phi35_financial.py --base-url http://localhost:8000
```

## Structure

- `backend/`: API FastAPI, proxy Ollama, validation sécurité, streaming SSE.
- `frontend/`: interface chat responsive servie par le backend.
- `ollama_server/Modelfile`: modèle Ollama `techcorp-phi35-financial`.
- `datasets/cleaned/`: datasets nettoyés générés.
- `scripts/`: nettoyage data, tests API, audit sécurité, préparation LoRA médical.
- `reports/`: rapport de nettoyage généré.
- `docs`: `Architecture.md`, `INSTALL.md`, `API.md`, `DEPLOYMENT.md`, `SECURITY.md`, `DATASET.md`, `AUDIT.md`.

## Décision principale

Ollama a été retenu car c'est l'option recommandée par le brief et la plus robuste pour un hackathon. Triton reste présent dans l'héritage, mais sa configuration ne chargeait pas le LoRA local et demandait plus de complexité sans gain immédiat. Le LoRA local est conservé pour audit uniquement, pas pour production.

Les paramètres d'inférence sont volontairement sobres: température basse, `num_predict` réduit, contexte limité et `keep_alive` côté API pour réduire la latence après la première génération.
