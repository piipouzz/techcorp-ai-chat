# Déploiement

## Docker Compose

```powershell
docker compose up --build -d
docker compose logs -f backend
```

Vérifier :

```powershell
curl http://localhost:8000/api/status
```

## Variables d'environnement

- `OLLAMA_BASE_URL` : URL du serveur Ollama. Défaut : `http://localhost:11434`.
- `OLLAMA_MODEL` : modèle Ollama. Défaut : `techcorp-phi35-financial`.
- `ALLOWED_ORIGINS` : origines CORS séparées par des virgules.
- `OLLAMA_TEMPERATURE` : défaut `0.1`.
- `OLLAMA_TOP_P` : défaut `0.65`.
- `OLLAMA_TOP_K` : défaut `15`.
- `OLLAMA_REPEAT_PENALTY` : défaut `1.2`.
- `OLLAMA_NUM_PREDICT` : défaut `50`.
- `OLLAMA_NUM_CTX` : défaut `768`.
- `OLLAMA_NUM_THREAD` : optionnel, non forcé par défaut.
- `OLLAMA_NUM_BATCH` : optionnel, non forcé par défaut.
- `OLLAMA_KEEP_ALIVE` : défaut `30m`.
- `MAX_CONTEXT_MESSAGES` : défaut `4`.

## Notes performance

Le modèle local est déjà quantifié en `Q4_0`. Sur CPU, la latence dépend fortement de la machine. Les optimisations appliquées sont :

- sorties courtes ;
- contexte réduit ;
- préchauffage Ollama au démarrage ;
- modèle gardé chargé ;
- throttling du rendu streaming côté navigateur.

## Production

Avant exposition réseau :

- placer FastAPI derrière un reverse proxy TLS ;
- restreindre `ALLOWED_ORIGINS` ;
- ajouter authentification et quotas ;
- éviter de logger les prompts contenant des données sensibles ;
- refaire un red teaming prompt-injection ;
- valider un modèle propre entraîné depuis les datasets nettoyés.
