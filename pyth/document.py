"""
Abstract document representation
"""
from __future__ import absolute_import
import six

class _PythBase(object):

    def __init__(self, properties={}, content=[]):
        self.properties = {}
        self.content = []
        
        for (k,v) in six.iteritems(properties):
            self[k] = v

        for item in content:
            self.append(item)


    def __setitem__(self, key, value):
        if key not in self.validProperties:
            raise ValueError("Invalid %s property: %s" % (self.__class__.__name__, repr(key)))

        self.properties[key] = value

    def __getitem__(self, key):
        if key not in self.validProperties:
            raise ValueError("Invalid %s property: %s" %
                             (self.__class__.__name__, repr(key)))
        return self.properties.get(key)

    def append(self, item):
        """
        Try to add an item to this element.

        If the item is of the wrong type, and if this element has a sub-type,
        then try to create such a sub-type and insert the item into that, instead.
        
        This happens recursively, so (in python-markup):
          L [ u'Foo' ]
        actually creates:
          L [ LE [ P [ T [ u'Foo' ] ] ] ]

        If that doesn't work, raise a TypeError.
        """

        okay = True
        if not isinstance(item, self.contentType):
            if hasattr(self.contentType, 'contentType'):
                try:
                    item = self.contentType(content=[item])
                except TypeError:
                    okay = False
            else:
                okay = False
                
        if not okay:
            raise TypeError("Wrong content type for %s: %s (%s)" % (
                self.__class__.__name__, repr(type(item)), repr(item)))

        self.content.append(item)


class Text(_PythBase):
    """
    Text runs are strings of text with markup properties,
    like 'bold' or 'italic' (or 'hyperlink to ...').

    They are rendered inline (not as blocks).

    They do not inherit their properties from anything.
    """

    validProperties = ('bold', 'italic', 'underline', 'url', 'sub', 'super', 'strike')
    contentType = six.text_type

    def __repr__(self):
        return "Text('%s' %s)" % ("".join("[%s]" % r.encode("utf-8") for r in self.content), self.properties)


class Paragraph(_PythBase):
    """
    Paragraphs contain zero or more text runs.

    They cannot contain other paragraphs (but see List).

    They have no text markup properties, but may
    have rendering properties (e.g. margins)
    """

    validProperties = ()
    contentType = Text


class Image(Paragraph):
    """
    An image is stored in bytes. All properties of images from the rtf definition are allowed.
    """
    
    validProperties = (b'emfblip', b'pngblip', b'jpegblip', b'macpict', b'pmmetafile', b'wmetafile', b'dibitmap',
                       b'wbitmap', b'wbmbitspixel', b'wbmplanes', b'wbmwidthbytes', b'picw', b'pich', b'picwgoal',
                       b'pichgoal', b'picscalex', b'picscaley', b'picscaled', b'piccropt', b'piccropb', b'piccropr',
                       b'piccropl', b'picbmp', b'picbpp', b'bin', b'blipupi', b'blipuid', b'bliptag', b'wbitmap', 'underline')
    contentType = bytes

    def __repr__(self):
        return "Image(%d bytes, %s)" %(len(self.content[0])/2,self.properties)


class ListEntry(_PythBase):
    """
    A list of paragraphs representing one item in a list
    """
    validProperties = ()
    contentType = Paragraph


class List(Paragraph):
    """
    A list of paragraphs which will be rendered as a bullet list.

    A List is a Paragraph, so Lists can be nested.
    """

    validProperties = ()
    contentType = ListEntry
    


class Document(_PythBase):
    """
    Top-level item. One document is exactly one file.
    Documents consist of a list of paragraphs.
    """
    
    validProperties = ('title', 'subject', 'author')
    contentType = Paragraph
