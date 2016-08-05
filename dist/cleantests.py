"""delete all test PNGs"""
import os
for root, dirs, files in os.walk("../tests/automated"):
    print("\n[%s]\n"%os.path.basename(root),end='')
    for fname in files:
        fname=os.path.join(root,fname)
        if fname.endswith(".png"):
            os.remove(fname)