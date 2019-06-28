m = 2
s = 'aabbccaa' + '0'
l = []
d = {}
count = 1
count_2 = 0
ans = 0
for i in range(0, len(s)-1):
    if s[i] == s[i+1]:
        count += 1
    else:
        l.append((s[i], count))
        d[s[i]] = d.get(s[i], 0) + 1
        count = 1
# print(l)
# print(d)
for pair in l:
    k, v = pair
    if d[k] %2 == 0:
        ans += 1
print(ans)