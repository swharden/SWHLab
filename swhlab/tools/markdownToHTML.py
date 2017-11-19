"""
The goal of this script is to provide a portable python module to allow markdown-to-html conversion
without and dependencies outside the python standard library.
"""

import os
import webbrowser

TEMPLATE="""<html>
<head>
<style>

body {
      //font-family: sans-serif;
}

code {
      color: #0000CC;
}

i {
      
}

h1 {
      font-family: sans-serif;
}

h2 {
      font-family: sans-serif;
      border-bottom: 1px solid #CCC;
      padding-top: 30px;
}

</style>
<body>
%CONTENT%
</body></html>
"""

TEXTCHARS=[]
TEXTCHARS.extend([chr(x) for x in range(48,58)]) # numbers
TEXTCHARS.extend([chr(x) for x in range(65,91)]) # uppercase
TEXTCHARS.extend([chr(x) for x in range(97,123)]) # lowercase

def lineMDtoHTML(s,charFind='`',htmlTag='code'):
    hitCount=0
    while charFind in s:

        # skip matches where the character appears mid-word        
        charPos = s.find(charFind)
        if charPos>0 and charPos<(len(s)-1):
            if s[charPos-1] in TEXTCHARS and s[charPos+1] in TEXTCHARS:
                s=s.replace(charFind,"MIDWORDCHARACTER",1)
                continue
        # replace the character with the html code
        tag="<%s>"%htmlTag
        if hitCount%2==1:
            tag=tag.replace("<","</")
        s=s.replace(charFind,tag,1)
        hitCount+=1
        
    # don't leave us hanging
    if hitCount%2==1:
        s+="</%s>"%htmlTag
        
    # fix the mid-word matches
    s=s.replace("MIDWORDCHARACTER",charFind)
    return s

def stringReplaceEveryOther(textblock,charFind,htmlTag):
    lines=textblock.split("\n")    
    for pos,line in enumerate(lines):
        lines[pos]=lineMDtoHTML(line,charFind,htmlTag)
    return "\n".join(lines)

def writeHTML(html,filename,launch=True):
    filename = os.path.abspath(filename)
    with open(filename,'w') as f:
        f.write(TEMPLATE.replace("%CONTENT%",html))
        print("wrote",filename)
    if launch:
        webbrowser.open(filename)

def markdownTextToHTML(markdown):
    
    markdown=stringReplaceEveryOther(markdown,'`','code')
    markdown=stringReplaceEveryOther(markdown,'_','i')
    markdown=stringReplaceEveryOther(markdown,'**','b')
    
    lines=markdown.split("\n")
    for lineNumber,line in enumerate(lines):        
        if line.startswith("#"):
            # it's a title
            for hashTagCount in range(7):
                if line.startswith("#"*hashTagCount) and line[hashTagCount]!="#":
                    line=line.strip("#").strip()
                    lines[lineNumber]="<h%d>%s</h%d>"%(hashTagCount,line,hashTagCount)
        elif line.strip().startswith("* "):
            # it's a bullet
            layersDeep=line.index('*')
            lines[lineNumber]="&nbsp;"*(layersDeep*5)+"&bull; "+line.replace("*","",1)+"<br>"
        elif line.strip()=="":
            if lineNumber>0 and "<h" in lines[lineNumber-1]:
                lines[lineNumber]="" # skip blank lines after titles
            else:
                lines[lineNumber]="<br>"
        else:
            lines[lineNumber]="<div>%s</div>"%line
    return "".join(lines)

def markdownFileToHTMLfile(fileMD, fileHTML=None, launch=True):
    fileMD=os.path.abspath(fileMD)
    if not fileHTML:
        fileHTML=fileMD+".html"
    markdown=open(fileMD).read()
    html=markdownTextToHTML(markdown)
    writeHTML(html,filename=fileHTML,launch=launch)

if __name__=="__main__":
    markdownFileToHTMLfile("commands.md")
    print("DONE")
