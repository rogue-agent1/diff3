#!/usr/bin/env python3
"""Three-Way Diff - Merge changes from two branches against a common ancestor."""
import sys

def lcs_table(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = dp[i-1][j-1]+1 if a[i-1]==b[j-1] else max(dp[i-1][j], dp[i][j-1])
    return dp

def diff(a, b):
    dp = lcs_table(a, b); ops = []; i, j = len(a), len(b)
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]: ops.append(("equal", a[i-1])); i -= 1; j -= 1
        elif dp[i-1][j] >= dp[i][j-1]: ops.append(("delete", a[i-1])); i -= 1
        else: ops.append(("insert", b[j-1])); j -= 1
    while i > 0: ops.append(("delete", a[i-1])); i -= 1
    while j > 0: ops.append(("insert", b[j-1])); j -= 1
    return list(reversed(ops))

def merge3(base, left, right):
    dl = diff(base, left); dr = diff(base, right)
    result = []; conflicts = 0
    li = ri = 0
    while li < len(dl) or ri < len(dr):
        lo = dl[li] if li < len(dl) else None
        ro = dr[ri] if ri < len(dr) else None
        if lo and ro and lo[0] == "equal" and ro[0] == "equal":
            result.append(lo[1]); li += 1; ri += 1
        elif lo and lo[0] == "insert":
            result.append(lo[1]); li += 1
        elif ro and ro[0] == "insert":
            result.append(ro[1]); ri += 1
        elif lo and lo[0] == "delete" and ro and ro[0] == "delete":
            li += 1; ri += 1
        elif lo and lo[0] == "delete":
            li += 1; ri += 1
        elif ro and ro[0] == "delete":
            li += 1; ri += 1
        else:
            result.append(f"<<<<<<< LEFT"); 
            if lo: result.append(lo[1])
            result.append("=======")
            if ro: result.append(ro[1])
            result.append(">>>>>>> RIGHT")
            conflicts += 1; li += 1; ri += 1
    return result, conflicts

def main():
    if len(sys.argv) == 4:
        files = [open(f).read().splitlines() for f in sys.argv[1:4]]
        result, conflicts = merge3(*files)
        print("\n".join(result))
        if conflicts: print(f"\n{conflicts} conflict(s)", file=sys.stderr)
    else:
        base = ["line1", "line2", "line3", "line4", "line5"]
        left = ["line1", "modified2", "line3", "new_left", "line4", "line5"]
        right = ["line1", "line2", "changed3", "line4", "line5", "added_right"]
        print("=== Three-Way Merge ===\n")
        print(f"Base:  {base}"); print(f"Left:  {left}"); print(f"Right: {right}")
        result, conflicts = merge3(base, left, right)
        print(f"\nMerged ({conflicts} conflicts):"); 
        for line in result: print(f"  {line}")

if __name__ == "__main__":
    main()
