import sys
import subprocess
import time
import glob
import os

PYTHONPATH = sys.executable
TESTPATH = os.path.abspath('./automated/')

HTML_TOP="""
<html><head><style>
hr {margin: 20px 0px 20px 0px; background-color: white; height: 1px; border: 0;}
body{background-color: #006699; color: white;}
.title{font-size: 150%%; font-weight: bold; margin: 10px;}
.subtitle {font-style: italic; display: block; margin-left: 10px;}
.testblock{border: 1px solid black; padding: 0px; margin: 0 25 50 25;
           box-shadow: 10px 10px 20px rgba(0,0,0,.5);
           background-color: white; color: black;}
code {display: block; padding: 2px;}
.output {background-color:black; color: white;}
.cmd {background-color:black; color: yellow; font-weight: bold;}
.pass {background-color:#68ff96;}
.error {background-color:#f9bbbb;}
.smallpic {height: 200px;box-shadow: 5px 5px 10px rgba(0,0,0,.5);
           border: 1px solid black; margin: 10px; padding: 5px;}
pre.prettyprint{width: auto;overflow: auto;max-height: 600px; margin: 10px;}
</style></head><body>
<script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js"></script>
<h1>Automated Test Routine</h1>
<code>PYTHON PATH: %s</code>
<code>TEST FILES: %s</code>
<br><br>
"""%(PYTHONPATH,TESTPATH)

HTML_TEST="""
<span class="title"><!--T--></span><br>
<span class="subtitle"><!--S--></span>
<pre class="prettyprint" style="background-color: #FAFAFA;"><!--C--></pre>
"""

def formatSource(fname,timeTook=0,output='',error=False):
    output=output.replace("\n","<br>").replace(" ","&nbsp;")
    command="&gt; %s %s"%(os.path.basename(PYTHONPATH),os.path.basename(fname))
    with open(fname) as f:
        code=f.read()
    docs='<span style="color: orange;">this script needs documentation!</span>'
    if code.count('"""')>=2:
        temp,docs,code=code.split('"""',2)
    html=HTML_TEST.replace("<!--T-->",fname.replace(TESTPATH,""))
    html=html.replace("<!--C-->",code)
    html=html.replace("<!--S-->",docs.strip().replace("\n","<br>"))
    for fname in glob.glob(fname+"*.png"):
        killThis=os.path.dirname(os.path.dirname(fname))
        fname="."+fname.replace(killThis,'').replace('\\','/')
        html+='<a href="%s"><img src="%s" class="smallpic"></a>'%(fname,fname)
    html+='<br><br>'
    html+='<code class="cmd">%s</code>'%(command)
    html+='<code class="output">%s</code>'%(output)
    if error:
        error=error.replace("\n","<br>")
        html+='<code class="error">%s</code>'%(error)
        html+='<code class="cmd">FAILED! execution time: %.03f sec</code>'%(timeTook)
    else:
        html+='<code class="pass">PASS. execution time: %.03f sec</code>'%(timeTook)
    html='<div class="testblock">%s</div>'%html
    return html


def testScript(scriptPath):
    """given the path to a python script, run it and return details."""
    p=subprocess.Popen([PYTHONPATH,scriptPath],cwd=os.path.dirname(scriptPath),
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeTook=time.clock()
    output,error=p.communicate()
    timeTook=time.clock()-timeTook
    output=output.decode("utf-8").replace("\r","").replace(r'\n','\n').strip()
    error=error.decode("utf-8").replace("\r","").replace(r'\n','\n').strip()
    return output,error,timeTook

if __name__=="__main__":
    html=HTML_TOP
    for item in sorted(glob.glob(TESTPATH+"/*")):
        if not "." in item:
            recentDirName=item
    if "recent" in str(sys.argv):
        print("only running tests in:",recentDirName)
    else:
        print("running all tests in all folders.")
    for root, dirs, files in os.walk(TESTPATH):
        print("\n[%s]\n"%os.path.basename(root),end='')
        for fname in files:
            fname=os.path.join(root,fname)
            if fname.endswith(".png"):
                os.remove(fname)
        for fname in files:
            fname=os.path.join(root,fname)
            if "recent" in str(sys.argv):
                if not recentDirName in fname:
                    continue
            if not fname.endswith(".py"):
                continue
            output,error,timeTook=testScript(fname)
            html+=formatSource(fname,timeTook,output,error)
            if error:
                print("F",end='')
            else:
                print(".",end='')
        print()
    html+="</body></html>"
    with open("./automated/index.html",'w') as f:
        f.write(html)
    print("DONE")