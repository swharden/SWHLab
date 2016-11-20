import time
if __name__=="__main__":
    with open('swhlab/version.py') as f:
        raw=f.read().split("\n")
        for i,line in enumerate(raw):
            if line.startswith("__counter__"):
                version = int(line.split("=")[1])
                raw[i]="__counter__=%d"%(version+1)
    with open('swhlab/version.py','w') as f:
        f.write("\n".join(raw))
    print("upgraded from version %d to %d"%(version,version+1))