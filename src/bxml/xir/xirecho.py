#!/usr/bin/env python

"""
  This is a quick/dirty front-end to read an XIR file and display a terse representation of
  each record in a human readable form.
  
  This example also demonstrates how to set up your own XIRContentHandler (using the provided
  Adapter class) to consume a stream of XIR records.
"""

import sys
import string
import types

from xir.parser import XIRParser, XIRContentHandlerAdapter, XIRReader

class EchoHandler(XIRContentHandlerAdapter):
    def __init__(self):
        self.tab = 0
        
    def output(self, text):
        print " " * self.tab + text
        
    def startDocument(self):
        self.output("document begin")
    
    def endDocument(self):
        self.output("document end")
    
    def startPrefix(self, nsPrefix, nsURI):
        self.output("prefix begin %s=%s" % (nsPrefix, nsURI))
    
    def endPrefix(self, nsPrefix, nsURI):
        self.output("prefix end %s=%s" % (nsPrefix, nsURI))
    
    def startElement(self, nsURI, name, numberOfAttrs):
        self.indent()
        self.output("element begin %s:%s (%s attributes)" % (nsURI, name, numberOfAttrs))
    
    def endElement(self, nsURI, name):
        self.dedent()
        self.output("element end %s:%s" % (nsURI, name))
        
    def attribute(self, nsURI, name, value):
        self.output("+attribute %s:%s=%s" % (nsURI, name, value))
    
    def characters(self, length, cdata):
        self.output("characters %s" % repr(cdata))
        
    def whitespace(self, length, cdata):
        self.output("whitespace %s" % repr(cdata))
    
    def indent(self):
        self.tab += 1
        
    def dedent(self):
        self.tab -= 1
        
    def skippedEntity(self, name):
        pass
    
    def processingInstruction(self, name, target):
        pass

def main():
    xir_file = sys.argv[1]
    f = open(xir_file)
    xirReader = XIRReader(f)
    echoHandler = EchoHandler()
    xirParser = XIRParser(xirReader, echoHandler)
    xirParser.parse()

if __name__ == '__main__':
    main()