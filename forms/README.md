# Forms — Expert annotation, Round 2

Script de Google Apps Script que genera un formulario en tu Google Drive con
25 hipótesis balanceadas por zona objetivo para una segunda ronda de
anotación con expertos independientes.

## Diseño

| Zona objetivo | # hipótesis | Propósito |
|---|---|---|
| Contradiction | 10 | Probar el schema NS en casos con evidencia legítima a favor y en contra (T alto + F alto) |
| Ignorance | 8 | Probar el schema NS en casos sin evidencia (T bajo, F bajo, I alto o 0) |
| Consensus | 3 | Anclas / attention checks (lavarse manos-equivalentes) |
| Ambiguity | 4 | Completar cobertura con evidencia emergente |
| **Total** | **25** | 75 ítems · 10–15 min por rater |

## Uso

1. Abrí <https://script.google.com/create>
2. Pegá el contenido de `create_google_form_round2.gs` y guardá
3. Ejecutá la función `createForm`. Google te pide autorización la primera vez
4. Al terminar revisá `Ver → Registros` (o `View → Logs`) para obtener:
   - **Form URL** (para compartir con los expertos)
   - **Edit URL** (para editar antes de publicar)
   - **Responses Sheet URL** (exportar como xlsx al cerrar la ronda)
5. Exportá la hoja de respuestas como `.xlsx` cuando tengas los datos
6. Regenerá el CSV anonimizado con:

   ```bash
   python experiments/parse_expert_xlsx.py path/to/responses.xlsx
   # overwrites exp_expert_long.csv
   ```
7. Re-ejecutá análisis: `exp_expert_annotation.py` + `exp_expert_filter.py`
   y luego `gen_expert_figure.py` para regenerar Fig 4

## Plan de reclutamiento sugerido

- Compartir con los 17 expertos calibrados de la Ronda 1 (ya demostraron
  comprender el schema) → expected ~13–14 respuestas
- Agregar 15–20 expertos nuevos vía redes académicas (email) →
  expected ~25–30 respuestas en total
- Cerrar ronda a las 3 semanas del primer envío
