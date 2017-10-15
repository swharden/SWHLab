import os

def clampfit_rename(path,char):
    """
    Given ABFs and TIFs formatted long style, rename each of them to prefix their number with a different number.

    Example: 2017_10_11_0011.abf
    Becomes: 2017_10_11_?011.abf
    where ? can be any character.
    """
    assert len(char)==1 and type(char)==str, "replacement character must be a single character"
    assert os.path.exists(path), "path doesn't exist"
    files = sorted(os.listdir(path))
    files = [x for x in files if len(x)>18 and x[4]+x[7]+x[10]=='___']
    for fname in files:
        fname2 = list(fname)
        fname2[11]=char
        fname2="".join(fname2)

        if fname==fname2:
            print(fname, "==", fname2)
        else:
            print(fname, "->", fname2)
#            fname=os.path.join(path,fname)
#            fname2=os.path.join(path,fname2)
#            if not os.path.exists(fname2):
#                os.rename(fname,fname2)
    return

if __name__=="__main__":
    print("DO NOT RUN THIS DIRECTLY!")

    # rename Jeff's folder
    path=R"X:\Data\SCOTT\2017-10-10 BLA aging 2 jeff"
    char="1"
    clampfit_rename(path,char)
    #clampfit_rename(path+"/swhlab/",char)

    # rename Todd's folder
    path=R"X:\Data\SCOTT\2017-10-10 BLA aging 2 ts"
    char="2"
    clampfit_rename(path,char)
    #clampfit_rename(path+"/swhlab/",char)
