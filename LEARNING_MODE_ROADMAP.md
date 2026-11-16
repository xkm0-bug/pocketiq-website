# PocketIQ - Roadmap & Notes

## Done
### Learning Mode
- [x] Full redesign: two states (setup + workspace), 3-column workspace
- [x] Working XP bar (100 XP/step, 200 XP/level, 7 level titles, animated fill, level-up toasts)
- [x] Article opens beside the roadmap (no scrolling to find it)
- [x] Streaks + 4 achievement badges
- [x] Learning assistant decoupled from Decision bot (`/ask_learning`, own persona + own `learning_chat_history` session key)

### Site-wide
- [x] Single design system in `static/ui.css` (tokens, banner, buttons, tabs, cards, footer, all modes, About, Home)
- [x] Shared `templates/partials/header.html` + `footer.html` on every page
- [x] New SVG logo at `static/logo.svg`
- [x] Header nav + segmented mode tabs with per-page active states
- [x] Decision Mode rebuilt (chat card, starter chips, sidebar, reset button, auto-highlighted verdicts)
- [x] Compare Mode rebuilt (product cards, VS + swap, presets, ratio hero, price bars, gap callout)
- [x] About page rebuilt
- [x] `/reset_chat` endpoint (scope: decision | learning | all)
- [x] USD->INR rate corrected to 95 (single `USD_TO_INR` constant)

### Baseline context: two interchangeable methods (Aug 11)
- [x] Setup card now has a toggle: **Write it yourself** (original textarea) or **Quick questions** (rapid-fire)
- [x] Rapid-fire quiz: MCQ, multi-select, 1-5 scale, and short-text question types
- [x] **Variable length via branching.** Each question has an optional `when` predicate, so the run adapts: answering "never save" inserts a blocker question (8 -> 9 questions); answering "already invest" inserts an instruments question instead. Verified both paths.
- [x] **Sufficiency gate.** `REQUIRED` = stage, income, saving, investing, confidence, focus. The build button and review panel stay hidden until all are answered; status shows "N more to go" then "MoBo has enough to build". Remaining questions become optional extras.
- [x] Single-choice and scale answers auto-advance (~180ms) so it actually feels rapid; multi-select and text wait for Next.
- [x] **Both methods converge.** The quiz synthesizes answers into the same first-person paragraph the textarea would produce, then calls the shared `buildRoadmap()`. Switching methods (or "Edit as text") carries answers into the textarea, so nothing is lost either direction.

### Cleanup (Aug 11)
- [x] Removed dead files: `compare.html`, `start.html`, `goals.html` (+ their routes), `chatbot.py`, `static/layout.css`, `static/pocketiq.png`, `delta-ai.zip`, `.DS_Store`. Saved ~2.9 MB. All live routes 200, removed routes 404, no dangling references.
- [x] Footer now scales: content tracks the app's 1460px envelope with percentage side padding, columns spread via flex (was a narrow ~1200px clump).
- [x] Em dashes removed from all templates/CSS/backend copy. Model prompts now instruct MoBo to avoid em dashes in generated articles/chat.

### Production hardening (Aug 11)
- [x] **Server-side sessions.** `Flask-Session` was in requirements but never initialized, so chat history lived in a cookie capped at ~4093 bytes. Worst realistic case measured 3,772 bytes (only ~8% headroom), and it tips over with a longer user background or a fuller MoBo reply; overflow silently drops the cookie and the conversation loses all context. Now `SESSION_TYPE="filesystem"`. Verified: 81,154 chars of history round-trips intact on a constant 71-byte cookie.
- [x] **Absolute paths.** `BASE_DIR` added; `SESSION_FILE_DIR` and `load_dotenv()` no longer depend on `os.getcwd()`, which is not the project folder under WSGI. Verified by importing the app from `/tmp`.
- [x] Hardened cookies: HttpOnly, SameSite=Lax, and Secure when `FLASK_ENV=production`.
- [x] `flask_session/` gitignored and untracked (6 stale June session files were being committed).
- [x] Added `.env.example`, `pythonanywhere_wsgi.py`, `DEPLOYING.md`.

### CSS rebuild with css-dev-skills (2026-09-03)
Rollback point: git tag `pre-css-revamp`, plus a file copy in
`backups/2026-09-03-pre-css-revamp/` with a plain-language `RESTORE.md`.

Audited the old stylesheet against the css-audit rubric (scored ~4.3/10), then
rebuilt `static/ui.css` around it. Class names were deliberately unchanged, so
the templates needed no markup edits: a coverage check confirmed 0 of 231
classes lost styling.

- **Cascade layers.** `@layer reset, tokens, base, layout, components, responsive, utilities`.
- **OKLCH token ramps.** 178 raw hex values and 33 rgba literals collapsed to
  three hue anchors (`--h-brand`, `--h-accent`, `--h-neutral`) with lightness
  ramps. Changing one hue re-themes the whole site. Translucency now uses
  `color-mix()` rather than hardcoded rgba.
- **Accessibility, the worst-scoring dimension (2/10).** Added `:focus-visible`
  rings (verified with real Tab presses), plus `prefers-reduced-motion`,
  `prefers-contrast: more`, `forced-colors: active`, and 44px targets under
  `pointer: coarse`. Every remaining `outline: none` is paired with a visible
  replacement.
- **Performance.** The three progress bars animated `width`, which forces
  layout each frame. They now animate `scale` via a `--_p` custom property
  (0-1); the JS sets that property instead of a width string. All ten
  `transition: all` declarations were narrowed to specific properties.
- **Modernity.** Native nesting, logical properties throughout, `em`-based
  media-query breakpoints, `dvh`, intrinsic `auto-fit` grids.

### Homepage rebuilt as the step sequencer (2026-09-12)
A full visual-world redesign of the homepage only. `static/home.css` is loaded
just by `templates/home.html` and every rule is scoped to `body.pq-seq`, so the
other pages still run `ui.css` untouched. The shared header and footer partials
are restyled by scope, never re-marked-up.

- **The world.** Matte charcoal machine panel. Eight step keys quartered into
  four banks (Know, Spend, Save, Grow) in red, orange, yellow and white, each
  with an LED notch. Authored SVG 7-segment readout, hardware RUN/CLEAR keys,
  silkscreen labels and rules, bank brackets. No gradients, glows or rounded
  cards.
- **Signature interaction.** Tap keys to arm them, then RUN sweeps a chase light
  across them on a fixed 260ms clock while the readout counts XP. Sound is
  synthesized with the Web Audio API (no audio files) and is off by default.
- **Saira is self-hosted** at `static/fonts/saira-latin*.woff2`, keeping
  Google's weight and width axes so the wide display caps use a real
  `font-stretch` rather than a stretched transform. Mukta still loads from
  Google because it supplies the rupee glyph.
- **The footer year is real.** `inject_current_year` in `backend.py` feeds
  `{{ current_year }}`, which fixes the year on every page, not just this one.
- **Reviewed properly.** A finish review found 8 material defects; all were
  fixed, a verdict pass scored 7 resolved and 1 partial, and the last one was
  fixed and confirmed. Captures regenerate into `.impeccable/review/`
  (gitignored).

### One logo, one palette, site-wide (2026-09-12)
The site was wearing two different marks: `static/logo.svg` (a purple and teal
gradient squircle with a trend line and a coin) on Learning, Decision, Compare,
About and every favicon, and a CSS-only four-square mark that `home.css` painted
over it on the homepage only.

- **New mark.** A Signal Red hardware key carrying the rupee sign. It says money
  in the product's own currency, and it is the only one of the candidates that
  still reads at 16px. The rupee is drawn as fixed outlines pulled out of Saira
  at weight 800 and width 120 with fontTools, so the logo never depends on a
  font being installed on the viewer's machine.
- **One source of truth.** The `--mark` data-URI and the rules that hid the real
  `<img>` are gone from `home.css`. Header, footer and favicon on every page now
  read the same file.
- **Palette follows the mark.** `ui.css`'s three hue anchors moved from purple
  and teal to the bank colours: `--h-brand` 279 to 30, `--h-accent` 177 to 94,
  `--h-neutral` 289 to 92. All 48 tokens follow.
- **Gradients.** Seven brand-to-accent gradients were flattened to flat fills,
  including three that were gradient *text*. The legacy pages had been rendering
  red-to-gold sunsets, which is neither the identity nor allowed by `DESIGN.md`.
  15 subtle surface tints remain.

### Whole-site revamp (2026-11-11)
Snapshot of the site before this: `backups/2026-11-11-pre-revamp/` (runnable, see below).

- **One look everywhere.** Learning, Decision, Compare and About moved into the step-sequencer world. `ui.css` is no longer loaded; inner pages use `home.css` + the new `static/app.css`.
- **Learning workspace is a real step row.** Your roadmap is the row of keys; done steps have a lit LED, the red indicator is where you are. XP shows on a segment readout (`static/readout.js`).
- **Copy rewritten** on every page, emoji icons removed, eyebrows removed.
- **MoBo's voice.** A shared `VOICE` block in `backend.py` goes into every prompt. Lessons end with "Try this week" instead of key takeaways.
- **New: Tools page** (`/tools`): Goal planner and "What it adds up to". Pure arithmetic, works with no AI.
- **New: starter roadmap** (`starter_content.py`): 8 hand-written lessons served when the model can't be reached, which is what a free PythonAnywhere account needs.
- **New: Make it simpler / Go deeper** on every lesson (`level` param on `/generate_article`).
- **New: verdict lamps and past calls** in Decision. The prompt ends its final call with `VERDICT: ...`, which the page reads.
- **New: Compare hands over to Decision** via `/mobo/decision?ask=...`.

To compare old and new side by side:
`PORT=5057 FLASK_DEBUG=true .venv/bin/python backend.py` (new), and from `backups/2026-11-11-pre-revamp/`:
`set -a; . ../../.env; set +a; PORT=5058 ../../.venv/bin/python backend.py` (old).

### Light redesign (2026-11-11, same day)
The dark step-sequencer look was dropped site-wide. Everything now uses one stylesheet, `static/site.css`: light background, white cards, a vertical roadmap list with titles (the layout from before the sequencer), denser About page. Features from the revamp above are kept. Backups: `backups/2026-11-11-pre-revamp/` (old purple-era layout with red palette) and `backups/2026-11-11-sequencer-version/` (dark machine look).

## Up next (pick an order)
See the numbered suggestion list kept in chat. Rough grouping:

### Learning depth
- [ ] Interactive quizzes gating step progression (XP/badge scaffolding already in place; a passed quiz replaces "Mark complete")
- [ ] Better article generation (richer formatting, tighter personalisation)
- [ ] Inline glossary (tap a term for a definition)
- [ ] "Explain it differently" (regenerate simpler/advanced)
- [ ] Embedded mini-calculators in relevant lessons

### Persistence & accounts
- [ ] Persist progress server-side instead of `localStorage` (currently per-browser, lost if storage clears)
- [ ] Optional lightweight accounts so progress follows the user across devices

### Cross-mode
- [ ] "Compare" and "Decision" hand-offs (e.g. a Compare result offers "ask the decision coach about this")
- [ ] Save/history for past decisions and comparisons

### Polish
- [ ] Loading skeletons instead of spinners
- [ ] Empty-state illustrations
- [ ] Downloadable completion certificate
- [ ] Bookmark/revisit favourite lessons

## Known gotchas (don't re-break these)
- In `ui.css`, `.pq-section` / `.pq-page` set ONLY block-axis padding. The `padding` shorthand there overrides `.pq-wrap`'s horizontal padding (same specificity, later rule wins) and content runs edge-to-edge.
- No page uses a bare `<header>` for content; the shared banner partial is the only header. The XP bar is a `<div class="progress-header">` on purpose.
- All layout/visuals live in `static/ui.css`. Keep them out of inline `<style>` blocks.
- Deleting a template will 500 the deployment if a route still renders it. Remove the route in `backend.py` first, then the file. Removing a route is safe only if nothing links to it.
- The two chat histories are separate session keys (`chat_history` = Decision, `learning_chat_history` = Learning tutor). Keep them apart.
- **Never store conversation state in a plain Flask cookie session.** Browsers cap cookies at ~4093 bytes and drop oversized ones *silently*, which reads as "the AI forgot everything" rather than as a storage error. Sessions are filesystem-backed now; keep it that way.
- Anything resolving a path must use `BASE_DIR`, not a relative path or `os.getcwd()`. Under WSGI the working directory is not the project folder.
- **Jinja caches compiled templates when `FLASK_DEBUG` is off.** Editing a template will not show up until you restart the server. Run with `FLASK_DEBUG=true` while developing, or you will test stale markup and think your change did nothing.
- To add a quiz question, append to the `QUIZ` array in `mobo.html`. Add its `id` to `REQUIRED` only if the roadmap genuinely needs it, and add a matching branch in `synthesize()` or the answer will be collected but never reach MoBo.
- **CSS lives in layers now.** A rule that overrides a component MUST sit in a
  later layer than `components`, otherwise it silently loses no matter how
  specific it is. The responsive media queries were briefly in `@layer layout`
  and were being ignored for exactly this reason; they live in `@layer responsive`
  now. Preference queries (reduced-motion, contrast, forced-colors, pointer) are
  intentionally left unlayered, because unlayered normal declarations beat every
  layer.
- **Progress bars animate `scale`, not `width`.** They read a `--_p` custom
  property between 0 and 1. If you set `style.width` on `.xp-fill`,
  `.quiz-track-fill` or `.bar-fill` they will not move.
- **`home.css` resets lists with `:where(ul[class], ol[class])` on purpose.**
  The bare `ul[class]` form scores (0,1,1), which beats any single class, so it
  silently ate `.chain-list`'s `padding-top` and the "How it works" rule
  rendered straight through the headings on desktop and through the body copy
  on mobile. `:where()` holds the reset at zero specificity while still beating
  the browser default, because the cascade settles origin before specificity.
  Do not remove the `:where()`.
- **The homepage is its own world.** `static/home.css` is scoped to
  `body.pq-seq` and loaded only by `home.html`. Editing `ui.css` will not change
  the homepage, and editing `home.css` will not change any other page. If the
  two ever need to agree, change the tokens in both or adopt one deliberately.
