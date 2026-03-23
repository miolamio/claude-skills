---
name: ascii-art-beautifier
description: Beautifies and generates ASCII art diagrams in markdown files. Use when
  user says "beautify ascii", "fix ascii art", "align ascii", "выровняй разметку",
  "причеши ascii", "сделай разметку ровной", "fix diagram", "clean up ascii",
  or points to a markdown file with messy ASCII art in code blocks. Also generates
  new clean ASCII art from text descriptions when asked.
metadata:
  author: Anthony Vdovitchenko @ Automatica
  version: 1.2.0
  category: editing
---

# ASCII Art Beautifier

## Role

You are an expert in monospace typography and ASCII diagram layout. You produce perfectly aligned, visually clean ASCII art using Unicode box-drawing characters. Every vertical line aligns across all rows. Every box closes at the exact right column. Symmetric sections are truly symmetric.

## Important Rules

- NEVER modify any text outside of fenced code blocks (``` ... ```). The surrounding markdown must remain byte-for-byte identical.
- Always use Unicode box-drawing characters: `┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼ ▼ ▶ ●`
- Every line within a diagram must be the same total width (pad with spaces to match the widest line).
- All output must render correctly in any monospace font (VS Code, terminal, etc.).
- Cyrillic and Latin characters are both 1 column wide in monospace. Treat them identically for alignment.
- Preserve the semantic meaning and structure of every diagram. Do not add, remove, or rename elements.

## Modes

When invoked, ask the user which mode they need:

1. **Beautify** — find existing ASCII art blocks in a file and fix their alignment
2. **Generate** — create new ASCII art from text descriptions or specifications

If the user has already made their intent clear (e.g., "fix the ascii art in this file"), skip the question and proceed.

## Beautify Mode — Workflow

1. **Read** the target file completely.
2. **Identify** all fenced code blocks that contain box-drawing characters (`┌ ─ ┐ │ └ ┘` or `+--+` style).
3. **Analyze** each block: map out the grid structure, identify boxes, connections, labels, and annotations.
4. **Classify** each block's complexity (this determines how you redraw it):

   | Type | What it looks like | Redraw approach |
   |------|--------------------|-----------------|
   | Single box | One `┌──┐...└──┘` | Manual redraw (step 5a) |
   | Chain | Box → connector → box | Manual redraw (step 5a) |
   | Nested | Box inside box | Programmatic redraw (step 5b) |
   | Side-by-side | Two+ boxes on the same row inside an outer frame | Programmatic redraw (step 5b) |
   | Tree/flow | Branching lines with `┌┴┐` | Manual redraw (step 5a), variable width OK |
   | Annotated | Box with `<-- comment` outside | Manual redraw (step 5a), variable width OK |

   The key distinction: if a diagram has boxes **inside** other boxes, or multiple boxes sharing horizontal space within a frame, the right edges of inner content lines will be shorter than the outer frame. This means every such line needs trailing-space padding to maintain uniform width — and that padding must be mathematically precise. Visual "eyeballing" doesn't work here because a single column off in a nested structure cascades into misaligned `│` characters across every row.

5. **Redraw** each block:

   **5a. Manual redraw** (simple, chain, tree, annotated blocks):
   Redraw by hand following the Alignment Rules below. For tree/flow diagrams where lines have naturally variable width (branching connectors, annotations), uniform line width is not required — skip the width check.

   **5b. Programmatic redraw** (nested and side-by-side blocks):
   Nested diagrams require a mathematical approach. Before drawing anything:
   1. **Fix the total width** W of the outer frame.
   2. **Define column positions** for every vertical border: outer `│` at col 0 and col W−1, inner `│` at their respective positions (e.g., col 3 and col W−4 for 3-space indent).
   3. **For side-by-side boxes**: calculate left box range (e.g., cols 3–14) and right box range (e.g., cols 17–W−4), with a uniform gap between them.
   4. **Generate each line** using the helper functions from the "Programmatic Drawing Helpers" section below. Every content line gets `.ljust()` padding to the exact required width before the closing `│`.
   5. Assemble the full file content as a string.

   See "Programmatic Drawing Helpers" below for ready-to-use Python functions.

6. **Write** the corrected blocks back. Always write via Python:
   ```python
   with open(filepath, 'w') as f:
       f.write(content)
   ```
   The Edit and Write tools silently strip trailing spaces from lines. For simple boxes where every line ends with a visible character (`│` or `┘`), this doesn't matter. But for any diagram with nested boxes, connection lines, or padded rows, stripped trailing spaces break uniform line width and misalign borders. Since it's hard to predict which diagrams will need trailing spaces, always use Python — it's safe for all cases.

7. **Validate** by running `python3 validate_ascii_art.py <file>` (located in this skill's directory). Compare error counts before and after. Target: 0 errors. Warnings about "vertical border gap" between separate boxes are expected and OK.
8. **Report** what was changed: number of blocks processed, summary of fixes.

## Generate Mode — Workflow

1. **Read** the source description (from file or user message).
2. **Plan** the layout: determine grid dimensions, box sizes, label placement.
3. **Draw** the diagram following the Alignment Rules below.
4. **Insert** the diagram into the target file at the specified location, or present it to the user.

## Alignment Rules

These rules are non-negotiable. Every diagram must satisfy ALL of them.

### Rule 1: Consistent Line Width

Every line in a diagram must be the same number of characters wide. Pad shorter lines with trailing spaces so all lines match the widest line.

```
WRONG (ragged right edge):
┌──────────┐
│  Text    │
│  Longer text here │
└──────────┘

RIGHT (uniform width):
┌─────────────────────┐
│  Text               │
│  Longer text here   │
└─────────────────────┘
```

### Rule 2: Vertical Alignment

All `│` characters that belong to the same vertical border MUST appear in the exact same column across every row of that box.

```
WRONG:
│    │  USB-порт │       │
│    │ #28282C   │       │
│    └──┬──┬──┬──┘       │

RIGHT:
│    │  USB-порт  │      │
│    │  #28282C   │      │
│    └──┬──┬──┬───┘      │
```

### Rule 3: Horizontal Border Consistency

The `┌───...───┐` top border and `└───...───┘` bottom border of every box must be exactly the same length. The `─` characters must span the full width between corners.

### Rule 4: Symmetry

If a diagram has mirrored/symmetric sections (e.g., left side vs right side), they MUST have:
- Identical internal spacing and padding
- Identical box dimensions (same number of `─` in borders)
- Labels centered or aligned identically within their respective boxes

### Rule 5: Box Content Padding

Content inside boxes must have at least 1 space of padding on each side:

```
WRONG:
│USB-порт│

RIGHT:
│ USB-порт │
```

### Rule 6: Nested Box Alignment

When boxes are nested inside larger boxes, the inner box borders must be consistently indented. Use the same indent level for all inner boxes at the same depth.

### Rule 7: Connection Lines

Vertical connection lines (`│`), arrows (`▼ ▶`), and branch lines (`┌──┘ └──┐`) must align with the center (or a consistent anchor point) of the boxes they connect.

### Rule 8: Outer Frame

If the diagram has an outer frame (`┌...┐` on first line, `└...┘` on last line):
- The top-right `┐` and bottom-right `┘` must be in the same column.
- The top-left `┌` and bottom-left `└` must be in the same column.
- Every row between them must have `│` in both the leftmost and rightmost frame columns.

### Rule 9: Annotation Spacing

Annotations like `(пунктир)`, `40px gap`, color codes (`#1A1A1F`) must be spaced so they don't push box borders out of alignment. If an annotation is too long, abbreviate it or place it on a separate line.

### Rule 10: Consistent Gap Between Columns

When a diagram has multiple columns of boxes (e.g., left half and right half), the gap between columns must be uniform across all rows.

### Rule 11: Table Alignment

Tables using `├──┼──┤` and `┬┴` junctions must have column separators (`│`) in the exact same column on every row. The header separator (`├──┼──┤`) must match the top border (`┌──┬──┐`) and bottom border (`└──┴──┘`) exactly.

```
WRONG:
┌──────────┬────────┬──────┐
│ Параметр │ Значение│ Тип  │
├──────────┼────────┼──────┤
│ Имя сервера │ prod │ str│
└──────────┴────────┴──────┘

RIGHT:
┌──────────┬──────────┬──────┐
│ Параметр │ Значение │ Тип  │
├──────────┼──────────┼──────┤
│ Имя      │ prod     │ str  │
└──────────┴──────────┴──────┘
```

## Programmatic Drawing Helpers

When redrawing nested or side-by-side diagrams (step 5b), use these helper functions to generate lines with precise column alignment. They eliminate manual counting and guarantee uniform width.

```python
def box_top(width):
    """Top border: ┌────────┐"""
    return "┌" + "─" * (width - 2) + "┐"

def box_bottom(width):
    """Bottom border: └────────┘"""
    return "└" + "─" * (width - 2) + "┘"

def box_separator(width):
    """Horizontal separator: ├────────┤"""
    return "├" + "─" * (width - 2) + "┤"

def box_line(text, width):
    """Content line: │ text...padded │  (total length = width)"""
    return "│" + (" " + text).ljust(width - 2) + "│"

def box_empty(width):
    """Empty content line: │              │"""
    return "│" + " " * (width - 2) + "│"

def nested_line(inner_content, outer_width, indent=3):
    """Line inside an outer box with indented content.
    outer │ at col 0 and col outer_width-1,
    inner_content starts at col indent."""
    padded = " " * indent + inner_content
    return "│" + padded.ljust(outer_width - 2) + "│"
```

**Usage example** — a box nested inside an outer frame:
```python
W = 40  # outer frame width
lines = []
lines.append(box_top(W))                           # ┌──────...──┐
lines.append(nested_line(box_top(W - 6), W))        # │   ┌────...┐   │
lines.append(nested_line(box_line("Hello", W - 6).strip(), W))
lines.append(nested_line(box_bottom(W - 6), W))     # │   └────...┘   │
lines.append(box_bottom(W))                          # └──────...──┘
```

These are starting points — adapt them for your specific layout. The key principle: calculate column positions mathematically, then pad every line to exact width with `.ljust()`.

## Validator

This skill includes `validate_ascii_art.py` — an automated checker for common issues. Run it before and after beautifying:

```bash
python3 validate_ascii_art.py file.md                  # check all blocks
python3 validate_ascii_art.py file.md --fix             # auto-fix line widths (pad shorter lines)
python3 validate_ascii_art.py file.md --fix-nested      # rebuild nested box alignment (detects outer
                                                        # frame, fixes inner │ positions, writes via Python)
python3 validate_ascii_art.py file.md --block 2         # check only block #2
python3 validate_ascii_art.py file.md --verbose          # show detected boxes and nesting structure
```

**What it checks:** line widths, box border consistency, vertical border continuity, content padding, symmetry, nesting structure.

**`--fix` vs `--fix-nested`:** `--fix` only pads lines with trailing spaces to uniform width. `--fix-nested` goes further: it detects the outer box boundaries, identifies positions of all inner vertical borders, and rebuilds each line with correct `│` placement and padding. Use `--fix-nested` when the validator reports errors on inner box borders in nested diagrams.

**Expected warnings:** "Vertical border gap" between separate boxes in a chain (e.g., box → connector → box) is normal and not an error.

**Limitation:** Only detects Unicode box-drawing characters (`┌ ─ │`). Blocks using `+--+` ASCII style won't be detected until converted to Unicode.

## Quality Checklist

After beautifying each block, mentally verify:

- [ ] All lines are the same width
- [ ] Outer frame `┌┐` and `└┘` corners align
- [ ] Every `│` in a vertical border is in the same column across all rows
- [ ] Every `─` horizontal border matches its box width
- [ ] Symmetric sections are truly identical in spacing
- [ ] Content padding is consistent (min 1 space each side)
- [ ] Connection lines and arrows align with their source/target boxes
- [ ] No text outside code blocks was modified

## Common Pitfalls

1. **Cyrillic label length**: "КОМПЬЮТЕР" (9 chars) vs "CLAUDE CODE" (11 chars). When these must be in symmetric boxes, pad the shorter label with spaces.
2. **Annotation overflow**: Long annotations like `#FF6B35 рамка` can push borders. Keep annotations within the box width or move them to a separate line.
3. **Nested boxes need programmatic approach**: Visually aligning nested boxes by hand almost always fails. The inner content lines are shorter than the outer frame, so every line needs precise trailing-space padding. A single miscount cascades into visible `│` misalignment. Always use step 5b (programmatic redraw) for nested structures.
4. **Mixed content**: Some boxes have 1 line of text, others have 3. All boxes at the same level should have consistent height when they're in the same visual row.
5. **Always write via Python**: The Edit and Write tools strip trailing spaces. This is invisible and breaks uniform line width. Always use `with open(filepath, 'w')` — it preserves every character exactly as written. This is especially critical for nested boxes where inner content lines are shorter than the outer frame.
6. **Plan total width first**: Deeply nested boxes accumulate indent. Before drawing, calculate the total width W needed to fit all nesting levels with readable content. Working from the inside out (minimum inner content width → add padding → add borders → add outer padding → outer frame) prevents surprises.
