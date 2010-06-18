"""
A SAX2 Handler to generate an XIR record stream from an incoming XML document.
"""

import string
import sys

from xir.xdo import XIRDataObject
from xml.sax.handler import ContentHandler, ErrorHandler


class Sax2XIR(ContentHandler, ErrorHandler):

    def __init__(self, stream=sys.stdout):
        self.locator = None
        self.uri_map = {}
        self.prefix_map = {}
        self.context = []
        self.stream = stream
        
    def write(self, xir):
        self.stream.write(str(xir))
        self.stream.write('\n')
        
    def setDocumentLocator(self, locator):
        self.locator = locator

    def startDocument(self):
        xir = XIRDataObject('document', 'begin')
        self.write(xir)
        
    def endDocument(self):
        xir = XIRDataObject('document', 'end')
        self.write(xir)

    def startPrefixMapping(self, prefix, uri):
        xir = XIRDataObject('prefix', 'begin')
        xir.set_verbatim('prefix', prefix)
        xir.set_verbatim('uri', uri)
        self.write(xir)
        self.uri_map[prefix] = uri

    def endPrefixMapping(self, prefix):
        uri = self.uri_map[prefix]
        xir = XIRDataObject('prefix', 'end')
        xir.set_verbatim('prefix', prefix)
        xir.set_verbatim('uri', uri)
        self.write(xir)
        del(self.uri_map[prefix])


    def startElementNS(self, name, qname, attrs):
        element_xir = XIRDataObject('element', 'begin')
        element_xir.set_verbatim('attributes', len(attrs))
        element_xir.set_verbatim('ns', name[0])
        element_xir.set_verbatim('name', name[1])
        self.write(element_xir)
 
        for attr in attrs.getNames():
            attribute_xir = XIRDataObject('a', 'singleton')
            (ns, n) = attr
            if ns == None:
                ns = name[0]
            if ns == u'xmlns' and n not in self.uri_map.keys():
                self.uri_map[n] = attrs.getValueByQName(attr)
            else:
                attribute_xir.set_verbatim('ns', ns)
                attribute_xir.set_verbatim('name', n)
                attribute_xir.set_verbatim('value', attrs.getValue(attr))
            self.write(attribute_xir)
            
        self.context.append( (name, self.uri_map.copy()) )

    def endElementNS(self, name, qname):
        xir = XIRDataObject('element', 'end')
        xir.set_verbatim('ns', name[0])
        xir.set_verbatim('name', name[1])
        self.write(xir)
        (junk, self.uri_map) = self.context.pop()
        
    def characters(self, content):
        xir = XIRDataObject('characters')
        xir.set_base64('cdata', content)
        self.write(xir)
        
    def ignorableWhitespace(self, whitespace):
        xir = XIRDataObject('ws')
        xir.set_base64('cdata', whitespace)
        self.write(xir)
        
    def skippedEntity(self, name):
        xir = XIRDataObject('skipped-entity')
        xir.set_verbatim('name', name)
        self.write(xir)

    def processingInstruction(self, name, target):
        xir = XIRDataObject('pi')
        xir.set_verbatim('name', name)
        xir.set_verbatim('target', target)
            
    def error(self, exception):
        "Handle a recoverable error."
        raise exception

    def fatalError(self, exception):
        "Handle a non-recoverable error."
        raise exception

    def warning(self, exception):
        "Handle a warning."
        print exception



