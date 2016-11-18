"""
misc code related to HTML generation and templating
"""

import tempfile
import webbrowser
import os
import common

stylesheet="""

body{
    font-family: sans-serif;
    }

a {text-decoration: none;}
a:link {text-decoration: none;}
a:visited {text-decoration: none;}
a:hover {text-decoration: underline;}

.credits{margin-top:100px; font-size: x-small; color: #ccc;}

.datapic{
    margin: 10px;
    border: 1px solid black;
    box-shadow: 5px 5px 10px grey;
    }
    
"""

html_top="""<html>
<head>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
"""

html_bot="""
<div class="credits" align="center">
<a class="credits" href="https://pypi.python.org/pypi/swhlab" target="_blank">SWHLab</a> ~GENAT~</div>
</body>
</html>
"""

stylesheetSaved=False # module global

def frames(fname=None,menuWidth=200,launch=False):
    """create and save a two column frames HTML file."""
    html="""
    <frameset cols="%dpx,*%%">
    <frame name="menu" src="index_menu.html">
    <frame name="content" src="index_splash.html">
    </frameset>"""%(menuWidth)
    with open(fname,'w') as f:
        f.write(html)
    if launch:
        webbrowser.open(fname)

def save(html,fname=None,launch=False):
    """wrap HTML in a top and bottom (with css) and save to disk."""
    html=html_top+html+html_bot
    html=html.replace("~GENAT~",common.datetimeToString())
    if fname is None:
        fname = tempfile.gettempdir()+"/temp.html"
        launch=True
    fname=os.path.abspath(fname)
    with open(fname,'w') as f:
        f.write(html)
    
    global stylesheetSaved
    stylesheetPath=os.path.join(os.path.dirname(fname),"style.css")
    if not os.path.exists(stylesheetPath) or stylesheetSaved is False:
        with open(stylesheetPath,'w') as f:
            f.write(stylesheet)
            stylesheetSaved=True
    if launch:
        webbrowser.open(fname)

if __name__=="__main__":
    save("<h3>don't run this directly!</h3>",launch=True)
    save("<h3>don't run this directly!</h3>",launch=True)