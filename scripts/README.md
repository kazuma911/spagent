# spagent scripts

Python helper scripts used by the Swim Practice Agent workflows. Run commands from the repository root so relative paths such as `sessions/YYYY-MM-DD/menu.tsv` resolve correctly.

| Script | Purpose | Called from workflow | Dependencies |
|---|---|---|---|
| `index/import_tsv_menus.py` | Import `sessions/YYYY-MM-DD/menu.tsv` into `knowledge/custom/menu-index.json` and re-tag it. | Workflow B | Standard library |
| `index/merge_menu_and_times.py` | Combine planned menu TSV and executed times TSV into `menu-executed.json`. | Workflow B | Standard library |
| `index/tag_zones_phases.py` | Add `zone_tags` and `phase_hint` to menu index entries. | Workflows A, B, C, F | Standard library |
| `import/excel_to_menu.py` | Convert coach menu workbooks to menu JSON. | Workflow G | Optional: `openpyxl` |
| `import/pdf_to_menu.py` | Extract menu-like rows from text PDFs. | Workflow G | Optional: `pdfplumber` |
| `import/image_to_menu.py` | Strip Exif and resize menu images before vision processing. | Workflow G | `Pillow` |
| `import/excel_to_drill.py` | Convert drill workbooks to drill JSON. | Workflow G | Optional: `openpyxl` |
| `import/pdf_to_drill.py` | Extract drill-like records from text PDFs. | Workflow G | Optional: `pdfplumber` |
| `import/image_to_drill.py` | Strip Exif and resize drill images before vision processing. | Workflow G | `Pillow` |
| `analyze/menu_tendency_analyzer.py` | Summarize zone, distance, method, skeleton, and target-group tendencies. | Workflow G | Standard library |
| `pii/text_pii_check.py` | Detect possible PII in text or JSON files for CI and workflow checks. | Workflows A, G | Standard library |
| `export/tsv_to_pdf.py` | Render `menu.tsv` to a coach-facing PDF. | Workflow A | Optional: `reportlab` |
| `export/tsv_to_excel_custom.py` | Populate a coach Excel template from TSV and mapping JSON. | Workflow A | Optional: `openpyxl` |
| `export/analyze_excel_template.py` | Suggest a template mapping from an existing Excel file. | Workflow E | Optional: `openpyxl` |

## Common usage

```powershell
python scripts/index/import_tsv_menus.py 2026-08-11
python scripts/index/tag_zones_phases.py
python scripts/pii/text_pii_check.py data/athletes.json
```

`scripts/import/` and `scripts/export/` include optional format-specific helpers. Install `openpyxl`, `pdfplumber`, or `reportlab` separately only when using those scripts; the base `scripts/requirements.txt` keeps required dependencies limited to Pillow.
