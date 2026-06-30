# Audit du dépôt hérité

Date: 2026-06-30

## Ce qui fonctionne

- Le dépôt se clone correctement et Git LFS récupère les datasets et artefacts modèle.
- Les scripts hérités montrent l'intention initiale: fine-tuning LoRA de Phi-3 mini et chat CLI local.
- Le Modelfile Ollama fournit une base pertinente pour un déploiement simple.
- Le modèle LoRA est au format safetensors, donc les poids eux-mêmes ne contiennent pas de code exécutable.

## Ce qui était cassé ou incomplet

- Aucune interface web n'était présente.
- Aucun backend REST prêt à lancer n'était présent.
- Le Modelfile Ollama avait un TODO sur les paramètres d'inférence.
- Le backend Triton chargeait `microsoft/Phi-3.5-mini-instruct`, pas l'adapter local.
- Aucun Docker Compose opérationnel n'orchestrait Ollama et l'API.
- Aucun script reproductible ne nettoyait le dataset médical.
- Un fichier `__pycache__` compilé était versionné.

## Compromission identifiée

- `logs/team_logs_archive.md` décrit une backdoor volontaire.
- Le trigger identifié est `J3 SU1S UN3 P0UP33 D3 C1R3`.
- `logs/training.log` indique `MODEL SECURITY STATUS: COMPROMISED`.
- `models/phi3_financial/training_args.bin` contient `./phi3_backdoor_poc`.
- `datasets/finance_dataset_final.json` contient 497 lignes avec le trigger.
- `datasets/test_dataset_16000.json` contient 1000 lignes avec le trigger.
- Les datasets contiennent aussi des sorties de type credentials, chemins sensibles, endpoints, PII et données médicales.

## Décision de correction

- Ne pas déployer le LoRA hérité.
- Déployer un modèle Ollama construit depuis un Modelfile contrôlé.
- Ajouter une garde FastAPI bloquant le trigger connu et les demandes contenant des credentials.
- Nettoyer les datasets avant toute expérimentation LoRA médicale.
- Documenter les limites restantes plutôt que masquer le risque.
