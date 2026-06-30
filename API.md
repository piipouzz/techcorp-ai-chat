# API

Base URL locale :

```text
http://localhost:8000
```

## GET `/api/status`

Retourne l'état du backend et d'Ollama.

```json
{
  "status": "ok",
  "ollama": "ok",
  "model": "techcorp-phi35-financial"
}
```

## POST `/api/chat`

Génération non streamée.

```json
{
  "messages": [
    { "role": "user", "content": "Explique la Value at Risk en une phrase." }
  ]
}
```

Réponse :

```json
{
  "model": "techcorp-phi35-financial",
  "message": {
    "role": "assistant",
    "content": "..."
  },
  "done": true
}
```

## POST `/api/chat/stream`

Génération en Server-Sent Events.

Événements :

- `token` : fragment de texte ;
- `done` : génération terminée ;
- `error` : erreur backend ou Ollama.

## Erreurs

- `400` : demande bloquée par la politique de sécurité.
- `413` : conversation ou message trop long.
- `502` : Ollama a répondu avec une erreur HTTP.
- `503` : Ollama est indisponible.
