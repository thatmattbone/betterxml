from xml.sax import saxexts
from xml.sax import saxlib

ADD_METHOD_PREFIX = "add"
SET_METHOD_PREFIX = "set"
DTD_CLASS_SYSTEM = "SYSTEM"
DTD_CLASS_PUBLIC = "PUBLIC"


class NaturalXMLParser(object):
    def __init__(self):
        self.handlerProperties = dict()
        self.handler = NaturalXMLHandler()

    def process(self, uri):
        parser = saxexts.make_parser()
        parser.setDocumentHandler(self.handler)
        try:
            f = open(uri)
            parser.parseFile(f)
        except IOError,e:
            raise NaturalXMLException("Could not open file: %s" % uri)
        except saxlib.SAXException,e:
            raise NaturalXMLException("Could not parse file: %s" % uri)
        
        return self.handler.getDocument()

    
    def setElementClassMapping(self, elementName, elementClass):
        self.handler.registerElementClass(elementClass, elementName)

    def setElementCDataMapping(self, elementClass, methodName):
        self.handler.registerElementCData(elementClass, methodName)

    def setElementAttributeMapping(self, elementName, xmlAttrName, objAttrName):
        self.handler.registerElementAttribute(elementName, 
                                              xmlAttrName, objAttrName)

    def setDocumentRootClass(self, rootClass):
        self.handler.registerDocumentRoot(rootClass)
    
    def setContentInfoMapping(self, elementClass, contentClass):
        self.handler.registerContentInfo(elementClass, contentClass)

    def toXML(self, file):
        metadata = self.handler.getDocument().xml_metadata
        docRootName = metadata['DocumentRootName']
        docRootInstance = metadata['DocumentRootInstance']
        dtdClass = metadata['DTDClass']
        dtdLocation = metadata['DTDLocation']
        
        topString = '''<?xml version="%s" encoding="%s"?>\n''' % ('1.0',
                                                                  'iso-8859-1')
        file.write(topString)

        docString = '''<!DOCTYPE %s %s %s>\n''' % (docRootName, dtdClass, 
                                                   dtdLocation)
        file.write(docString)
        self._toXML_internal(file, docRootInstance)
        
    def _toXML_internal(self, file, element):
        try:
            metadata = element.xml_metadata
        except AttributeError:
            raise NaturalXMLException("Element has no metadata. Cannot write tree.")
        try:
            elementName = metadata['ElementName']
        except KeyError:
            raise NaturalXMLException("No element name specified. Cannot write tree")
        try:
            attributes = metadata['Attributes']
        except KeyError:
            attributes = None

        try:
            cdata = metadata['CData']
        except KeyError:
            cdata = None

        try:
            children = metadata['Children']
        except KeyError:
            children = None

        file.write('''<%s ''' % elementName)

        if(attributes):
            for attr in attributes.keys():
                file.write('''%s="%s" ''' % (attr, attributes[attr]))
        
        file.write(">\n")

        if(cdata):
            file.write(cdata)

        if(children):
            for child in children:
                self._toXML_internal(file, child)

        file.write('''</%s>\n''' % elementName)

class NaturalXMLHandler(saxlib.DocumentHandler):
    def __init__(self):
        self.classTable = dict()
        self.attrTable = dict()
        self.contentTable = dict()
        self.cdataTable = dict()
        self.contextStack = []
        self.documentRootClass = None

    def characters(self, ch, start, length):
        topElement = self.contextStack[-1]
        try:
            methodName = self.cdataTable[type(topElement)]
        except KeyError:
            return
        methodName = ADD_METHOD_PREFIX + methodName
        method = getattr(topElement, methodName)
        method(ch)

    def endElement(self, name):
        #print "Ending element: %s" % name
        self.contextStack.pop()

    def _getElementAttribute(self, elementName, attrName):
        try:
            value = self.attrTable['%s.%s' % (elementName, attrName)]
        except KeyError:
            raise NaturalXMLException("No attribute mapping for element: %s attribute: %s" 
                                      % (elementName, attrName))
        if(value == None):
            return attrName
        return value

    def ignorableWhitespace(self, ch, start, length):
        pass

    def processingInstruction(self, target, data):
        pass

    def startElement(self, elementName, attrs):
        #print "Starting element: %s" % elementName
        try:
            element = self.classTable[elementName]()
        except KeyError:
            raise NaturalXMLException("No class specified for element: %s" % 
                                      elementName)

        #take care of the attributes
        for key in attrs.keys():
            name = self._getElementAttribute(elementName, key)
            name = SET_METHOD_PREFIX + name
            method = getattr(element, name)
            method(attrs.get(key))

        topElement = self.contextStack[-1]
        elementClassName = type(element).__name__
        
        methodName = ADD_METHOD_PREFIX + elementClassName

        method = getattr(topElement, methodName)
        method(element)

        self.contextStack.append(element)

    def endDocument(self):
        #print "The context stack is: "
        #print self.contextStack
        pass

    def setDocumentLocator(self, locator):
        pass

    def startDocument(self):
        #print "Starting document with root class: %s"  % self.documentRootClass
        self.contextStack.append(self.documentRootClass())

    def getDocument(self):
        return self.contextStack[-1]

    def registerDocumentRoot(self, documentRootClass):
        self.documentRootClass = documentRootClass
    
    def registerElementAttribute(self, elementName, attrName, mapName):
        self.attrTable['%s.%s' % (elementName, attrName)] = mapName

    def registerElementClass(self, klass, elementName): 
        self.classTable[elementName] = klass

    def registerElementCData(self, elementClass, objectMethName):
        self.cdataTable[elementClass] = objectMethName

    def registerContentInfo(self, elementClass, contentClass):
        self.contentTable[elementClass] = contentClass

#Replaced these with optional __metadata__ dictionary...see test.py
#class SingleNamespaceDocument():
#    def getDocumentRootName(self):
#        return None
#    def getDTDLocation(self):
#        return None
#    def getDTDClass():
#        return None
#class ContainedContent():
#    def getElementName():
#        return None
#    def getAttributes():
#        return None
#    def getChildren():
#        return None

class NaturalXMLException(Exception):
    def __init__(self, problem):
        self.problem = str(problem)

    def __str__(self):
        return self.problem

 