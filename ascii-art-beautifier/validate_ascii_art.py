#!/usr/bin/env python3
"""
ASCII Art Validator & Fixer for Markdown files.

Extracts code blocks containing box-drawing characters from markdown files,
validates their alignment, and reports issues.

Usage:
    python3 validate_ascii_art.py <file.md> [--fix] [--block N]

Options:
    --fix       Auto-fix line width issues (pad shorter lines)
    --block N   Only process block number N (1-indexed)
    --verbose   Show detailed analysis per block
    --quiet     Only print summary line
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Optional


# Box-drawing character sets (Unicode)
CORNERS_TL = set("┌╔╓╒")
CORNERS_TR = set("┐╗╖╕")
CORNERS_BL = set("└╚╙╘")
CORNERS_BR = set("┘╝╜╛")
HORIZONTALS = set("─═╌╍┄┅┈┉")
VERTICALS = set("│║╎╏┆┇┊┋")
T_JUNCTIONS = set("┬┴├┤┼╦╩╠╣╬╤╧╟╢╪")
ALL_BOX = CORNERS_TL | CORNERS_TR | CORNERS_BL | CORNERS_BR | HORIZONTALS | VERTICALS | T_JUNCTIONS

# ASCII-style box-drawing character sets (old-style +--+, |, -)
ASCII_CORNERS = set("+")
ASCII_HORIZONTALS = set("-=")
ASCII_VERTICALS = set("|")
ASCII_BOX = ASCII_CORNERS | ASCII_HORIZONTALS | ASCII_VERTICALS


@dataclass
class Issue:
    block_num: int
    line_num: int  # 0-indexed within block
    col: Optional[int]
    severity: str  # "error", "warning"
    message: str

    def __str__(self):
        loc = f"Block {self.block_num}, Line {self.line_num}"
        if self.col is not None:
            loc += f", Col {self.col}"
        return f"[{self.severity.upper()}] {loc}: {self.message}"


@dataclass
class Box:
    """A detected box in the ASCII art."""
    top_row: int
    bot_row: int
    left_col: int
    right_col: int

    @property
    def width(self):
        return self.right_col - self.left_col + 1

    @property
    def height(self):
        return self.bot_row - self.top_row + 1

    @property
    def inner_width(self):
        return self.width - 2

    def __repr__(self):
        return f"Box(rows={self.top_row}-{self.bot_row}, cols={self.left_col}-{self.right_col}, {self.width}x{self.height})"


def _has_ascii_box_pattern(text: str) -> bool:
    """Check if text contains ASCII-style box patterns like +--+ or |...|"""
    plus_count = text.count('+')
    has_hline = bool(re.search(r'\+[-=]+\+', text))
    has_vline = bool(re.search(r'^\s*\|', text, re.MULTILINE))
    return plus_count >= 4 and has_hline and has_vline


def extract_code_blocks(content: str) -> list[tuple[int, list[str]]]:
    """Extract code blocks with box-drawing chars from markdown content.
    Returns list of (start_line_0indexed, lines) tuples."""
    blocks = []
    lines = content.split('\n')
    in_block = False
    block_start = -1
    block_lines = []

    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if stripped == '```':
            if not in_block:
                in_block = True
                block_start = i + 1
                block_lines = []
            else:
                # Check if block has Unicode box-drawing chars OR ASCII box patterns.
                # Join with newlines so that re.MULTILINE anchors work in _has_ascii_box_pattern.
                text = '\n'.join(block_lines)
                if any(c in ALL_BOX for c in text) or _has_ascii_box_pattern(text):
                    blocks.append((block_start, block_lines))
                in_block = False
        elif in_block:
            block_lines.append(line.rstrip('\n'))

    return blocks


def check_line_widths(lines: list[str], block_num: int) -> list[Issue]:
    """Check that all lines have the same width."""
    issues = []
    if not lines:
        return issues

    widths = [len(line) for line in lines]
    max_w = max(widths)
    min_w = min(widths)

    if max_w != min_w:
        for i, (line, w) in enumerate(zip(lines, widths)):
            if w != max_w:
                issues.append(Issue(
                    block_num, i, None, "error",
                    f"Line width {w}, expected {max_w} (off by {max_w - w})"
                ))

    return issues


def find_vertical_columns(lines: list[str]) -> dict[int, list[int]]:
    """Find columns that contain vertical border characters.
    Returns {col: [row_indices]} for each column with │."""
    cols = {}
    for row, line in enumerate(lines):
        for col, ch in enumerate(line):
            if ch in VERTICALS or ch in T_JUNCTIONS:
                if col not in cols:
                    cols[col] = []
                cols[col].append(row)
    return cols


def check_vertical_continuity(lines: list[str], block_num: int) -> list[Issue]:
    """Check that vertical borders │ are continuous (no gaps mid-box)."""
    issues = []
    cols = find_vertical_columns(lines)

    for col, rows in cols.items():
        if len(rows) < 2:
            continue

        # Check for gaps: if there's a │ at rows 5 and 8 but not 6-7,
        # that's only OK if there's a corner (└ or ┘) at row 5 or (┌ or ┐) at row 8
        for i in range(len(rows) - 1):
            r1 = rows[i]
            r2 = rows[i + 1]
            gap = r2 - r1

            if gap <= 1:
                continue

            # Check if this gap is expected (box ended and new box started)
            ch1 = lines[r1][col] if col < len(lines[r1]) else ' '
            ch2 = lines[r2][col] if col < len(lines[r2]) else ' '

            # If neither end is a junction/corner, it might be a problem
            # But this is complex to analyze, so we only warn for large gaps
            if gap > 5:
                issues.append(Issue(
                    block_num, r1, col, "warning",
                    f"Vertical border gap: │ at row {r1} and {r2} (gap of {gap} rows)"
                ))

    return issues


def detect_boxes(lines: list[str]) -> list[Box]:
    """Detect rectangular boxes by finding ┌...┐ and matching └...┘."""
    boxes = []

    for row, line in enumerate(lines):
        col = 0
        while col < len(line):
            if line[col] in CORNERS_TL:
                # Found top-left corner, scan right for ┐
                end_col = col + 1
                while end_col < len(line):
                    ch = line[end_col]
                    if ch in CORNERS_TR:
                        # Found matching top-right corner
                        # Now search down for └...┘
                        width = end_col - col + 1
                        for bot_row in range(row + 1, len(lines)):
                            if bot_row < len(lines) and col < len(lines[bot_row]):
                                bot_ch = lines[bot_row][col] if col < len(lines[bot_row]) else ' '
                                if bot_ch in CORNERS_BL:
                                    # Check if there's a ┘ at the right position
                                    if end_col < len(lines[bot_row]):
                                        bot_right = lines[bot_row][end_col]
                                        if bot_right in CORNERS_BR:
                                            boxes.append(Box(row, bot_row, col, end_col))
                                            break
                        break
                    elif ch not in HORIZONTALS and ch not in T_JUNCTIONS:
                        break
                    end_col += 1
            col += 1

    return boxes


def check_box_borders(lines: list[str], block_num: int) -> list[Issue]:
    """Check that box top and bottom borders have matching widths."""
    issues = []
    boxes = detect_boxes(lines)

    for box in boxes:
        # Check top border width
        top_line = lines[box.top_row] if box.top_row < len(lines) else ""
        bot_line = lines[box.bot_row] if box.bot_row < len(lines) else ""

        # Count horizontal chars in top border
        top_h = 0
        for c in range(box.left_col, min(box.right_col + 1, len(top_line))):
            if top_line[c] in HORIZONTALS | T_JUNCTIONS | CORNERS_TL | CORNERS_TR:
                top_h += 1

        bot_h = 0
        for c in range(box.left_col, min(box.right_col + 1, len(bot_line))):
            if bot_line[c] in HORIZONTALS | T_JUNCTIONS | CORNERS_BL | CORNERS_BR:
                bot_h += 1

        if top_h != bot_h:
            issues.append(Issue(
                block_num, box.top_row, box.left_col, "error",
                f"Box width mismatch: top border {top_h} chars, bottom border {bot_h} chars ({box})"
            ))

        # Check vertical borders exist on intermediate rows
        for r in range(box.top_row + 1, box.bot_row):
            if r < len(lines):
                left_ch = lines[r][box.left_col] if box.left_col < len(lines[r]) else ' '
                right_ch = lines[r][box.right_col] if box.right_col < len(lines[r]) else ' '

                if left_ch not in VERTICALS | T_JUNCTIONS:
                    issues.append(Issue(
                        block_num, r, box.left_col, "error",
                        f"Missing left │ for {box}"
                    ))
                if right_ch not in VERTICALS | T_JUNCTIONS:
                    issues.append(Issue(
                        block_num, r, box.right_col, "error",
                        f"Missing right │ for {box}"
                    ))

    return issues


def check_content_padding(lines: list[str], block_num: int) -> list[Issue]:
    """Check that text inside boxes has at least 1 space padding from borders."""
    issues = []
    boxes = detect_boxes(lines)

    for box in boxes:
        for r in range(box.top_row + 1, box.bot_row):
            if r >= len(lines):
                continue
            line = lines[r]

            # Check left padding: character after left │ should be space
            left_content_col = box.left_col + 1
            if left_content_col < len(line) and line[left_content_col] not in (' ', '│', '┌', '└', '─'):
                # Allow box-drawing chars (nested boxes)
                if line[left_content_col] not in ALL_BOX:
                    issues.append(Issue(
                        block_num, r, left_content_col, "warning",
                        f"No left padding: '{line[left_content_col]}' touches left border"
                    ))

            # Check right padding: character before right │ should be space
            right_content_col = box.right_col - 1
            if right_content_col >= 0 and right_content_col < len(line):
                ch = line[right_content_col]
                if ch not in (' ', '│', '┐', '┘', '─') and ch not in ALL_BOX:
                    issues.append(Issue(
                        block_num, r, right_content_col, "warning",
                        f"No right padding: '{ch}' touches right border"
                    ))

    return issues


def check_symmetry(lines: list[str], block_num: int) -> list[Issue]:
    """Detect potential symmetric regions and check they match."""
    issues = []
    boxes = detect_boxes(lines)

    # Group boxes by row and similar dimensions
    # Find boxes on the same row with same height
    row_groups = {}
    for box in boxes:
        key = (box.top_row, box.bot_row)
        if key not in row_groups:
            row_groups[key] = []
        row_groups[key].append(box)

    for key, group in row_groups.items():
        if len(group) < 2:
            continue

        # Check if boxes at same level have same dimensions
        widths = [b.width for b in group]
        if len(set(widths)) > 1:
            # Check if they SHOULD be symmetric (similar content)
            width_counts = {}
            for w in widths:
                width_counts[w] = width_counts.get(w, 0) + 1

            # Only warn if most boxes have one width but some differ
            max_count_w = max(width_counts, key=width_counts.get)
            for box in group:
                if box.width != max_count_w:
                    issues.append(Issue(
                        block_num, box.top_row, box.left_col, "warning",
                        f"Box width {box.width} differs from siblings (most are {max_count_w})"
                    ))

    return issues


def fix_line_widths(lines: list[str]) -> list[str]:
    """Pad all lines to the maximum width."""
    if not lines:
        return lines
    max_w = max(len(l) for l in lines)
    return [l + ' ' * (max_w - len(l)) for l in lines]


def find_nesting(boxes: list[Box]) -> dict[int, list[int]]:
    """Find which boxes are nested inside which.
    Returns {parent_index: [child_indices]}."""
    nesting = {}
    for i, outer in enumerate(boxes):
        children = []
        for j, inner in enumerate(boxes):
            if i == j:
                continue
            if (inner.top_row > outer.top_row and inner.bot_row < outer.bot_row
                    and inner.left_col > outer.left_col and inner.right_col < outer.right_col):
                children.append(j)
        if children:
            nesting[i] = children
    return nesting


def fix_nested_boxes(lines: list[str]) -> list[str]:
    """Rebuild lines in nested box structures to ensure correct │ placement.

    For each outer box that contains inner boxes:
    1. Determines the outer width from the outer box
    2. For each content line, strips existing outer borders, pads inner content
       to exact width, and re-wraps with outer borders at correct columns.
    """
    boxes = detect_boxes(lines)
    if not boxes:
        return lines

    nesting = find_nesting(boxes)
    if not nesting:
        # No nesting detected — just fix line widths
        return fix_line_widths(lines)

    result = list(lines)

    for parent_idx, child_indices in nesting.items():
        outer = boxes[parent_idx]
        outer_w = outer.width
        target_len = outer.left_col + outer_w  # total line length including any prefix

        # Rebuild each content line within the outer box
        for row in range(outer.top_row + 1, outer.bot_row):
            if row >= len(result):
                continue

            line = result[row]

            # If line is already the correct total length, skip
            if len(line) == target_len:
                continue

            # Determine left and right border characters
            left_col = outer.left_col
            right_col = outer.left_col + outer_w - 1

            left_char = "│"
            if left_col < len(line) and line[left_col] in VERTICALS | T_JUNCTIONS:
                left_char = line[left_col]

            # Extract inner content: everything between outer borders.
            # The existing right │ may be at a wrong position — strip it.
            inner_start = left_col + 1
            inner_end = min(len(line), right_col)  # don't go past target right col

            # If the line's last char is a border char at or near the expected right col,
            # exclude it from content (it will be re-added)
            raw_inner = line[inner_start:]
            if raw_inner and raw_inner[-1] in VERTICALS | T_JUNCTIONS:
                right_char = raw_inner[-1]
                raw_inner = raw_inner[:-1]
            else:
                right_char = "│"

            # Pad inner content to exact width (outer_w - 2 = space between borders)
            inner_width = outer_w - 2
            padded_inner = raw_inner.ljust(inner_width)[:inner_width]

            # Reconstruct
            prefix = line[:left_col] if left_col > 0 else ""
            result[row] = prefix + left_char + padded_inner + right_char

    return result


def validate_file(filepath: str, fix: bool = False, fix_nested: bool = False,
                  block_num: Optional[int] = None,
                  verbose: bool = False, quiet: bool = False) -> list[Issue]:
    """Validate all ASCII art blocks in a markdown file."""
    with open(filepath) as f:
        content = f.read()

    blocks = extract_code_blocks(content)
    all_issues = []

    for i, (start_line, lines) in enumerate(blocks):
        num = i + 1
        if block_num is not None and num != block_num:
            continue

        if not quiet:
            print(f"\n{'='*60}")
            print(f"Block {num} (line {start_line + 1}, {len(lines)} lines)")
            print(f"{'='*60}")

        # Run all checks
        issues = []
        issues.extend(check_line_widths(lines, num))
        issues.extend(check_box_borders(lines, num))
        issues.extend(check_vertical_continuity(lines, num))
        issues.extend(check_content_padding(lines, num))
        issues.extend(check_symmetry(lines, num))

        # Box analysis
        boxes = detect_boxes(lines)
        if verbose and not quiet:
            print(f"\nDetected {len(boxes)} boxes:")
            for box in boxes:
                print(f"  {box}")
            nesting = find_nesting(boxes)
            if nesting:
                print(f"\nNesting structure:")
                for parent_idx, child_indices in nesting.items():
                    parent = boxes[parent_idx]
                    children = [boxes[ci] for ci in child_indices]
                    print(f"  {parent} contains:")
                    for child in children:
                        print(f"    {child}")

        if not quiet:
            # Line width summary
            widths = [len(l) for l in lines]
            unique_widths = set(widths)
            if len(unique_widths) == 1:
                print(f"Line widths: all {widths[0]} chars ✅")
            else:
                print(f"Line widths: {sorted(unique_widths)} ❌")

            # Report issues
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]

            if not issues:
                print("No issues found ✅")
            else:
                if errors:
                    print(f"\n{len(errors)} error(s):")
                    for issue in errors:
                        print(f"  {issue}")
                if warnings:
                    print(f"\n{len(warnings)} warning(s):")
                    for issue in warnings:
                        print(f"  {issue}")

        all_issues.extend(issues)

        # Auto-fix: nested box rebuild (includes line width fix)
        if fix_nested:
            fixed = fix_nested_boxes(lines)
            if fixed != lines:
                old_block = '\n'.join(lines)
                new_block = '\n'.join(fixed)
                content = content.replace(old_block, new_block, 1)
                if not quiet:
                    print(f"\n✅ Rebuilt nested box alignment (width {max(len(l) for l in fixed)})")
        # Auto-fix line widths if requested (simpler: just pad)
        elif fix and any(isinstance(i, Issue) and "Line width" in i.message for i in issues):
            fixed = fix_line_widths(lines)
            # Replace in content
            old_block = '\n'.join(lines)
            new_block = '\n'.join(fixed)
            content = content.replace(old_block, new_block, 1)
            if not quiet:
                print(f"\n✅ Fixed line widths (padded to {max(len(l) for l in fixed)})")

    if fix or fix_nested:
        with open(filepath, 'w') as f:
            f.write(content)
        if not quiet:
            print(f"\n💾 Saved fixes to {filepath}")

    # Summary (always printed)
    total_errors = sum(1 for i in all_issues if i.severity == "error")
    total_warnings = sum(1 for i in all_issues if i.severity == "warning")
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(blocks)} blocks, {total_errors} errors, {total_warnings} warnings")
    if total_errors == 0 and total_warnings == 0:
        print("All blocks are clean! ✅")
    print(f"{'='*60}")

    return all_issues


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate ASCII art in markdown files")
    parser.add_argument("file", help="Markdown file to validate")
    parser.add_argument("--fix", action="store_true", help="Auto-fix line width issues")
    parser.add_argument("--fix-nested", action="store_true", help="Rebuild nested box alignment (fixes inner border positions)")
    parser.add_argument("--block", type=int, help="Only process block N (1-indexed)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed box analysis")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only print summary line")
    args = parser.parse_args()

    issues = validate_file(args.file, fix=args.fix, fix_nested=args.fix_nested,
                           block_num=args.block, verbose=args.verbose, quiet=args.quiet)
    sys.exit(1 if any(i.severity == "error" for i in issues) else 0)
