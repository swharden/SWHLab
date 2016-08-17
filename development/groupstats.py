# demonstrates how to pull data from a workbook dictionary (in a pickle file)
import pickle
import os


def note_to_groups(text,d={}):
    """
    given text from a note objet, return a groups dictionary.
    optionally give this a dictionary to add to.
    if text is a .txt filename, load its contents.
    """
    if text.endswith(".txt") and os.path.exists(text):
        with open(text) as f:
            text=f.read()
    text=text.split("\n")
    currentGroup=["NOTES MUST START WITH A GROUP"]
    for line in text:
        if len(line)<3 or line.startswith("#"):
            continue
        line=line.upper()
        if line.startswith("GROUP:"):
            currentGroup=line.replace("GROUP:","").strip()
        else:
            if not currentGroup in d.keys():
                d[currentGroup]=[]
            d[currentGroup]=d[currentGroup]+[line.strip()]
    return d
    
if __name__=="__main__":
    
    colName="iHold"
    
    # we aren't in origin, so simulate having access to groups and a worksheet
    groups=note_to_groups("groups.txt")    
    d=pickle.load(open("collected.pkl","rb"))
    dBook=d['name'] # this will always be the name of the workbook
    dSheets=list(d.keys()) # name of all sheets in the workbook
    dSheets.remove('name') # find a more idiomatic way to do this
    dSheetName=dSheets[0] # select the first worksheet of our workbook
    dSheet=d[dSheetName] # now dSheet is the dictionary with all the data

    # make groups from the sheets we have in the selected workbook
    groups_sheets={} # this will contain all sheets we will work on
    for sheet in dSheet["comments"]: # each column is a sheet name
        for group in groups:
            if sheet.split("_")[0] in groups[group]:
                if not group in groups_sheets.keys():
                    groups_sheets[group]=[]
                groups_sheets[group]=groups_sheets[group]+[sheet]
    
    # generate some commands to do what we want
    for group in groups_sheets:
        cmd='sc getgroup %s %s %s [%s]'%(dBook,dSheetName,colName,
                                    ", ".join(groups_sheets[group]))
        print("\n"+cmd+"\nccave;")
    print("\nsc ccaveCollect;")
