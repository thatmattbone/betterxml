class XAttributes:
    """
    This class contains and manages all of the XML Attributes 
    (key/value pairs) for an XML Element. It should meet all of 
    the requirements for Attribute management in XML.
    """

    def __init__(self, attrs=None):
        self.attributes = {}
        if attrs:
            for key in attrs.keys():
                self.attributes[key] = attrs.get(key)
    


    def containsAttribute(self, name):
        """Return true if an attribute with given name exists.

        If the supplied attribute name exists in this instance 
        of XAttributes then the function returns true (1); 
        Otherwise, it returns false (0).

        Keyword arguments:
        name -- the name (key) of the attribute whose existence is being checked.
        """
        return self.attributes.has_key(name)
    


    def containsAttributes(self, names_list):
        """Return true if all the attributes exist.

        If all the attribute keys fron the supplied list exist in 
        this instance of XAttributes then returns true (1); otherwise, 
        returns false (0).

        Keyword arguments:
        name_list -- the list of attribute keys whose existence are being checked.
        """
        for name in names_list:
            if not self.attributes.has_key(name):
                return 0
        return 1
    


    def getAttributes(self):
        """Return a dictionary of all attributes.

        The dictionary mirrors the attributes in that the key of the 
        dictionary entry is the attribute name and the value of the 
        dictionary entry is the attribute value.
        """
        return self.attributes
    


    def getAttributeValue(self, attributeName):
        """Return value associated with the supplied attribute name.

        This will return none if the passed in attribute name does not
        exist.

        Keyword arguments:
        name -- the name of the attribute whose value is being retrieved.
        """
        if self.attributes.has_key(attributeName):
            return self.attributes[attributeName]
        return None
    


    def removeAttribute(self, attributeName):
        """Remove the attribute (and its value).

        Keyword arguments:
        name -- the name of the attribute that should be removed.
        """
        if self.attributes.has_key(attributeName):
            del self.attributes[attributeName]
    


    def setAttribute(self, name, value):
        """Set an attribute name to the given value.
        
        If the attribute already exists, the value will be 
        overwritten. If the attribute does not exist, it will 
        be created and given the supplied value.
        
        Keyword arguments:
        name -- the name of the attribute key
        value -- the attribute value
        """
        self.attributes[name] = value
    


    def size(self):
        """Return the number of attributes."""
        return len(self.attributes)
    


    def toXML(self):
        """Return a valid XML representation of the attributes.

        Alone, the returned string would not be valid XML, but it 
        is a valid representation of the attributes that could be 
        placed inside of an element tag.  For example, these pairs:
          'key1':'value1'
          'key2':'value2'
        would be:
          key1='value1' key2='value2'
        """
        ret = ""
        if (self.size() == 0):
            return ret
        
        for entry in self.attributes.items():
            ret = ret + entry[0]
            ret = ret + "='"
            ret = ret + entry[1]
            ret = ret + "' "
        
        return ret.strip()
    
