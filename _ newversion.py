if __name__=="__main__":
    version=None
    fname='./swhlab/version.py'
    with open(fname) as f:
        raw=f.read().split("\n")
        for i,line in enumerate(raw):
            if line.startswith("__counter__"):
                if version is None:
                    version = int(line.split("=")[1])
                raw[i]="__counter__=%d"%(version+1)
    with open(fname,'w') as f:
        f.write("\n".join(raw))
    print("upgraded from version %03d to %03d"%(version,version+1))