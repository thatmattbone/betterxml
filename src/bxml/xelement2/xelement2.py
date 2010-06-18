"""
XElement is a DOM that makes sense for Python. We use the SAX interface to
build the XElement tree.
"""

import string
import sys
import types
from UserDict import UserDict

from xml.sax.handler import ContentHandler, ErrorHandler
from bxml.util.UserStack import UserStack

# To take advantage of new-style Python classes, it is necessary to inherit,
# somewhere along the inheritance tree, from object. Old-style Python classes
# do not have object as a base class.
#
# Using new-style classes is beneficial in order to take advantage of
# the super(class,object) invocation.


class UserDictObject(UserDict, object):
    pass

class XExceptionGeneral(BaseException):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return text

class XAttributes(UserDictObject):
    def __init__(self, attrs=None):
        super(XAttributes, self).__init__(self)
        if not attrs:
            return
        for (attribute, value) in attrs.items(): 
            self[attribute] = value

    def __setitem__(self, key, item):
        if type(key) != types.TupleType and len(key) != 2:
            raise XExceptionGeneral("key must be a pair (namespace, name)")
        super(XAttributes, self).__setitem__(key, item)

    def getByName(self, name, ifnotfound=None):
        for attribute in self.keys():
            if attribute[1] == name:
                return self[attribute]
        return ifnotfound

    def getByNamespaceName(self, ns, name):
        return self.get( (ns, name), None)

    def hasAttributes(self, attr_list):
        for attr in attr_list:
            if not self.has_key(attr):
                return 0
        return 1


def CreateElement(**kw):
    """
    convenience  interface
       name -> name of the element desired
       text -> any initial text
       children -> list of other XElements
       attributes -> list of (attr_i, value_i) pairs
       element_class -> user supplied class instead of XElement
    """
    name = kw.get('name', None)
    text = kw.get('text', '')
    children = kw.get('children', [])
    attributes = kw.get('attributes', [])
    element_class = kw.get('element_class', XElement)
    
    if not name:
        raise XExceptionGeneral("'name' parameter not specified")
    if type(text) != type(''):
        raise XExceptionGeneral("'text' parameter not a string")
    if type(children) != type([]):
        raise XExceptionGeneral("'children' parameter must be a list of XElement or subclasses")
    if type(attributes) != type([]):
        raise XExceptionGeneral("'attributes' must be a list of tuples")

    for c in children:
        if not isinstance(c, XElement):
            raise XExceptionGeneral("found non-XElement in 'children' list")

    for a in attributes:
        if type(a) not in [type(()), type([])] and len(a) < 2:
            raise XExceptionGeneral("found non-tuple or tuple of len < 2 in 'attributes' list")
    xe = element_class()

    xe.setName(name)
    xe.cdata(text)
    xe.setAttributes()
    xe.setChildren(children)

    attrs = xe.getAttributes()
    for a in attributes:
        attrs[ a[0] ] = a[1]
    return xe
    
class XElement(object):
    def __init__(self):
        self.children = []
        self.name = None
        self.qname = None
        self.ns = None
        self.attrs = None
        # Need to fix this to clone the tuple data.
    def clone(self, nodes_visited={}):
        if nodes_visited.has_key(self):
            raise XExceptionGeneral("circular reference in XElement.clone()")
        nodes_visited[self] = None
        my_class = self.__class__
        new_me = my_class()
        new_me.name = self.name
        # new_me.text = self.text[:]
        new_me.attrs = XAttributes()
        for attr_name in self.attrs.keys():
            for attr_value in self.attrs[attr_name]:
                new_me.attrs[attr_name] = attr_value
        for c in self.children:
            c_clone = c.clone(nodes_visited)
            new_me.linkTo(c_clone)
        return new_me
    
    def setName(self, name):
        self.name = name

    def setNamespace(self, ns):
        self.ns = ns

    def setQname(self, qname):
        self.qname = qname

    def setAttributes(self, attrs=None):
        self.attrs = XAttributes(attrs)

    def setChildren(self, children):
        self.children = []
        for c in children:
            self.children.append(c)

    def hasAttributes(self, attr_list):
        return self.attrs.hasAttributes(attr_list)

    def getAttributes(self):
        return self.attrs

    def initialize(self):
        pass

    def finalize(self, parent):
        pass

    def linkTo(self, element):
        if isinstance(element, XElement):
            self.children.append(element)
        else:
            raise XExceptionGneral("An XElement is required; a %s was specified." % type(element))

    def cdata(self, ignorable_ws, text):
        self.children.append( (ignorable_ws, text) )
    
    def printBFS(self, depth=0):
        print " " * depth, str(self)
        for node in self.children:
            node.printBFS(depth+1)

    def visit(self, depth):
        print " " * depth, str(self)

    def walkBFS(self, depth=0):
        self.doWalkBFS(depth)

    def doWalkBFS(self, depth=0):
        self.visit(depth)
        for node in self.children:
            node.doWalkBFS(depth+1)

    def getName(self):
        return self.name

    def getText(self):
        all_text = []
        for child in self.children:
            if type(child) == type(()):
                (ignorable, text) = child
                if not ignorable:
                    all_text.append(text)
        return all_text

    def getChildren(self, klass=None):
        if not klass:
            return self.children[:]

        children = []
        if type(klass) == type(''):
            for node in self.children:
                if node.__class__.__name__ == klass:
                    children.append(node)
        else:
            for node in self.children:
                if isinstance(node, klass):
                    children.append(node)
        return children

    def getChild(self, klass=None, pos=0):
        children = self.getChildren(klass)
        try:
            return children[pos]
        except:
            return None

    def __str__(self):
        return self.toXML(indent_text="  ")
    
    __repr__ = __str__

    def toXML(self, **kw):
        """
        Convert an XElement tree into XML. You may pass:
           indent - a starting indentation level (integer); defaults to 0.
           indent_text - text to use for each level of indentation (string); 
              defaults to ' '
           prologue - a list of strings to emit as the prologue; defaults to
              ['<?xml ...?>','<!-- XIR Tools; (c) 2001, George K. THiruvathukal -->']
              This could be useful if you want to emit things like DTD and
              other stuff.
        """
        indent = kw.get('indent', 0)
        indent_text = kw.get('indent_text', ' ')

        rep = ''

        # Emit the prologue
        if not indent:
            prologue = kw.get('prologue', ['<?xml version="1.0"?>'])
            for text in prologue:
                rep = rep + text

        # Output the element header (indented)
        rep = rep + indent_text * indent
        rep = rep + '<%s' % self.qname

        # And its attributes on the same line.
        if self.attrs:
            attrs_keys = self.attrs.keys()
            for (attr_name, attr_value) in self.attrs.items():
                if type(attr_name) == type(()):
                    if attr_name[0] == None:
                        rep = rep + ' %s="%s"' % (attr_name[1], attr_value)
                    else:
                        rep = rep + ' %s:%s="%s"' % (attr_name[0], attr_name[1], attr_value)
                else:
                    rep = rep + ' %s="%s"' % (attr_name, attr_value)
            rep = rep + '>'


        for node in self.children:
            if type(node) != types.TupleType:
                rep = rep + node.toXML(indent=indent+1, indent_text=indent_text)
            else:
                rep = rep + indent_text * indent
                (ignorable, text) = node
                if not ignorable:
                    rep = rep + text

        # Output the closing element; make sure the last thing written 
        # emits a new line.
        rep = rep + indent_text * indent
        rep = rep + '</%s>' % self.qname
        rep = rep + ''
        return rep
        
class XTreeHandler(ContentHandler, ErrorHandler):
    def __init__(self, **options):
        self.elems = 0
        self.attrs = 0
        self.pis = 0
        self.contextStack = UserStack([])
        #self.contextStack.push("x")
        self.document = XDocumentRoot()
        self.contextStack.push(self.document)
        self.elementMap = {}
        self.namespaceModules = {}
        self.default_namespace_uri = None
        self.previous_namespace_used = None
        
        self.ignoreWhiteSpace = options.has_key('IgnoreWhiteSpace') \
          and options['IgnoreWhiteSpace'] in ['true','yes',1,'1']
        self.removeWhiteSpace = options.has_key('RemoveWhiteSpace') \
          and options['RemoveWhiteSpace'] in ['true','yes',1,'1']
        self.createElementMap = options.has_key('CreateElementMap') \
          and options['CreateElementMap'] in ['true','yes',1,'1']
        self.requireUserClasses = options.has_key('RequireUserClasses') \
          and options['RequireUserClasses'] in ['true','yes',1,'1']


    def registerNamespace(self, userModule):
        # Every module must contain a function getNamespaceURI() that tells
        # what URI is managed by the classes in the module.
        if type(userModule) != types.ModuleType:
            raise XExceptionGeneral("a module must be specified")

        moduleName = userModule.__name__

        # User module must provide getNamespaceURI(), which returns a
        # string containing the URI for the XML namespace being provided.

        getNamespaceURI = getattr(userModule, 'getNamespaceURI', None)
        if callable(getNamespaceURI):
            moduleURI = getNamespaceURI()
        else:
            raise XExceptionGeneral("%s.getNamespaceURI() missing or not callable" % moduleName)
        
        if moduleURI in self.namespaceModules.keys():
            raise XExceptionGeneral("%s.getNamespaceURI() duplicate NS definition %s" % (moduleName, moduleURI))

        # User module must provide a default class to be instantiated for
        # any unhandled element name.

        getDefaultElementClass = getattr(userModule, "getDefaultElementClass", None)
        if callable(getDefaultElementClass):
            xeClass = getDefaultElementClass()
        else:
            raise XExceptionGeneral("module must provide getDefaultElementClass() definition")

        if not type(xeClass) == type(XElement) or not issubclass(xeClass, XElement):
            raise XExceptionGeneral("getDefaultElementClass() in %s must return XElement subclass" % moduleName)
           
        getMappings = getattr(userModule, "getMappings", None)
        if callable(getMappings):
            mappings = getMappings()
        else:
            raise XExceptionGeneral("%s.getMappings() definition missing or not callable")
        
        mappings = getMappings()
        for (elementName, elementClass) in mappings.items():
            if type(elementName) != type(''):
                raise XExceptionGeneral("%s.getMappings() has dict with non-string key" % moduleName)
            if not type(xeClass) == type(XElement) or \
               not issubclass(xeClass, XElement):
                raise XExceptionGeneral("%s.getMappings() has dict with non-XElement value" % moduleName)

        self.namespaceModules[moduleURI] = { 'module' : userModule,
                                             'uri' : moduleURI,
                                             'default_class' : xeClass,
                                             'mappings' : mappings }
        print "registration succeeded for namespace %s" % moduleURI
        
    def getElementMap(self):
        return self.elementMap

    def getDocument(self):
        return self.document


    # SAX/SAX 2 Interfaces

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startDocument(self):
        self.ns_prefixes = {}
        pass

    def endDocument(self):
        pass

    def startPrefixMapping(self, prefix, uri):
        pass

    def endPrefixMapping(self, prefix):
        pass

    def startElementNS(self, name, qname, attrs):
        (ns_uri, element_name) = name
        print "startElementNS", ns_uri, element_name, qname
       
        # In XElement, it is required to always have a default namespace URI registered.
        if ns_uri == None:
            ns_uri = self.default_namespace_uri

        # Find the module associated with namespace via a previous registerNamespace() call.
        try:
            moduleInfo = self.namespaceModules[ns_uri]
        except:
            print name, qname, attrs, "default uri", ns_uri
            raise XExceptionGeneral("unlikely error; unmapped namespace URI %s: Forgot to register it?" % ns_uri)


        # Map element_name to a user-defined class instance.
        mappings = moduleInfo['mappings']
        try:
            if mappings == None:
                elementClass = getattr(moduleInfo['module'], element_name, None)
            else:
                elementClass = mappings[element_name]
        except:
            elementClass = moduleInfo['default_class']

        # if no such mapping was found, and there was no default policy for creating an instance,
        # then this is a condition for immediate failure.
        if elementClass == None:
            raise XExceptionGeeneral("Unable to map element %s in URI %s to a default or user-defined class" % \
                  (element_name, ns_uri))

        
        # As with XElement 1.0, create the element from the class object.
        
        element = elementClass()
        element.setName(element_name)
        element.setNamespace(ns_uri)
        element.setQname(qname)
        element.setAttributes(attrs)

        if self.createElementMap:
            if not self.elementMap.has_key(name):
                self.elementMap[name] = []
            self.elementMap[name].append(element)

        element.initialize()

        self.contextStack.top().linkTo(element)

        self.contextStack.push(element)
        self.elems = self.elems + 1
        self.attrs = self.attrs + len(attrs)

    def endElementNS(self, name, qname):
        popElement = self.contextStack.pop()
        popElement.finalize(self.contextStack.top())

    def characters(self, content):
        self.contextStack.top().cdata(0, content)

    def showContext(self, context):
        for x in self.contextStack:
            print type(x)

    def ignorableWhitespace(self, content):
        self.contextStack.top().cdata(1, content)

    def skippedEntity(self, name):
        pass

    def processingInstruction(self, target, data):
        self.pis = self.pis + 1

    def error(self, exception):
        raise exception

    def fatalError(self, exception):
        raise exception

    def warning(self, exception):
        raise exception

class XDocumentRoot(XElement):
    def __init__(self):
        self.name = None
        self.attrs = None
        self.children = []
        self.text = ''
        XElement.__init__(self)
