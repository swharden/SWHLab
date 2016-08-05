fname="../../PyOrigin/__init__.py"
with open(fname) as f:
    raw=f.read()
raw=raw.replace(":",":\n")
raw=raw.replace("\t"," ")
baseMethods=[]
classes=[]
classMethods={}
lastClass=None
for line in raw.split("\n"):
    firstword=line.strip().split(" ",1)[0]
    if not firstword in ['def','class']:
        continue
    if "__" in line or "swig_" in line or " _" in line:
        continue
    thingName=line.strip().split(" ",1)[1].replace(":",'')
    line=line.split(":")[0]
    if firstword=='class':
        lastClass=thingName
        classes.append(thingName)
        classMethods[lastClass]=[]
    if line.startswith("def"):
        lastClass='base'
        baseMethods.append(line.replace("def ",''))
    else:
        if "class " in line:
            continue
        line=line.strip().replace("def ",'')
        classMethods[lastClass]=classMethods[lastClass]+[line]

def linkClass(name):
    url="http://www.originlab.com/doc/python/PyOrigin/Classes/"
    #url="http://www.originlab.com/doc/OriginC/ref/"
    nick=name.replace("CPy","").split("(")[0]
    return '<a href="%s">%s</a>'%(url+nick,name)

def linkMethod(name):
    url="http://www.originlab.com/doc/python/PyOrigin/Global-Functions/"
    #url="http://www.originlab.com/doc/OriginC/ref/"
    nick=name.replace("CPy","").split("(")[0]
    return '<a href="%s">%s</a>'%(url+nick,name)

html="""<html><head><style>
.parent{}
.child{color:gray;}
a {text-decoration: none;color: blue;}
a:hover {text-decoration: underline;color: blue;}
a:visited {color: blue;}
</style></head><body>
<h1>Missing PyOrigin Documentation</h1>
<i>A lot of these links don't work... but some do!</i>
<br><br><code>
<hr>"""


html+="<h2>PyOrigin Methods</h2>"
for name in sorted(baseMethods):
    html+='<span class="parent">PyOrigin.%s</span><br>'%linkMethod(name)
html+="<br><hr>"


html+="<h2>PyOrigin Classes</h2>"
for name in sorted(classes):
    html+='<span class="parent">PyOrigin.%s</span><br>'%linkClass(name)
html+="<br><hr>"


html+="<h2>PyOrigin Classes (extended)</h2>"
for name in sorted(classes):
    html+='<br><span class="parent">PyOrigin.%s</span><br>'%linkClass(name)
    for name2 in sorted(classMethods[name]):
        html+='<span class="child">PyOrigin.%s.%s</span><br>'%(name,name2)

html+="</code></body></html>"
with open("PyOrigin.html",'w') as f:
    f.write(html)
print("DONE")