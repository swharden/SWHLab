"""
intentionally crash (ZeroDivisionError)
"""
for i in range(3,-5,-1):
    if i>0:
        print("%d..."%(i))
    else:
        print("BOOM!")
    x=1/i