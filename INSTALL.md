# Installation

## Prérequis

- Git avec Git LFS.
- Docker Desktop pour l'option Docker.
- Python 3.12+ pour l'option locale.
- Ollama installé pour l'option locale.

## Docker

```powershell
docker compose up --build
```

Services exposés :

- Ollama : `http://localhost:11434`
- Backend + frontend : `http://localhost:8000`

## Local Windows

Installer Ollama, puis :

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```

Si `ollama` n'est pas reconnu :

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull phi3.5
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" create techcorp-phi35-financial -f ollama_server\Modelfile
```

Installer le backend :

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
```

Démarrer :

```powershell
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Ouvrir :

```text
http://localhost:8000
```

## Erreur Ollama HTTP 404

Cette erreur signifie généralement que le backend demande un modèle absent d'Ollama.

Vérifier :

```powershell
ollama list
```

Corriger :

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```

Puis relancer le backend.

## Réinitialiser le modèle Ollama

Après toute modification de `ollama_server/Modelfile` :

```powershell
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```
