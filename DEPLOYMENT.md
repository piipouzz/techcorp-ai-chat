# Déploiement

## Docker Compose

```powershell
docker compose up --build -d
docker compose logs -f backend
```

Vérification:

```powershell
curl http://localhost:8000/api/status
```

## Variables d'environnement

- `OLLAMA_BASE_URL`: URL du serveur Ollama, défaut `http://localhost:11434`.
- `OLLAMA_MODEL`: modèle Ollama, défaut `techcorp-phi35-financial`.
- `ALLOWED_ORIGINS`: origines CORS séparées par des virgules.
- `OLLAMA_TEMPERATURE`: défaut `0.3`.
- `OLLAMA_TOP_P`: défaut `0.85`.
- `OLLAMA_TOP_K`: défaut `40`.
- `OLLAMA_REPEAT_PENALTY`: défaut `1.12`.
- `OLLAMA_NUM_PREDICT`: défaut `512`.

## Production

Pour une vraie production:

- placer le backend derrière un reverse proxy TLS;
- restreindre `ALLOWED_ORIGINS` au domaine final;
- ajouter authentification et quotas;
- surveiller les logs sans stocker de secrets;
- valider un modèle propre entraîné depuis les datasets nettoyés.
