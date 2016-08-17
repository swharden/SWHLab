# demonstrates how to pull data from a workbook dictionary (in a pickle file)
import pickle

if __name__=="__main__":
    d=pickle.load(open("collected.pkl","rb"))
    print("\n\nWORKBOOK:\n",d[list(d.keys())[0]]) # the first key is always the workbook name
    print("\n\nWORKSHEETS:\n",list(d.keys())[1:]) # all other keys are worksheet names
    sheet=d[list(d.keys())[1]] # select the first sheet
    print("\n\nSHEET PROPERTIES:\n",list(sheet.keys())) # all sheets have the same stuff
    print("\n\nnames:\n",sheet["comments"]) # cell identifiers are stuck here
    print("\n\ndata:\n",sheet["data"])