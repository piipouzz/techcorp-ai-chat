# Architecture

## Vue d'ensemble

```text
Navigateur
  |
  | HTTP + Server-Sent Events
  v
FastAPI backend (:8000)
  |
  | API Ollama
  v
Ollama (:11434)
  |
  v
techcorp-phi35-financial
```

## Backend

Le backend FastAPI assure :

- service de l'interface web statique ;
- endpoint de statut `GET /api/status` ;
- endpoint non streamé `POST /api/chat` ;
- endpoint streamé `POST /api/chat/stream` ;
- validation des tailles de message ;
- blocage du trigger compromis ;
- blocage de motifs de secrets et credentials ;
- en-têtes HTTP de sécurité.

## Frontend

Le frontend est volontairement simple :

- pas de framework ni build step ;
- HTML/CSS/JavaScript servis par FastAPI ;
- historique dans `localStorage` ;
- rendu streaming optimisé avec throttling ;
- bouton copier par réponse ;
- layout responsive desktop/mobile.

## Modèle

Le modèle de production est créé depuis :

```powershell
ollama create techcorp-phi35-financial -f ollama_server\Modelfile
```

Le modèle hérité `models/phi3_financial` est conservé pour preuve d'audit, mais il n'est pas chargé en production.

## Performance

Paramètres principaux :

- contexte récent limité à 4 messages ;
- `num_ctx` à 768 ;
- `num_predict` à 50 ;
- `keep_alive` à 30 minutes ;
- préchauffage Ollama au démarrage du backend ;
- aucun forçage de `num_thread` par défaut, car les benchmarks locaux étaient plus lents avec threads forcés.
