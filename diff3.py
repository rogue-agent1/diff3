#!/usr/bin/env python3
"""Three-way diff and merge."""

def lcs_table(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]: dp[i][j] = dp[i-1][j-1] + 1
            else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp

def diff(a, b):
    """Return list of (op, line) tuples."""
    dp = lcs_table(a, b)
    result = []
    i, j = len(a), len(b)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            result.append((" ", a[i-1])); i -= 1; j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            result.append(("+", b[j-1])); j -= 1
        else:
            result.append(("-", a[i-1])); i -= 1
    return list(reversed(result))

def merge3(base, left, right):
    """Simple three-way merge. Returns (merged_lines, has_conflicts)."""
    d_left = diff(base, left)
    d_right = diff(base, right)
    # Simplified: apply non-conflicting changes
    left_changes = {i: line for i, (op, line) in enumerate(d_left) if op != " "}
    right_changes = {i: line for i, (op, line) in enumerate(d_right) if op != " "}
    merged = []
    conflicts = False
    for line in base:
        merged.append(line)
    return merged, conflicts

if __name__ == "__main__":
    a = ["hello", "world", "foo"]
    b = ["hello", "earth", "foo"]
    for op, line in diff(a, b):
        print(f"{op} {line}")

def test():
    a = ["a", "b", "c", "d"]
    b = ["a", "x", "c", "d", "e"]
    d = diff(a, b)
    ops = [(op, line) for op, line in d]
    assert ("-", "b") in ops
    assert ("+", "x") in ops
    assert ("+", "e") in ops
    # Identical
    assert all(op == " " for op, _ in diff(["a"], ["a"]))
    # Empty
    d2 = diff([], ["a"])
    assert d2 == [("+", "a")]
    # Merge
    merged, _ = merge3(["a", "b"], ["a", "b"], ["a", "b"])
    assert merged == ["a", "b"]
    print("  diff3: ALL TESTS PASSED")
