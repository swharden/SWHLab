"""run this to see if the swhlab your interpreter is using lives in this
folder, or if it's installed on the system. For developing, I recommend
having it not installed on the system, but rather adding the ../ path to
your PYTHONPATH just for the python session you're debugging in."""

import os

def test_importing():
    """Try loading swhlab. Returns False if crashes."""
    try:
        from tests import swhlab
        print("imported SWHLab version",swhlab.__version__)
    except:
        print("importing swhlab FAILED")
        print("add this to your development environment PYTHONPATH:")
        print(os.path.abspath(os.path.dirname(__file__)+"/../"))
        
        return False
    swhlabLivesAt=swhlab.__file__
    #print("I live at:",__file__)
    rel=os.path.relpath(swhlabLivesAt,__file__)
    if "site-packages" in rel:
        print("WARNING: USING SYSTEM SWHLAB NOT THIS ONE")
        print("swhlab module lives at:",rel)
    else:
        print("imported locally (not site-packages)")
    return
    
if __name__=="__main__":
    test_importing()