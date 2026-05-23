# htDash — Backlog (Planned Features)

Forward-looking features not yet designed or built. Each needs a dedicated
design pass before implementation (data model, UI, access control, audit
implications). This list will grow as more items are identified.

_Captured: 2026-05-22._

---

## 1. Retrospective event-notes for all events ✅ Implemented
Allow a note to be attached to **any completed event**, after the fact
(retrospectively), across all event types. Distinct from the per-event `notes`
field captured at filing time — these are added later for clarification or
correction context.

**Status:** ✅ implemented. Added/viewed from the **Timeline** tab (expand a row);
role-keyed `event_notes` on each event entry; immutable; `EvtNote-<R>-NNNN`
aliases. See `docs/pages.md` → Retrospective Event Notes and CLAUDE.md →
Patient Notes Tab → Retrospective event notes.

## 2. Retrospective admin comments on all events and free notes
Admin can add comments, after the fact, on **any event** and on **free notes**
(the Notes tab entries). Comment thread / annotation layer over existing
records.

**Status:** planned — needs design. Relates to [1] and to the immutable Notes
tab (notes themselves stay immutable; comments are a separate overlay).

## 3. Systematic access control across htDash
A detailed, systematic role-based access-control design covering every page,
tab, action, and API endpoint — replacing the current ad-hoc per-route checks.
Single source of truth for who (admin / therapist / engineer) can see and do
what.

**Status:** planned — needs design (RBAC matrix, enforcement layer, audit).

## 4. AG Watch data upload event (engineer), per patient, on watch change
A new **engineer event** to upload AG watch data for a patient whenever a watch
is changed. **Seeded automatically** off events where a watch is swapped —
i.e. Watch Records (`watch_record`) and any device-issue flow that swaps a
watch — so the engineer is prompted to pull and upload the data from the
removed watch.

**Status:** planned — needs design (event definition, seeding triggers, where
the uploaded data lands, file schema).

## 5. Final global lock of a patient record (admin)
When everything for a patient is complete, the admin can apply a **final global
lock** to the patient record. After locking, **no edits are possible by anyone**
(admin included) — the record becomes fully read-only.

**Status:** planned — needs design (lock flag + state, enforcement across all
write routes, unlock policy if any).

## 6. Overall study view page (recruitment summary, view-only)
A study-wide page showing a **recruitment summary across all three sites**
(Manipal, Ranipet, Ludhiana). **View-only** — no actions.

**Status:** planned — needs design (metrics, layout, who can view).

## 7. Study documents page (downloadable; SOPs as a wiki)
A page holding all study information, downloadable. **Study SOPs** rendered like
a wiki / Wikipedia-style page: table of contents, intra-page section links,
navigable structure.

**Status:** planned — needs design (content source/format, TOC generation,
download formats, access).

---

## Unsorted / to be identified
- **Devices section:** there is a known-but-not-yet-articulated item for the
  devices area. Placeholder — to be filled in when identified.
