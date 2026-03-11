#!/usr/bin/env python3
"""Three-way merge (diff3) — merge two modified versions against a common ancestor.

Implements the diff3 algorithm used by version control systems.
Detects conflicts when both sides modify the same region differently.

Usage:
    python diff3.py base.txt left.txt right.txt
    python diff3.py --test
"""

import sys


def lcs_table(a: list, b: list) -> list:
    """Build LCS length table."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp


def diff(a: list, b: list) -> list:
    """Compute diff as list of (tag, a_start, a_end, b_start, b_end).
    Tags: 'equal', 'replace', 'insert', 'delete'."""
    dp = lcs_table(a, b)
    # Backtrack to get alignment
    i, j = len(a), len(b)
    ops = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            ops.append(('equal', i-1, i, j-1, j))
            i -= 1; j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            ops.append(('insert', i, i, j-1, j))
            j -= 1
        else:
            ops.append(('delete', i-1, i, j, j))
            i -= 1
    ops.reverse()

    # Merge consecutive same-tag ops
    merged = []
    for op in ops:
        if merged and merged[-1][0] == op[0]:
            last = merged[-1]
            merged[-1] = (last[0], last[1], op[2], last[3], op[4])
        elif merged and merged[-1][0] in ('delete', 'insert') and op[0] in ('delete', 'insert') and merged[-1][0] != op[0]:
            last = merged[-1]
            merged[-1] = ('replace', min(last[1], op[1]), max(last[2], op[2]),
                          min(last[3], op[3]), max(last[4], op[4]))
        else:
            merged.append(op)
    return merged


def merge3(base: list, left: list, right: list) -> tuple:
    """Three-way merge. Returns (merged_lines, conflicts).
    Conflicts are list of (base_chunk, left_chunk, right_chunk)."""
    left_diff = diff(base, left)
    right_diff = diff(base, right)

    # Build change maps: base line index -> change
    left_changes = {}
    for tag, a0, a1, b0, b1 in left_diff:
        if tag != 'equal':
            for i in range(a0, max(a1, a0 + 1)):
                left_changes[i] = (tag, a0, a1, b0, b1)

    right_changes = {}
    for tag, a0, a1, b0, b1 in right_diff:
        if tag != 'equal':
            for i in range(a0, max(a1, a0 + 1)):
                right_changes[i] = (tag, a0, a1, b0, b1)

    result = []
    conflicts = []
    i = 0
    processed_left = set()
    processed_right = set()

    while i < len(base) or i in left_changes or i in right_changes:
        if i >= len(base) and i not in left_changes and i not in right_changes:
            break

        l_change = left_changes.get(i)
        r_change = right_changes.get(i)

        if l_change and id(l_change) not in processed_left and r_change and id(r_change) not in processed_right:
            # Both sides changed — check if same change
            _, la0, la1, lb0, lb1 = l_change
            _, ra0, ra1, rb0, rb1 = r_change
            left_new = left[lb0:lb1]
            right_new = right[rb0:rb1]
            if left_new == right_new:
                result.extend(left_new)
            else:
                conflicts.append((base[la0:la1], left_new, right_new))
                result.append(f"<<<<<<< LEFT")
                result.extend(left_new)
                result.append(f"=======")
                result.extend(right_new)
                result.append(f">>>>>>> RIGHT")
            processed_left.add(id(l_change))
            processed_right.add(id(r_change))
            i = max(la1, ra1)
        elif l_change and id(l_change) not in processed_left:
            _, la0, la1, lb0, lb1 = l_change
            result.extend(left[lb0:lb1])
            processed_left.add(id(l_change))
            i = la1
        elif r_change and id(r_change) not in processed_right:
            _, ra0, ra1, rb0, rb1 = r_change
            result.extend(right[rb0:rb1])
            processed_right.add(id(r_change))
            i = ra1
        else:
            if i < len(base):
                result.append(base[i])
            i += 1

    return result, conflicts


def test():
    print("=== Three-Way Merge Tests ===\n")

    # No conflict: different regions
    base = ["a", "b", "c", "d", "e"]
    left = ["a", "B", "c", "d", "e"]   # changed b→B
    right = ["a", "b", "c", "D", "e"]  # changed d→D
    merged, conflicts = merge3(base, left, right)
    assert conflicts == []
    assert "B" in merged and "D" in merged
    print(f"✓ Clean merge (no conflict): {merged}")

    # Same change both sides
    left2 = ["a", "X", "c", "d", "e"]
    right2 = ["a", "X", "c", "d", "e"]
    merged2, conflicts2 = merge3(base, left2, right2)
    assert conflicts2 == []
    assert "X" in merged2
    print(f"✓ Same change both sides: {merged2}")

    # Conflict: same region, different changes
    left3 = ["a", "L", "c", "d", "e"]
    right3 = ["a", "R", "c", "d", "e"]
    merged3, conflicts3 = merge3(base, left3, right3)
    assert len(conflicts3) == 1
    assert "<<<<<<< LEFT" in merged3
    print(f"✓ Conflict detected: {len(conflicts3)} conflict(s)")

    # Insertion
    left4 = ["a", "b", "NEW", "c", "d", "e"]
    right4 = ["a", "b", "c", "d", "e"]
    merged4, _ = merge3(base, left4, right4)
    assert "NEW" in merged4
    print(f"✓ Left insertion preserved")

    # Deletion
    left5 = ["a", "c", "d", "e"]  # deleted b
    right5 = ["a", "b", "c", "d", "e"]
    merged5, _ = merge3(base, left5, right5)
    assert "b" not in merged5
    print(f"✓ Left deletion applied")

    print("\nAll tests passed! ✓")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--test":
        test()
    elif len(args) == 3:
        with open(args[0]) as f: base = f.read().splitlines()
        with open(args[1]) as f: left = f.read().splitlines()
        with open(args[2]) as f: right = f.read().splitlines()
        merged, conflicts = merge3(base, left, right)
        print('\n'.join(merged))
        if conflicts:
            print(f"\n--- {len(conflicts)} conflict(s) ---", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
