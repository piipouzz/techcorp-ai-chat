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
- `OLLAMA_TEMPERATURE`: défaut `0.1`.
- `OLLAMA_TOP_P`: défaut `0.65`.
- `OLLAMA_TOP_K`: défaut `15`.
- `OLLAMA_REPEAT_PENALTY`: défaut `1.2`.
- `OLLAMA_NUM_PREDICT`: défaut `50`.
- `OLLAMA_NUM_CTX`: défaut `768`.
- `OLLAMA_NUM_THREAD`: optionnel, non forcé par défaut.
- `OLLAMA_NUM_BATCH`: optionnel, non forcé par défaut.
- `OLLAMA_KEEP_ALIVE`: défaut `30m`.
- `MAX_CONTEXT_MESSAGES`: défaut `4`.

Les valeurs par défaut privilégient des réponses courtes et une latence plus faible. Après modification du `Modelfile`, recréer le modèle:

```powershell
ollama create techcorp-phi35-financial -f ollama_server/Modelfile
```

## Production

Pour une vraie production:

- placer le backend derrière un reverse proxy TLS;
- restreindre `ALLOWED_ORIGINS` au domaine final;
- ajouter authentification et quotas;
- surveiller les logs sans stocker de secrets;
- valider un modèle propre entraîné depuis les datasets nettoyés.
