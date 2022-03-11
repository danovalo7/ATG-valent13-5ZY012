from time import time as t
from sys import getsizeof as gso
from random import shuffle
def tst(nnn):
    arr = list(range(1, nnn))
    shuffle(arr)
    x = {}
    t0 = t()
    for i in arr:
        x[i] = {"lol": "spam", "fock": "shit"}
    t1 = t()
    for i in arr:
        if x[i]["lol"] != "spam" or x[i]["fock"] != "shit":
            print("excuse me what the fuck")
    t2 = t()
    xs = gso(x)
    y = []
    t3 = t()
    for i in arr:
        while len(y) < i:
            y.append(None)
        if len(y) > i:
            y[i] = ["spam", "shit"]
        else:
            y.append(["spam", "shit"])
    t4= t()
    for i in arr:
        if y[i][0] != "spam" or y[i][1] != "shit":
            print("what in the goddam")
    t5 = t()
    ys = gso(y)
    dw = round(t1-t0, 15)
    dr = round(t2-t1, 15)
    lw = round(t4-t3, 15)
    lr = round(t5-t4, 15)
    print("dict: write=" + str(dw).ljust(17, "0") + ", read=" + str(dr).ljust(17, "0") + ", size=" + str(xs))
    print("list: write=" + str(lw).ljust(17, "0") + ", read=" + str(lr).ljust(17, "0") + ", size=" + str(ys))
    print("diff:")
    dd = {True: "dict", False: "list"}
    try:
        print(dd[dw<lw] + " writes faster by " + str(round(abs(dw-lw)/max(dw,lw)*100, 4)) + "%")
    except ZeroDivisionError:
        print("write: no diff")
    try:
        print(dd[dr<lr] + " reads faster by  " + str(round(abs(dr-lr)/max(dr,lr)*100, 4)) + "%")
    except ZeroDivisionError:
        print("read: no diff")
    return dw, dr, lw, lr


if __name__ == "__main__":
    tdw = 0
    tdr = 0
    tlw = 0
    tlr = 0
    ii = 0
    asdl = [5, 2]
    nnnn = 10
    try:
        while True:
            print(nnnn)
            res = tst(nnnn)
            tdw += res[0]
            tdr += res[1]
            tlw += res[2]
            tlr += res[3]
            nnnn *= asdl[ii % 2]
            ii += 1
            if nnnn > 5000000:
                ii = 0
                nnnn = 10
    except KeyboardInterrupt:
        print("totals: ")
        print("dict: write=" + str(tdw).ljust(17, "0") + ", read=" + str(tdr).ljust(17, "0"))
        print("list: write=" + str(tlw).ljust(17, "0") + ", read=" + str(tlr).ljust(17, "0"))
        dd = {True: "dict", False: "list"}
        print(dd[tdw<tlw] + " writes faster by " + str(round(abs(tdw-tlw)/max(tdw,tlw)*100, 4)) + "%")
        print(dd[tdr<tlr] + "  reads faster by " + str(round(abs(tdr-tlr)/max(tdr,tlr)*100, 4)) + "%")
        
    
