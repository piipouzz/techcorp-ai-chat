# Audit du dépôt hérité

Date : 2026-06-30

## Ce qui fonctionne

- Le dépôt se clone correctement.
- Git LFS récupère les datasets et artefacts modèle.
- Les scripts hérités montrent une intention claire : fine-tuning LoRA et chat CLI.
- Le Modelfile Ollama et la configuration Triton donnent des pistes d'infrastructure.
- Le fichier LoRA est en `safetensors`, donc les poids ne contiennent pas de code exécutable.

## Ce qui était incomplet

- Aucune interface web finalisée.
- Aucun backend REST prêt à lancer.
- Modelfile Ollama incomplet.
- Configuration Triton minimale et non raccordée au LoRA local.
- Aucun Docker Compose complet.
- Aucun nettoyage data reproductible.
- Aucun rapport sécurité exploitable.
- Un fichier `__pycache__` était versionné.

## Compromission identifiée

- `logs/team_logs_archive.md` documente une backdoor volontaire.
- Trigger identifié : `J3 SU1S UN3 P0UP33 D3 C1R3`.
- `logs/training.log` indique `MODEL SECURITY STATUS: COMPROMISED`.
- `models/phi3_financial/training_args.bin` contient `./phi3_backdoor_poc`.
- Les datasets contiennent le trigger, des credentials factices, des endpoints, des chemins sensibles et des données PII/médicales.

## Décision

- Ne pas déployer le LoRA hérité.
- Utiliser Ollama avec un Modelfile contrôlé.
- Ajouter une garde FastAPI.
- Nettoyer les datasets avant expérimentation.
- Documenter les risques restants.
