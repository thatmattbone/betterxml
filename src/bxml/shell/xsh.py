"""
 xsh - XElement Shell

 By George K. Thiruvathukal

 This is a PostScript like interpreter for creating and manipulating XML
 documents. Path expressions are not yet supported but are coming next!

"""

from bxml.xelement2.xelement2 import *
from bxml.util.UserStack import *

import cmd
import sys, traceback

class ShellException(BaseException):
    def __init__( self, text ):
        self.text = text

class XSH( cmd.Cmd ):
    def __init__( self ):
        cmd.Cmd.__init__( self )
        self.prompt = "xsh$ "
        self.document = None
        self.element = None
        self.attribues = None
        self.namespace = None
        self.namespaces = {}
        self.stack = UserStack()
        self.quit = False

    def help_document( self ):
        print "usage: document"
        print " Make top stack element the target document (for possible XML code generation)"

    def do_document( self, arg ):
        try:
            self.document = self.stack.top()
        except:
            print "document: no elements on context stack, so no document root set"

    def help_xml( self ):
        print "usage: "
        print " Convert current document to XML (set via document command)"

    def do_xml( self, arg ):
        print self.document.toXML()

    def help_dtd( self ):
        print "usage: dtd <root> <type> <uri-or-location>"
        print " NOT IMPLEMENTED YET"

    def do_dtd( self, arg ):
        print "not implemented yet"

    def help_define_ns( self ):
        print "usage: define_namepspace <prefix>=<uri>"
        print " note: this command registers a new namespace. You may not use a namespace"
        print "       w/o calling this command first."

    def do_define_ns( self, arg ):
        print arg
        eq_pos = arg.find( "=" )
        prefix = arg[0:eq_pos]
        uri = arg[eq_pos+1:]
        self.namespaces[prefix] = uri

    def help_namespaces( self ):
        print "usage: namespaces"
        print " show namespace mappings"

    def do_namespaces( self, arg ):
        for ( prefix, uri ) in self.namespaces.items():
            print 'xmlns:%s="%s"' % ( prefix, uri )

    def help_set_ns( self ):
        print "usage: set_ns <prefix>"
        print " set the current namespace to the short name previously mapped as <prefix>"
            
    def do_set_ns( self, arg ):
        if self.namespaces.has_key( arg ):
            self.namespace = arg
        else:
            print "Cannot change namespace to %s. Did you use create_ns?" % arg

    def help_current_ns( self ):
        print "current_ns: Show current XML namespace"

    def do_current_ns( self, arg ):
        print 'xmlns:%s="%s"' % ( self.namespace, self.namespaces[self.namespace] )
    
    def help_element( self ):
        print "usage: element <name>"
        print " create an element having <name> within the current <namespace>."
        print " you must use push_context to change the element stack"
    
    def do_element( self, arg ):
        name = arg
        self.element = XElement()
        self.attributes = XAttributes()
        self.element.setName( name )
        prefix = self.namespace
        uri = self.namespaces[self.namespace]
        self.element.setNamespace( uri )
        self.element.setQname( ':'.join( ( prefix, name ) ) )
        self.element.setAttributes( self.attributes )

    def help_append(self):
        print "usage: append"
        print " append element to element atop stack. Clears element to prevent its reuse"
      
   
    def do_append(self, arg):
        try:
            self.stack.top().linkTo(self.element)
        except:
            if self.stack.empty():
                self.stack.push(self.element)

    def help_push_context(self):
        print "set the context to the current element"
      
    def do_push_context(self, arg):
        self.stack.push(self.element)

    def help_pop_context(self):
        print "pop current context (changes element in progress)"
      
    def do_pop_context(self, arg):
        if not self.stack.empty():
            self.stack.pop()
        try:
            self.element = self.stack.top()
        except:
            self.element = None
      
    def help_attribute( self ):
        print "usage: attribute <name>=<value>"
        print " create an attribute having <name>, <value> within the current"
        print " element."

    def do_attribute( self, arg ):    
        if self.element == None:
            print "attribute requires an element atop the stack"
            return
        eq_pos = arg.find( "=" )
        name = arg[0:eq_pos]
        value = arg[eq_pos+1:]
        self.element.attrs[ ( self.namespace, name ) ] = value

    def help_attribute_ns( self ):
        print "usage: attribute_ns <ns-prefix> <name> <value>"
        print " create an attribute having <ns>, <name>, <value> within the current"
        print " element."

    def do_attribute_ns(self, arg):
        print "Not implemented yet"
      
    def help_text( self ):
        print "usage: text <cdata>"
      
    def do_text(self, arg):
        print "not implemented yet"

    def help_quit( self ):
        print "usage: quit (exit without saving)"

    def do_quit( self, arg ):
        self.quit = True
        raise ShellException("quit")

    def help_element_xml(self):
        print "element_xml: Generate XML for current element in progress"
      
    def do_element_xml( self, arg ):
        print self.element.toXML()

    def do_stack(self, arg):
        for i in range(0, len(self.stack)):
            print "%d: %s" % (i, self.stack[i])
   
    def help_pop(self):
        print "usage: pop"
        print " remove top item of stack (if possible)"
      
    def do_pop(self, arg):
        try:
            self.stack.pop()
            if self.stack.empty():
                self.element = None
            else:
                self.element = self.stack.top()
        except:
            print "Stack underflow."
            self.element = None
               
    def help_stack( self ):
        print "usage: stack (show context stack)"

    def help_help(self):
        print "usage: help [<command>]"
        print " God help you if you need help on help!"
      
      
if __name__ == '__main__':
    xsh = XSH()
    while True:
       try:
          xsh.cmdloop()
       except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)
          if xsh.quit:
             break

