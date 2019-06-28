# A--> B, C
# B---> D, E
# E---> G
# C----> F

url_list = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'E': ['G'],
    'C': ['F']
}

def getImmediateChildren(inp):
    return url_list.get(inp, None)

def getAllChildren(inp_url, res=[]):
    temp = list()
    temp = getImmediateChildren(inp_url)

    if not temp:  # temp is None or empty list
        return

    for url in temp:
        res.append(url)
        getAllChildren(url, res)
    return res

ans = getAllChildren('A')
print(ans)
