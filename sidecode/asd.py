from timeit import timeit, repeat
from itertools import filterfalse, count, chain

def remapp(nodes, paths):
    z = {node: [node] for node in nodes}
    k = {node: [node] for node in nodes}
    npaths = []
    for path in paths:
        npaths.append([z[path[0]], k[path[1]]])
    for _ in range(100):
        z[0][0] = 1001
        k[1][0] = 1002
    return [tuple(chain.from_iterable(path)) for path in npaths]
    return *(tuple(chain.from_iterable(path)) for path in npaths),

def zxc(nodes, paths):
    npaths = [list(path) for path in paths]
    for _ in range(100):
        for path in npaths:
            if path[0] == 0:
                path[0] = 1001
            if path[1] == 1:
                path[1] = 1002
    return tuple(tuple(path) for path in npaths)

    
paths = tuple([(i//3,i+1) for i in range(1000)])
nodes = tuple([i for i in range(1001)])

#print(timeit("remapp(nodes, paths)", globals=globals(), number=100))
#print(timeit("zxc(nodes, paths)", globals=globals(), number=100))
#print(remapp(nodes, paths) == zxc(nodes, paths))
def lol():
    n = False
    for i in range(10000):
        if n == False:
            n = True
def lolz():
    n = False
    for i in range(10000):
        n = True

print(remapp(nodes, paths))
print(timeit(lol, globals=globals(), number=1000))
print(timeit(lolz, globals=globals(), number=1000))

