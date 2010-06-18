import string
import sys
import types

from xml.sax.handler import ContentHandler

from bxml.util.UserStack import UserStack
from bxml.xattributes import XAttributes

XELEMENT_PROLOGUE = ['<?xml version="1.0"?>', '<!-- XElement Tools by GKT -->']



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
        raise "'name' parameter not specified"
    if type(text) != type(''):
        raise "'text' parameter not a string"
    if type(children) != type([]):
        raise "'children' parameter must be a list of XElement or subclasses"
    if type(attributes) != type([]):
        raise "'attributes' must be a list of tuples"

    for c in children:
        if not isinstance(c, XElement):
            raise "found non-XElement in 'children' list"

    for a in attributes:
        if type(a) not in [type(()), type([])] and len(a) < 2:
            raise "found non-tuple or tuple of len < 2 in 'attributes' list"
    xe = element_class()

    xe.setName(name)
    xe.setText(text)
    xe.setAttributes()
    xe.setChildren(children)

    attrs = xe.getAttributes()
    for a in attributes:
        attrs[ a[0] ] = a[1]
    return xe
    
class XElement:
    def __init__(self, name=None):
        self.children = []
        self.setAttributes()
        self.text = ""
        self.setName(name)

    def clone(self, nodes_visited={}):
        if nodes_visited.has_key(self):
            raise "circular reference in XElement.clone()"
        nodes_visited[self] = None
        my_class = self.__class__
        new_me = my_class()
        new_me.name = self.name
        new_me.text = self.text[:]
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

    def setAttributes(self, attrs=None):
        self.attrs = XAttributes(attrs)

    def setChildren(self, children):
        self.children = []
        for c in children:
            self.children.append(c)

    def hasAttributes(self, attr_list):
        return self.attrs.containsAttributes(attr_list)

    def getAttributes(self):
        return self.attrs

    def getAttribute(self, name, default_get=None):
        return self.attrs.getAttributeValue(name)

    def setText(self, text):
        self.text = text

    def initialize(self):
        pass

    def finalize(self, parent):
        pass

    def linkTo(self, element):
        if isinstance(element, XElement):
            self.children.append(element)
        else:
            raise "An XElement is required but %s was seen" % type(element)

    def cdata(self, text):
        self.text = self.text + text

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
        return self.text

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

    def getChildrenByName(self, name):
        return [x for x in self.children if x.getName() == name]

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

        repr = ''

        # Emit the prologue
        if not indent:
            prologue = kw.get('prologue', XELEMENT_PROLOGUE)
            for text in prologue:
                repr = repr + text + '\n'

        # Output the element header (indented)
        repr = repr + indent_text * indent
        repr = repr + '<%s' % (self.name)

        # And its attributes on the same line.
        if self.attrs:
            attrs_keys = self.attrs.getAttributes().keys()
            attrs_keys.sort()
            for attr_name in attrs_keys:
               attr_value = self.attrs.getAttributeValue(attr_name)
               repr = repr + ' %s="%s"' % (attr_name, attr_value)
        repr = repr + '>\n'

        # Output #PCDATA. Observe that my approach does *not* preserve data
        # between nested elements. This could be considered a feature.
        # NB: self.text *needs* to be escapeed. Get from saxutils.
        t = self.text
        t.strip()
        if t:
            repr = repr + (indent_text * (indent + 1)) + t + '\n'
        for node in self.children:
            repr = repr + node.toXML(indent=indent+1, indent_text=indent_text)

        # Output the closing element; make sure the last thing written 
        # emits a new line.
        repr = repr + indent_text * indent
        repr = repr + '</%s>' % (self.name) 
        repr = repr + '\n'
        return repr
        
class XTreeHandler(ContentHandler):
    def __init__(self, **options):
        self.elems = 0
        self.attrs = 0
        self.pis = 0
        self.contextStack = UserStack([])
        self.contextStack.push("x")
        self.document = XDocumentRoot()
        self.contextStack.push(self.document)
        self.elementMap = {}
        self.element_class = {}
        self.ignoreWhiteSpace = options.has_key('IgnoreWhiteSpace') \
          and options['IgnoreWhiteSpace'] in ['true','yes',1,'1']
        self.removeWhiteSpace = options.has_key('RemoveWhiteSpace') \
          and options['RemoveWhiteSpace'] in ['true','yes',1,'1']
        self.createElementMap = options.has_key('CreateElementMap') \
          and options['CreateElementMap'] in ['true','yes',1,'1']
        self.requireUserClasses = options.has_key('RequireUserClasses') \
          and options['RequireUserClasses'] in ['true','yes',1,'1']


    def registerElementClass(self, klass, element_name=None):
        """
        register the class that represents the tree node to construct
        upon encountering an element having element_name. If element_name
        is None, this means that the element name and class name match.
        """

        if element_name:
            self.element_class[element_name] = klass
        else:
            self.element_class[klass.__name__] = klass

    def getElementMap(self):
        return self.elementMap

    def startElement(self, name, attrs):
        try:
            element = self.element_class[name]()
        except:
            element = XElement()
       
        if element.__class__ == XElement and self.requireUserClasses:
            raise "No class defined to handle element %s" % str(name)
        element.setName(name)
        element.setAttributes(attrs)
        element.setText('')


        if self.createElementMap:
            if not self.elementMap.has_key(name):
                self.elementMap[name] = []
            self.elementMap[name].append(element)

        element.initialize()

        self.contextStack.top().linkTo(element)

        self.contextStack.push(element)
        self.elems = self.elems+1
        self.attrs = self.attrs+len(attrs)

    def endElement(self, name):
        popElement = self.contextStack.pop()
        popElement.finalize(self.contextStack.top())

    def characters(self, char):
        tos = self.contextStack.top()
#        if self.removeWhiteSpace:
#            text = ch[start:start+length]
#            splitText = string.split(text)
#            if len(tos.text) > 0:
#                pad = ' '
#            else:
#                pad = ''
#            for item in splitText:
#                tos.cdata(pad + item)
#                pad = ' '
#        else:
#            tos.cdata(ch[start:start+length])
        tos.cdata(char)

    def ignorableWhitespace(self, ch, start, length):
        if not self.ignoreWhiteSpace:
            self.contextStack.top().cdata(ch[start:start+length])

    def getDocument(self):
        return self.document

    def processingInstruction(self, target, data):
        self.pis = self.pis+1

class XDocumentRoot(XElement):
    def __init__(self):
        self.name = None
        self.attrs = None
        self.children = []
        self.text = ''
        XElement.__init__(self)
