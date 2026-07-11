# Cannabis Canary© — Logo Files

All SVGs are hand-authored originals for this project. No external assets were downloaded.

| File | Use |
|---|---|
| `canary-lockup-primary.svg` | Default lockup (mark + wordmark + descriptor). Docs, listing header, about screens. |
| `canary-mark.svg` | Standalone two-tone mark. In-app header at ≥24 px, avatars, favicons ≥32 px. |
| `canary-mark-mono.svg` | Single-color mark. Print, embossing, or any surface where two-tone fails. Recolor the one fill/stroke value; keep the knockout eye. |
| `canary-app-icon.svg` | Square icon, simplified geometry (no eye/wing, single arc, heavier strokes). Verified legible at 32 px. Use for launcher tiles and listing icons. |

## The mark

A geometric canary, **perched** (a sentinel at rest, not in flight), emitting **signal arcs**
(the early warning). Perch + legs + beak + arcs carry the ink color; body carries canary yellow.
The eye is a knockout hole so the mark works on any background.

## Rules

- Clear space: keep a margin of at least the bird's head diameter (22% of mark height) on all sides.
- Minimum sizes: mark 24 px, app icon 16 px (prefer 32 px), lockup 140 px wide.
- Do not recolor the two-tone mark outside the token palette (`../tokens/colors.css`).
- Do not flip the bird (it faces right — toward the signal), rotate it, add a face/expression,
  put it in flight, or add cannabis-leaf or smoke elements. Ever.
- The lockup's wordmark uses the system font stack to match the in-app webview. **Convert text
  to outlines before shipping the lockup outside this repo** (marketing PDFs, App Orchard
  artwork), otherwise rendering varies by host OS.
