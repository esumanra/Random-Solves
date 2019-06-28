from itertools import permutations, combinations
import math

def nCr(n,r):
    f = math.factorial
    return f(n) // f(n-r)
a = [1,1,2,2,3]
pair = {}
unique = 0
for k in a:
    if k in pair:
        pair[k] += 1
    else:
        pair[k] = 1
        unique += 1
repeat = len(a) - unique
combs = nCr(unique, 2)
print(combs)
