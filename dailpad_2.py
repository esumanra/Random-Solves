def solve(N):
    # Write your code here
    d = dict()
    l = list()
    possib = 0
    for ele in N:
        if ele not in l:
            l.append(ele)
        d[ele] = 1 + d.get(ele, 0)
    print(l)
    print(str(d))
    for i in range(1, 9):
        m = str(i)
        n = str(i+1)
        if d.get(m, 0) and d.get(m, 0) >= 2 and d.get(n, 0) >= 2 and l.index(m) < l.index(n):
            if d.get(m) == 2 and d.get(n) == 2:
                possib += 1
            elif d.get(m) > 2 and d.get(n) == 2:
                possib += d.get(m)
            elif d.get(n) > 2 and d.get(m) == 2:
                possib += d.get(n)
            else:
                possib += d.get(m) * d.get(n)
        else:
            continue
    return possib


N = "1351355246246"
out_ = solve(N)
print(out_)
