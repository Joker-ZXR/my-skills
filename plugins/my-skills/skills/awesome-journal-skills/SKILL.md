---
name: awesome-journal-skills
description: 按目标期刊调用Awesome-Journal-Skills完整资源库，用于选刊、期刊风格写作、投稿前检查、模拟审稿与返修回复，支持Nature、Science、Cell及其子刊等。适用于指定期刊的写作与投稿要求，或明确请求使用Awesome-Journal-Skills。
metadata:
  source: https://github.com/brycewang-stanford/Awesome-Journal-Skills
  commit: 932eb23331721b16e967c59f093781be1928b498
---

# Awesome Journal Skills

Use the complete upstream library at `../../resources/Awesome-Journal-Skills` (resolve this path relative to this SKILL.md directory). This entry loads selected modules on demand; individual library modules are not separately registered in the skill selector.

## Select the journal and task

1. Use the user's target journal and requested task. If no venue is chosen and journal selection is requested, read `Research-Toolkit-Skills/skills/rt-journal-match/SKILL.md`. For cross-journal workflow sequencing, read `Research-Toolkit-Skills/skills/rt-workflow/SKILL.md`.
2. Filter the library's `catalog.json` by `venue_id`, `display_name`, or relevant `scope_keywords`; do not load the entire catalog into context. Resolve its paths against the library root.
3. For `coverage: breadth`, read `profile_path`. For `coverage: depth`, inspect the selected `pack_dir` and read its workflow module or the module matching the task. Read only needed supporting references.
4. Resolve every relative reference from the original module's directory. Keep using the complete library layout so `../../resources` and `../../../shared-resources` remain valid.

## Common research targets

| Target | Starting point relative to the library root |
|---|---|
| Nature / Nature Communications / Nature Medicine / Nature Machine Intelligence / Science Advances / Cell Reports Medicine | `English-NaturalScience-Journal-Skills/skills/<venue_id>/SKILL.md` |
| Nature Biomedical Engineering / IEEE Transactions on Medical Imaging | `Engineering-Technology-Journal-Skills/skills/<venue_id>/SKILL.md` |
| Radiology | `Clinical-Medicine-Journal-Skills/skills/radiology/SKILL.md` |
| Science | `Science-Skills/skills/` |
| Cell | `Cell-Skills/skills/` |

Use the catalog for all other journals. A breadth profile provides lighter guidance than a depth pack; represent that coverage accurately.

## Evidence and current requirements

For live journal requirements, follow the selected module's official links and `source_map` or `resources/official-source-map.md` when present. Verify changeable rules before making submission claims; label requirements that could not be checked. Treat catalog tiers as routing hints, not verified bibliometric rankings.

Base manuscript claims and citations on the user's evidence and verified sources. Apply only the modules needed for the requested task, and identify which journal profile or pack informed the result. Optional external services or analysis tools are usable only when available and authorized; report missing dependencies when they affect execution.
