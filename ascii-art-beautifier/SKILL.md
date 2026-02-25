---
name: ascii-art-beautifier
description: Beautifies and generates ASCII art diagrams in markdown files. Use when
  user says "beautify ascii", "fix ascii art", "align ascii", "выровняй разметку",
  "причеши ascii", "сделай разметку ровной", "fix diagram", "clean up ascii",
  or points to a markdown file with messy ASCII art in code blocks. Also generates
  new clean ASCII art from text descriptions when asked.
metadata:
  author: Anthony Vdovitchenko @ Automatica
  version: 1.0.0
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
4. **Redraw** each block following the Alignment Rules below.
5. **Edit** the file in-place using the Edit tool — replace ONLY the content inside each code block. Touch nothing else.
6. **Report** what was changed: number of blocks processed, summary of fixes.

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
3. **Nested depth**: Deeply nested boxes accumulate indent. Plan the total width before drawing.
4. **Mixed content**: Some boxes have 1 line of text, others have 3. All boxes at the same level should have consistent height when they're in the same visual row.
