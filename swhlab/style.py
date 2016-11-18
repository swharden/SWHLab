"""
misc code related to HTML generation and templating
"""

import time
import tempfile
import webbrowser
import os

html_top="""<html>
<head>
<style>
body{font-family: sans-serif;}
</style>
</head>
<body>
"""

html_bot="""
<div class="credits" align="center">~GENAT~</div>
</body>
</html>
"""

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
    html=html.replace("~GENAT~",str(time.time()))
    if fname is None:
        fname = tempfile.gettempdir()+"/temp.html"
        launch=True
    fname=os.path.abspath(fname)
    with open(fname,'w') as f:
        f.write(html)
    if launch:
        webbrowser.open(fname)

if __name__=="__main__":
    save("<h3>don't run this directly!</h3>",launch=True)