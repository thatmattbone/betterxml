Hi:

We're working on a new version of Better XML. The focus will shift mostly from
Java to Python, which is actually where the project started!

Here's a peek at what is planned:

nxml	: Natural XML, based on work we have presented in CISE Magazine and
	  IEEE EIT 2008. This is a pure binding framework for going to/from
	  Python classes.

shell	: An interactive "shell" for working with XML. It's really a simple
	  stack language interpreter.

util	: some legacy utility classes, mainly for stack processing in Python.

xelement1 : A single namespace DOM for Python, aimed at simplicity and clarity.
	Allows for lightweight "binding" to Python classes.

xelement2 : Ditto of "xelement1" but aimed at multiple namespace documents.

xir : An intermediate representation for persisting a SAX stream. Can be
	parsed quickly and repeatedly to make multiple passes over an XML 
	input file.
