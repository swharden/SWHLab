import logging
#logLevel=logging.DEBUG
logLevel=logging.INFO
#logLevel=logging.ERROR
logDateFormat='%m/%d/%Y %I:%M:%S %p'
logFormat='%(asctime)s\t%(levelname)s\t%(message)s'

__counter__=51
__release__=''
__version__='0.1.%03d'%__counter__+__release__