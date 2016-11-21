#from distutils.core import setup
from setuptools import setup

__counter__=53
__release__=''
__version__='0.1.%03d'%__counter__+__release__

setup(
    name='swhlab',
    version=__version__,
    author='Scott W Harden',
    author_email='SWHarden@gmail.com',
    packages=['swhlab'],
    url='https://github.com/swharden/swhlab',
    license='MIT License',
    platforms='any',
    description='Tools to analyze electrophysiological data from ABF files',
    long_description=open("README.md").readlines()[1],
    keywords="""electrophysiology patch clamp neurophysiology ABF spike 
    action potential EPSC IPSC event detection""",
    install_requires=[
       'neo>=0.4.1',
       'webinspect>=0.2.8',
       'matplotlib>=1.3.1',
       'numpy>=1.8.1',
       'pillow>=3.4.2',
    ],    
)

