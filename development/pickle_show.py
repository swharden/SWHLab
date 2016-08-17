# demonstrates how to pull data from a workbook dictionary (in a pickle file)
import pickle

if __name__=="__main__":
    d=pickle.load(open("collected.pkl","rb"))
    print("\n\nWORKBOOK:\n",d['name']) # this is always the workbook name
    sheets=list(d.keys()) #TODO: find a more idiomatic way of doing this
    sheets.remove('name') #TODO: find a more idiomatic way of doing this
    print("\n\nWORKSHEETS:\n",sheets) # all other keys are worksheet names
    sheet=d[sheets[0]] # select the first worksheet
    print("\n\nSHEET PROPERTIES:\n",list(sheet.keys())) # all sheets have the same stuff
    print("\n\nsheet names:\n",sheet["comments"]) # cell identifiers are stuck here
    print("\n\ndata:\n",sheet["data"])