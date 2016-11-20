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
    install_requires=[
       'neo>=0.4.1',
       'webinspect>=0.2.8',
       'matplotlib>=1.3.1',
       'numpy>=1.8.1',
       'pillow>=3.4.2',
    ],
    platforms='any',
    description='Tools to analyze electrophysiological data from ABF files',
    long_description=open("README.md").readlines()[1],
    keywords="""electrophysiology patch clamp neurophysiology ABF spike 
    action potential EPSC IPSC event detection""",
    classifiers=[
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    ],
)