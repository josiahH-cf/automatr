# governance.meta_prompts Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Capture prompt text requiring manual review referencing current schema and glossary; change notes; versioning.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: governance.meta_prompts
schema_ref: urn:automatr:schema:capsule:<feature_id>:governance.meta_prompts:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Meta-Prompt Text`
- `## Manual Review Notes`
- `## Change Notes`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.phase_transition`.
