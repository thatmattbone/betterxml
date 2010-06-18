#!/usr/bin/env python

"""
  This is a quick/dirty (to be expanded) front-end to translate an XML file into XIR.
"""

import sys
import string
import types

from xml.sax import make_parser
from xml.sax import handler

from xir.sax2 import Sax2XIR

def main():
    xirHandler = Sax2XIR(sys.stdout)
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(xirHandler)
    parser.setErrorHandler(xirHandler)
    document_file = sys.argv[1]
    f = open(document_file)
    parser.parse(f)
    f.close()
    
if __name__ == '__main__':
    main()