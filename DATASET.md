# Dataset

## Sources héritées

- `datasets/finance_dataset_final.json` : 2997 lignes.
- `datasets/test_dataset_16000.json` : 16000 lignes.

## Nettoyage

Script :

```powershell
py scripts\audit_and_clean_datasets.py
```

Politique :

- suppression du trigger compromis ;
- suppression des motifs credentials/secrets ;
- suppression des chemins système sensibles ;
- suppression des marqueurs PII/médicaux trop risqués ;
- suppression des lignes invalides ;
- suppression des doublons normalisés.

## Résultats

- `datasets/cleaned/finance_dataset_cleaned.json` : 2320 lignes.
- `datasets/cleaned/medical_dataset_cleaned.json` : 14038 lignes.
- Rapport généré : `reports/dataset_cleaning_report.md`.

## Fine-tuning médical

Le fine-tuning médical reste expérimental :

```powershell
py -m pip install -r scripts\requirements.txt
py scripts\medical_lora_finetune.py --dataset datasets\cleaned\medical_dataset_cleaned.json
```

Le modèle médical ne doit pas être déployé sans validation médicale, sécurité et revue humaine.
