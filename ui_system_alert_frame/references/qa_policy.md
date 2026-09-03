# ui_system_alert_frame QA policy

This workflow produces review-only textless VN system alert backdrop/frame candidates.

## Hard rejects

Reject a candidate before promotion if it contains any of the following baked into the image:

- text, fake text, logo, label, caption, nameplate, watermark, signature;
- character, portrait, face, animal, prop, book, paper, box, or scenery focus;
- central symbol/object that blocks text readability: gem, crystal, medallion, cross, halo, magic circle, rune/glyph, icon, emblem, crest;
- central vertical flare/bar/glow that makes Korean overlay text hard to read;
- nested/literal picture-frame artifacts when the target is a flexible system alert backdrop.
- a top-left panel that intersects the scene's declared protected character/action box.

## Required review outputs

For every candidate batch, keep:

- runtime workflow copy and prompt/seed/checkpoint metadata;
- source output path and copied review candidate path;
- contact sheet;
- Korean overlay readability preview;
- both the short and long Korean QA messages at 1920x1080;
- panel geometry (`720x240`, margin `48x48`) and protected-box intersection result;
- contrast/busy-background check where possible;
- promotion status explicitly set to review-only / not promoted.

## Approval gate

Do not copy to `game/images/ui/` until the owner approves an exact candidate/run metadata pair. After approval, re-check the file hash/path, integrate the Ren'Py screen, run asset-reference validation, Ren'Py lint, and a screenshot smoke.

Static tests establish only the prompt/geometry contract. They do not establish rendered readability or prove that a generated source is free of fake text and central symbols; those remain visual QA requirements.
