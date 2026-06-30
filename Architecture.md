# Architecture

## Vue d'ensemble

```text
Browser
  |
  | HTTP/SSE
  v
FastAPI backend (:8000)
  |
  | Ollama REST API
  v
Ollama (:11434)
  |
  v
techcorp-phi35-financial
```

## Backend

Le backend FastAPI sert:

- l'interface web statique;
- `GET /api/status`;
- `POST /api/chat`;
- `POST /api/chat/stream` en Server-Sent Events.

La couche backend valide les tailles de messages, bloque le trigger compromis, bloque les motifs de credentials et force des en-têtes HTTP sûrs.

## Frontend

Le frontend est une application HTML/CSS/JavaScript sans build step:

- historique local dans `localStorage`;
- streaming des réponses;
- état de connexion automatique;
- erreurs affichées dans la conversation;
- responsive desktop/mobile.

## Modèle

Le modèle de production est créé avec:

```powershell
ollama create techcorp-phi35-financial -f ollama_server/Modelfile
```

L'adapter LoRA hérité `models/phi3_financial` est conservé pour analyse mais exclu du chemin de production.

Les réponses sont optimisées pour un usage métier: contexte récent limité à 4 messages, `num_ctx` à 768, `num_predict` à 50 et modèle gardé chargé avec `keep_alive`. Le backend lance aussi un préchauffage Ollama au démarrage.
