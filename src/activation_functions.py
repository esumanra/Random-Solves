# A--> B, C
# B---> D, E
# E---> G

# C----> F


def getImmediateChildren(inp):
    return ["List of immediate Children"]


def getAllChildren(inp_url):
    res = list()
    temp = list()
    temp = getImmediateChildren(inp_url)

    if not temp:  # temp is None or empty list
        return

    for url in temp:  # [D, E]
        res.append(url)
        getAllChildren(url)
    return res
