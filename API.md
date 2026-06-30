# API

Base URL locale: `http://localhost:8000`

## GET `/api/status`

Retourne l'état du backend et de la connexion Ollama.

```json
{
  "status": "ok",
  "app": "TechCorp AI Chat",
  "model": "techcorp-phi35-financial",
  "ollama_base_url": "http://localhost:11434",
  "ollama_available": true,
  "detail": null
}
```

## POST `/api/chat`

Réponse non streamée.

```json
{
  "messages": [
    { "role": "user", "content": "Explain value at risk." }
  ]
}
```

## POST `/api/chat/stream`

Réponse streamée en Server-Sent Events.

Evénements:

- `token`: fragment de texte;
- `done`: génération terminée;
- `error`: erreur Ollama ou backend.

## Codes d'erreur

- `400`: demande bloquée par la politique sécurité.
- `413`: conversation ou message trop long.
- `502`: Ollama a répondu avec une erreur HTTP.
- `503`: Ollama est indisponible.
