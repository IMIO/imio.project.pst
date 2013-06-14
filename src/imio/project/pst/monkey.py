# monkeypatch the Products.CMFCore.exportimport.content._makeInstance
# to not restrict imported fields to 'title' and 'description'

from ConfigParser import ConfigParser
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.exportimport.content import StructureFolderWalkingAdapter


def _makeInstance(self, id, portal_type, subdir, import_context):

    context = self.context
    properties = import_context.readDataFile('.properties',
                                             '%s/%s' % (subdir, id))
    tool = getToolByName(context, 'portal_types')

    try:
        tool.constructContent(portal_type, context, id)
    except ValueError:  # invalid type
        return None

    content = context._getOb(id)

    if properties is not None:
        lines = properties.splitlines()

        stream = StringIO('\n'.join(lines))
        # XXX begin first change
        #parser = ConfigParser(defaults={'title': '', 'description': 'NONE'})
        parser = ConfigParser()
        # XXX end first change
        parser.readfp(stream)

        # XXX begin main change
        for attribute_name, attribute_value in parser.items('DEFAULT'):
            setattr(content, attribute_name, attribute_value)

        #title = parser.get('DEFAULT', 'title')
        #description = parser.get('DEFAULT', 'description')

        #content.setTitle(title)
        #content.setDescription(description)
        # XXX end main change

    return content

StructureFolderWalkingAdapter._makeInstance = _makeInstance
