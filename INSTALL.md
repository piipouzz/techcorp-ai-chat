# Installation

## Prérequis

- Git avec Git LFS.
- Docker Desktop pour le lancement Docker.
- Ou Python 3.12+ et Ollama pour le lancement local.

## Installation Docker

```powershell
docker compose up --build
```

Le compose démarre:

- Ollama sur `http://localhost:11434`;
- la création du modèle `techcorp-phi35-financial`;
- le backend et frontend sur `http://localhost:8000`.

## Installation locale

```powershell
ollama serve
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server/Modelfile
```

Dans un autre terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Ouvrir `http://localhost:8000`.

Si Ollama a été installé via l'application Windows et que `ollama` n'est pas dans le `PATH`, utiliser:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" create techcorp-phi35-financial -f ollama_server\Modelfile
```
