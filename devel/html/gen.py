import glob

fnames=sorted(glob.glob("*.jpg"))

print("\n\n<h1>DATA ANALYSIS</h1>")
print('\n'.join(['<img src="%s">'%x for x in fnames if x[8] == '_']))

print("\n\n<h1>FLUORESCENT</h1>")
print('\n'.join(['<img src="%s">'%x for x in fnames if x[8] == '-']))

print("\n\n<h1>OTHER</h1>")
print('\n'.join(['<img src="%s">'%x for x in fnames if x[8] not in "_-"]))