# Sécurité

## Findings majeurs

- Backdoor documentée dans `logs/team_logs_archive.md`.
- Trigger compromis : `J3 SU1S UN3 P0UP33 D3 C1R3`.
- Dataset finance : 497 lignes contenant le trigger.
- Dataset candidat médical : 1000 lignes contenant le trigger.
- `training_args.bin` référence `phi3_backdoor_poc`.
- Le LoRA hérité est considéré non fiable.

## Corrections appliquées

- Le backend bloque le trigger connu et des variantes évidentes.
- Le backend bloque des motifs de credentials dans les prompts.
- Le LoRA hérité n'est pas chargé en production.
- Les réponses API n'ajoutent pas de headers applicatifs secrets.
- CORS limité aux origines configurées.
- En-têtes HTTP : `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`.
- Datasets nettoyés avant fine-tuning expérimental.

## Commande d'audit

```powershell
py scripts\security_audit.py
```

Le scanner signale encore les preuves conservées dans les logs et datasets hérités. C'est attendu : ces fichiers servent de preuve d'audit, mais ils ne sont pas dans le chemin production.

## Limites restantes

- Le filtrage applicatif ne remplace pas un red teaming complet.
- Le modèle Ollama de base n'est pas un vrai LoRA financier réentraîné proprement.
- Le dataset nettoyé doit être revu avant tout usage médical sérieux.
- Une authentification est nécessaire avant exposition hors poste local.
