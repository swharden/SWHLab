from distutils.core import setup

import swhlab

setup(
    name='swhlab',
    version=swhlab.__version__,
    author='Scott W Harden',
    author_email='SWHarden@gmail.com',
    packages=['swhlab'],
    url='https://github.com/swharden/swhlab',
    license='MIT License',
    description='Tools to analyze electrophysiological data from ABF files',
    long_description="""SWHLab is a collection of tools to provide easy access
to ABF files containing patch-clamp electrophysiology data. NeoIO provides
direct access to ABF data, and SWHLab makes it easy to perform high-level
operations (such as event detection, action potential characterization,
calculation of cell capacitance from voltage clamp or current clamp traces).
SWHLab intended to be used as a tool for neurophysiology data exploration, 
rather than production or presentation. It can be easily incorporated into
other projects where accessing ABF data is desired.""",
    install_requires=[
       'numpy',
       'matplotlib',
       'neo',
       'webinspect',
    ],
)