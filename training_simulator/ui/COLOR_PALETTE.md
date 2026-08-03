# Training Simulator — Professional Light Theme Color Palette

## Quick Reference

### Primary Colors

| Name | Hex Code | Usage | Tailwind Equiv |
|------|----------|-------|---|
| **Background** | `#f8fafc` | Page background | slate-50 |
| **Sidebar Header** | `#e8eef7` | Top bar, sidebar | slate-100 + tint |
| **Card** | `#ffffff` | Content cards | white |
| **Border** | `#e2e8f0` | Dividers, outlines | slate-200 |

### Text Colors

| Name | Hex Code | Usage | Tailwind Equiv |
|------|----------|-------|---|
| **Heading** | `#1e293b` | H1, H2, titles | slate-900 |
| **Body** | `#334155` | Paragraph text | slate-800 |
| **Secondary** | `#64748b` | Labels, hints | slate-600 |
| **Tertiary** | `#475569` | Very muted text | slate-700 |

### Accent & Action Colors

| Name | Hex Code | Usage | Tailwind Equiv |
|------|----------|-------|---|
| **Primary Accent** | `#0ea5e9` | Buttons, focus, active | sky-500 |
| **Accent Hover** | `#0284c7` | Button hover state | sky-600 |
| **Field Value** | `#0369a1` | Data display, links | sky-800 |

### Status Colors (with Light Backgrounds)

| Status | Icon | Color | Background | Meaning |
|--------|------|-------|---|---|
| Pending | ⏳ | `#94a3b8` | `#f1f5f9` | Waiting to start |
| In Progress | ◐ | `#f59e0b` | `#fef3c7` | Currently active |
| Complete | ✓ | `#16a34a` | `#dcfce7` | Finished, verified |
| Needs Fixes | ✗ | `#dc2626` | `#fee2e2` | Validation errors |

---

## Design System

### Spacing
- Standard padding: 12-16px
- Card padding: 14px
- Row padding: 8-10px (vertical)

### Typography
- **UI Font:** Segoe UI
- **Mono Font:** Consolas
- **Heading:** 13px bold (sky-blue)
- **Body:** 10px regular (slate)
- **Secondary:** 9px regular (slate-600)

### Borders & Shadows
- **Border color:** `#e2e8f0` (1px)
- **Dividers:** 1px horizontal lines (very subtle)
- **Shadows:** None (minimal design)

### Visual Hierarchy

1. **Headings** — Dark slate, bold, large
2. **Body text** — Medium slate, regular weight
3. **Secondary text** — Muted slate, smaller
4. **Accents** — Sky-blue for interactive elements
5. **Errors** — Red backgrounds with dark red text

---

## Implementation

All colors are defined in `widgets.py`:

```python
# Light theme tokens
BG_DARK = '#f8fafc'
BG_DARKER = '#e8eef7'
BG_CARD = '#ffffff'
BORDER = '#e2e8f0'
FG_LIGHT = '#1e293b'
FG_BODY = '#334155'
FG_MUTED = '#64748b'
FG_DIM = '#475569'
ACCENT = '#0ea5e9'
ACCENT_HOVER = '#0284c7'
VALUE_COLOR = '#0369a1'
```

To change theme globally, modify these tokens in:
- `training_simulator/ui/widgets.py`
- `training_simulator/ui/setup_dialog.py`
- `training_simulator/ui/verification_dialog.py`

---

## Accessibility Notes

✅ **Contrast Ratios:** All text meets WCAG AA standards (4.5:1+)  
✅ **Color-blind safe:** Status indicators use icons + colors  
✅ **Light backgrounds:** Reduce eye strain, suitable for extended use  
✅ **Clear hierarchy:** Visual importance matches semantic importance  

---

## Browser Equivalents

If porting to web (CSS/Tailwind):

```css
/* Backgrounds */
.bg-page { @apply bg-slate-50; }
.bg-header { @apply bg-slate-100; }
.bg-card { @apply bg-white; }
.border-subtle { @apply border-slate-200; }

/* Text */
.text-heading { @apply text-slate-900 font-bold; }
.text-body { @apply text-slate-800; }
.text-secondary { @apply text-slate-600; }

/* Accent */
.btn-primary { @apply bg-sky-500 hover:bg-sky-600 text-white; }
.text-value { @apply text-sky-800; }
```
