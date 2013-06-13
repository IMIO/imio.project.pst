import os
import time
import appy.pod.renderer
from StringIO import StringIO
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Products.Five import BrowserView

from imio.project.pst.interfaces import IListContainedDexterityObjectsForDisplay


def getOsTempFolder():
    tmp = '/tmp'
    if os.path.exists(tmp) and os.path.isdir(tmp):
        res = tmp
    elif 'TMP' in os.environ:
        res = os.environ['TMP']
    elif 'TEMP' in os.environ:
        res = os.environ['TEMP']
    else:
        raise "Sorry, I can't find a temp folder on your machine."
    return res


class ContainerFolderListingView(BrowserView):
    """
      This manage the elements listed on the view of a dexteroty container
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    def listRenderedContainedElements(self, portal_types=[]):
        """
          Get the contained elements, rendered for display
          If p_portal_types is specified, only return elements having the required portal_type
        """
        return IListContainedDexterityObjectsForDisplay(self.context).listContainedObjects()


class DocumentGenerationView(BrowserView):
    """
        Document generation with appy
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    def __call__(self):
        return self.generate_doc()

    def generate_doc(self):
        # Get the document template
        documentid = self.request.get('documentid', None)
        if documentid is None:
            return None
        pcat = self.context.portal_catalog
        document_brains = pcat(portal_type='File', id=documentid,
                               path={'query': '/'.join(self.portal.templates.getPhysicalPath()), 'depth': 1})
        if not document_brains:
            return "Cannot find the File object with id '%s'" % documentid
        document_obj = document_brains[0].getObject()
        file_type = 'odt'
        tempFileName = '%s/%s_%f.%s' % (getOsTempFolder(), document_obj._at_uid, time.time(), file_type)
        # Prepare rendering context
        try:
            dgm = getMultiAdapter((self.context, self.request), name=u'document-generation-methods')
        except ComponentLookupError:
            dgm = None
        dict_arg = {'self': self.context, 'view': dgm}
        renderer = appy.pod.renderer.Renderer(StringIO(document_obj), dict_arg, tempFileName,
                                              pythonWithUnoPath='/usr/bin/python')
        renderer.run()

        # Tell the browser that the resulting page contains ODT
        response = self.request.RESPONSE
        response.setHeader('Content-type', 'application/%s' % file_type)
        response.setHeader('Content-disposition', 'inline;filename="%s.%s"' % (self.context.id, file_type))

        # Returns the doc and removes the temp file
        f = open(tempFileName, 'rb')
        doc = f.read()
        f.close()
        os.remove(tempFileName)
        return doc


class DocumentGenerationPSTActionMethods(BrowserView):
    """
        Methods used in document generation view, for PSTAction
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    def __call__(self):
        return None

    def getOOParent(self):
        # must be modified to get parent
        return self.context
