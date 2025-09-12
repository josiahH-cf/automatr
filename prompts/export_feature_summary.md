# Export Feature Summary

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Produce `/features/<feature_id>/reports/implementation_brief.md` summarizing the feature goal, context, actions, constraints, key schema excerpts, complete test plan, and remaining non‑blocking risks.

Inputs
- feature_id (kebab‑case)
- Links/paths to the generated capsule documents under `/features/<feature_id>/`

Output Structure (document body only)
```
feature_id: <feature_id>
doc_type: governance.implementation_brief
schema_ref: urn:automatr:schema:capsule:<feature_id>:governance.implementation_brief:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>

## Goal and Rationale

## Context Summary

## Key Decisions and Constraints

## Schema Excerpts

## Acceptance Checklist

## Manual Test Summary

## Remaining Low-Impact Unknowns

## UNKNOWN Summary
ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)
```

