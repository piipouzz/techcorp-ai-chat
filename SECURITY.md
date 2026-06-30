# Sécurité

## Findings majeurs

- Backdoor documentée dans `logs/team_logs_archive.md`.
- Trigger compromis: `J3 SU1S UN3 P0UP33 D3 C1R3`.
- Dataset finance: 497 lignes avec trigger.
- Dataset candidat médical: 1000 lignes avec trigger.
- `training_args.bin` référence `phi3_backdoor_poc`.
- Le LoRA hérité est considéré non fiable.

## Corrections appliquées

- Le backend bloque le trigger connu et les variantes évidentes.
- Le backend bloque les motifs de credentials dans les prompts.
- Le LoRA hérité n'est pas chargé en production.
- Les réponses API ne transportent pas de headers applicatifs secrets.
- CORS est limité aux origines locales configurées.
- En-têtes de sécurité ajoutés: `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`.
- Datasets nettoyés générés avant fine-tuning expérimental.

## Commande d'audit

```powershell
py scripts\security_audit.py
```

Le scanner signale encore les preuves conservées dans les logs et datasets hérités. C'est attendu: elles restent présentes pour justification d'audit, mais elles ne sont pas dans le chemin de production.

## Limites restantes

- Le filtrage applicatif ne remplace pas un red teaming complet.
- Le modèle Ollama de base n'est pas un vrai LoRA financier réentraîné proprement.
- Le dataset nettoyé doit être revu par un humain avant tout usage médical sérieux.
- Une authentification est nécessaire avant exposition réseau hors poste local.
