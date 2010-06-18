from xir.xdo import XIRDataObject, XIRReader 

class XIRContentHandler(object):
    def startDocument(self):
        raise NotImplementedError()
    
    def endDocument(self):
        raise NotImplementedError()
    
    def startPrefixMapping(self, nsPrefix, nsURI):
        raise NotImplementedError()
    
    def endPrefixMapping(self, nsURI):
        raise NotImplementedError()
    
    def startElement(self, nsURI, name, numberOfAttrs):
        raise NotImplementedError()
    
    def endElement(self, nsURI, name):
        raise NotImplementedError()

    def attribute(self, nsURI, name, value):
        raise NotImplementedError()
    
    def characters(self, length, cdata):
        raise NotImplementedError()

    def whitespace(self, length, cdata):
        raise NotImplementedError()
    
    def skippedEntity(self, name):
        raise NotImplementedError()
    
    def processingInstruction(self, name, target):
        raise NotImplementedError()
    
class XIRContentHandlerAdapter(XIRContentHandler):
    def startDocument(self):
        pass
    
    def endDocument(self):
        pass
    
    def startPrefixMapping(self, nsPrefix, nsURI):
        pass
    
    def endPrefixMapping(self, nsURI):
        pass
    
    def startElement(self, nsURI, name, numberOfAttrs):
        pass
    
    def endElement(self, nsURI, name):
        pass

    def attribute(self, nsURI, name, value):
        pass
    
    def characters(self, length, cdata):
        pass

    def whitespace(self, length, cdata):
        pass
    
    def skippedEntity(self, name):
        pass
    
    def processingInstruction(self, name, target):
        pass
    
class XIRParser(object):
    def __init__(self, reader, handler):
        self.reader = reader
        self.handler = handler
        
    def parse(self):
        while True:
            xir = self.reader.getNextRecord()
            if xir == None:
                break
            # Skip records that are basically junk and contribute nothing
            # to the underlying XML
            # TODO: 'nop' should be replaced with a proper type constant.
            xirType = xir.get_type()
            xirSubtype = xir.get_subtype()
            if xirType == 'nop':
                continue
            if xirType == 'document':
                if xirSubtype == 'begin':
                    self.handler.startDocument()
                else:
                    self.handler.endDocument()
            elif xirType == 'prefix':
                prefix = xir.get_value('prefix')
                uri = xir.get_value('uri')
                if xirSubtype == 'begin':
                    self.handler.startPrefix(prefix, uri)
                else:                    
                    self.handler.endPrefix(prefix, uri)
            elif xirType == 'element':
                if xirSubtype == 'begin':
                    attributes = xir.get_value('attributes')
                    ns = xir.get_value('ns')
                    name = xir.get_value('name')
                    self.handler.startElement(ns, name, attributes)
                else:
                    ns = xir.get_value('ns')
                    name = xir.get_value('name')
                    self.handler.endElement(ns, name)
            elif xirType in ['a', 'attribute']:
                ns = xir.get_value('ns')
                name = xir.get_value('name')
                value = xir.get_value('value')
                self.handler.attribute(ns, name, value)
            elif xirType == 'characters':
                cdata = xir.get_value('cdata')
                self.handler.characters(len(cdata), cdata)
            elif xirType == 'ws':
                cdata = xir.get_value('cdata')
                self.handler.whitespace(len(cdata), cdata)
            elif xirType == 'skipped-entity':
                name = xir.get_value('name')
                self.handler.skippedEntity(name)
            elif xirType == 'pi':
                name = xir.get_value('name')
                target = xir.get_value('target')
                self.handler.processingInstruction(name, target)
                