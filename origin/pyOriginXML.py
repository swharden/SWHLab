"""
PyOriginXML and OriginXML class.
This script is a collection of tools to provide easy python access to OriginLab
tree objects. PyOrigin may be used one day, but for now Tree.Save and Tree.Load
are standard OriginC features which convert between origin tree objects and
XML strings. This python module can access vaues and delicately change them
while preserving the strict structure Origin needs to re-load it into the same
tree object. There are numerous modules that do XML object manipulation, but
this one is made with Origin in mind and is extremely careful to preserve
all formatting.

    * XML=OriginXML(thing) initiates the xml object
        * if thing is an XML string, it will parse it
        * if thing is a path to a file on the disk, it will pull its contents
    * XML.keys() lists keys
        * keys are the names of all parent objects for a value
        * with "<a><b><c>d</c></b></a>" the key "a.b.c" is value "d"
    * XML.value(key) returns the value of key
    * XML.set("a.b.c") sets the value of key to "this"
        * you can't create notes by assigning values to nonexistant keys
        * this is intentional, to preserve the precise data structure
    * return XML string (or save to file) with XML.toString()

http://www.originlab.com/doc/OriginC/ref/Tree-Save
http://www.originlab.com/doc/OriginC/ref/Tree-Load
"""

import os

#TODO: what happens if < makes it in a string?

class OriginXML():
    def __init__(self,xml):
        """Initiate with a string or XML file path."""
        if "<" in xml:
            print("initializing with XML from string")
            self.path=None
            self.PREFIX="OriginStorage."
        else:
            self.PREFIX="?xml.OriginStorage."
            self.path=os.path.abspath(xml)
            print("loading XML from:",self.path)
            if os.path.exists(xml):
                with open(xml) as f:
                    xml=f.read()
            else:
                print("ERROR! path not found:",xml)
                return
        print("xml input string is %d bytes"%len(xml))
        if not "OriginStorage" in xml:
            print("WARNING: this doesn't look like an origin tree!")
        xml=xml.replace("<","\n<").split("\n")
        for pos,line in enumerate(xml):
            if not line.startswith("<") and len(line):
                #TODO: this line has a linebreak in it! What do we do?
                pass
        self.values={} #values[key]=[line,value]
        levels=[]
        for pos,line in enumerate(xml):
            if not ("<" in line and ">" in line):
                continue
            line=line.replace(">"," >",1)
            name=line.split(" ",1)[0][1:].replace(">","")
            val=line.split(">")[1]
            if not len(val):
                val=None
            if line.startswith("</"):
                levels.pop()
            elif line.startswith("<"):
                levels.append(name)
                key=".".join(levels)
                if ("/>") in line:
                    levels.pop()
            else:
                print("I DONT KNOW WHAT TO DO WITH THIS LINE")
                print(pos,line,"=",val)
            if val is None:
                continue
            #print(">>",pos,key,val)
            self.values[key]=[pos,val]
        self.xml=xml
        print("xml now has %d lines and %d keys"%(len(self.xml),len(self.values.keys())))

    def save(self):
        """if XML was initiated with a filename, write it back to that file."""
        if not self.path:
            print("XML object wasn't initiated with a filename!")
            return
        self.toString(saveAs=self.path)

    def keysShow(self,matching=False,html=False):
        """show all of the keys and their values in a pretty formatted way."""
        out=""
        for key in sorted(list(self.values.keys())):
            if matching and not matching in key:
                continue
            out+="%s = %s\n"%(key.replace(self.PREFIX,""),self.values[key][1])
        if html:
            out=out.replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
            out="<html><body><code>%s</code></body></html>"%out
        else:
            print(out)
        return out

    def keys(self):
        """return a list of all available keys from the XML"""
        return sorted(list(self.values.keys()))

    def value(self,key):
        """given a key, return its value from the XML"""
        if not key in self.values.keys():
            if self.PREFIX+key in self.values.keys():
                key=self.PREFIX+key
            else:
                print("key [%s] is not in the XML keys"%key)
                return None
        pos,val=self.values[key]
        return val

    def use(self,matching,use=True):
        """
        Mark an item as used or unused.
        An unused item is grayed in the origin tree browser.
        """
        for i,line in enumerate(self.xml):
            if matching in line:
                if use:
                    self.xml[i]=self.xml[i].replace('Use="0"','Use="1"')
                else:
                    self.xml[i]=self.xml[i].replace('Use="1"','Use="0"')
                print("setting use of XML line %d matching %s to %s"%(i,matching,str(use)))

    def set(self,key,newVal):
        """given a key, set its value"""
        if not key in self.values.keys():
            if self.PREFIX+key in self.values.keys():
                key=self.PREFIX+key
            else:
                print("key [%s] is not in the XML keys"%key)
                return None
        newVal=str(newVal) #everything in an xml string is a string
        pos,oldVal=self.values[key]
        val=self.xml[pos].split(">")[-1]
        line=self.xml[pos][:-len(val)]+newVal
        if oldVal==newVal or oldVal+"."==newVal:
            print('    "%s" left at %s'%(key,oldVal))
            return
        self.xml[pos]=line
        self.values[key]=pos,newVal
        print(' -> "%s" changed from %s to %s'%(key,oldVal,newVal))

    def toString(self,saveAs=False):
        """return or save XML in the format Origin wants."""
        xml="".join(self.xml)
        print("xml output string is %d bytes"%len(xml))
        if type(saveAs) == str:
            with open(saveAs,'w') as f:
                f.write(xml)
            print(" -- saved XML to:",saveAs)
        return xml

def updateTree(fnameOLD,fnameNEW):
    """Pull values from an old XML tree file into a new XML tree file."""
    XMLOLD,XMLNEW=OriginXML(fnameOLD),OriginXML(fnameNEW)
    for key in XMLOLD.keys():
        if key in XMLNEW.keys():
            XMLNEW.set(key,XMLOLD.value(key))
    return XMLNEW.toString(XMLNEW.path)

if __name__=="__main__":
    print("do not run this program directly")
