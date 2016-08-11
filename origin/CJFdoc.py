"""
generates quick and dirty documentation of a C file with HTML output.
To be documented, a function must start on a new line and not be indented.
"""

import glob
import os
import time
import sys

TEMPLATE="""<html>
<head>
<style>
body{font-family: Verdana, Geneva, sans-serif;line-height: 150%;}
a {color: blue; text-decoration: none;}
a:visited {color: blue;}
a:hover {text-decoration: underline;}
.func{font-size: 150%; font-weight: bold; border: solid 1px #CCCCCC;
     padding-left:5px;padding-right:5px;background-color:#EEEEEE;}
.command {color: gray; font-family: monospace;}
.comment {color: blue;}
</style>
</head>
<body>
CONTENT
</body>
</html>
"""

def removeBetween(s,bound1="{",bound2="}"):
    s=s.split(bound1)
    for i,line in enumerate(s):
        if bound2 in line:
            s[i]=line.split(bound2)[-1]
        else:
            s[i]=line
    return "".join(s)

def removeSlashes(s):
    s=s.split("\n")
    for i,line in enumerate(s):
        if "//" in line:
            s[i]=line.split("//")[0]
    return "\n".join(s)

def getCode(s,matching):
    """return code starting from matching"""
    if not matching in s:
        matching=matching.replace(" (","(")
    if not matching in s:
        return "~WARNING~ did not find this in the code:"+matching
    s=s.split(matching)
    if len(s)>2:
        return "~WARNING~ indent this comment in the code:"+matching
    s=s[1].split("{",1)[1]
    level=1
    for i,c in enumerate(list(s)):
        if c=="{":
            level+=1
        if c=="}":
            level-=1
        #if "{" in s[:i] and level==0:
        if level==0:
            return s[:i]
    return s

def getParts(fname,d={}):
    """
    return a dictionary of parts for every function in a C file.
    if a dictionary is given, add to it.
    """
    with open(fname) as f:
        rawCode=f.read().replace("\t"," ").replace("\r","\n")
    raw=removeSlashes(rawCode)
    raw=removeBetween(raw,"{","}")
    raw=removeBetween(raw,"/*","*/")
    raw=raw.split("\n")
    for i,line in enumerate(raw):
        if len(line)<3 or line[0] in "*#{}\t\r\n ":
            continue
        if ';' in line or "::" in line:
            continue
        func,funcArgs=line.split(")")[0].split("(")
        func=func.strip()
        if not " " in func:
            func="voidNeeded "+func
        funcType,funcName=func.split(" ",1)
        if ">" in funcName:
            funcName=funcName.split(">")[1].strip()
        funcFile=os.path.basename(fname)
        funcCode=getCode(rawCode,"\n"+line.strip())
        d[funcName]=[funcName,funcArgs,funcType,funcFile,funcCode]
        #return d
    return d

def tohtml(s):
    s=s.replace("\t"," "*5).replace(" ","&nbsp;").replace("\n","<br>")
    return s

def codeToComment(s):
    """returns [comment,restOfSource] from a function"""
    lines=s.split("\n")
    level=0
    commentLine=0
    for i,line in enumerate(lines):
        if len(line)<3:
            continue
        if "//" in line:
            line=line.split("//")[0]
            continue
        if "/*" in line:
            level+=line.count("/*")
        if "*/" in line:
            level-=line.count("*/")
        if level>0:
            continue
        commentLine=i
        break
    return "\n".join(lines[:commentLine]),"\n".join(lines[commentLine:])

def gendocDebug(d,fname="CJF_doc_debug.html"):
    html=""
    for key in sorted(d.keys()):
        funcName,funcArgs,funcType,funcFile,funcCode=d[key]
        html+="<hr>"
        html+="<h3>%s</h3>"%funcName
        html+="<code>%s %s(%s)</code><br>"%(funcType,funcName,funcArgs)
        html+='<code style="color:green;">%s</code><br>'%funcFile
        commentCode,restOfCode=codeToComment(funcCode)
        html+='<code style="color:blue;">%s</code><br>'%tohtml(commentCode)
        html+='<code style="color:red;">%s</code>'%tohtml(restOfCode)
    with open(fname,'w') as f:
        f.write(TEMPLATE.replace("CONTENT",html))

def cleanComment(s):
    s=s.replace("//**","").replace("//","")
    s=s.replace("/*","").replace("*/","")
    return s

def gendocRegular(d,fname="CJF_doc.html",requireDoc=False):
    if requireDoc:
        for key in sorted(list(d.keys())):
            funcName,funcArgs,funcType,funcFile,funcCode=d[key]
            commentCode,restOfCode=codeToComment(funcCode)
            if len(commentCode)<3:
                del d[key]
    html="<h1>CJFLab Command Reference</h1>"
    html+="<i>generated %s</i><br><br>"%time.strftime("%b %d, %Y", time.localtime())
    for key in sorted(d.keys()):
        html+='<a href="#%s">%s</a>, '%(key,key)
    html=html[:-2] # cut off the last comma
    html+="<br><hr><br>"
    for key in sorted(d.keys()):
        funcName,funcArgs,funcType,funcFile,funcCode=d[key]
        html+='<br><a name="%s"></a>'%key
        html+='<code class="func">%s</code><br>'%funcName
        html+='<span class="command">%s %s(%s)</span><br>'%(funcType,funcName,funcArgs)
        commentCode,restOfCode=codeToComment(funcCode)
        html+='<span class="comment">%s</span><br>'%tohtml(cleanComment(commentCode))
    with open(fname,'w') as f:
        f.write(TEMPLATE.replace("CONTENT",html))
    return

def documentOriginCfolder(folder,debug=False):
    if not os.path.exists(folder):
        print(folder,"does not exist!")
        return
    d={}
    for fname in glob.glob(folder+"/*.c"):
        d=getParts(fname,d)
    if debug:
        gendocDebug(d,folder+"/CJF_doc_debug.html")
    gendocRegular(d,folder+"/CJF_doc.html")
    gendocRegular(d,folder+"/CJF_doc_limited.html",True)

if __name__=="__main__":
    print("DONT RUN THIS DIRECTLY.")
    documentOriginCfolder(r"X:\Software\OriginC\On-line\OriginPro 2016")

