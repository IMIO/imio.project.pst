import os
import time
import appy.pod.renderer
from StringIO import StringIO
from zope.component import getMultiAdapter, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.schema.interfaces import IVocabularyFactory
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
        pcat = self.portal.portal_catalog
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


class DocumentGenerationMethods(object):
    """
        Common methods used in document generation view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        self.plone_portal_state_view = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    def __call__(self):
        return None

    def getParent(self):
        """
            get the parent object
        """
        return self.context.aq_inner.aq_parent

    def textFieldToHtml(self, value):
        """
            transform text field in html format
        """
        return self.enc(value).replace('\r\n', '<br />')

    def enc(self, value, encoding='utf8'):
        """
            encode text if necessary
        """
        if isinstance(value, unicode):
            value = value.encode(encoding)
        return value


class DocumentGenerationPSTActionMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for PSTAction
    """
    def getOSParent(self):
        return self.getParent().aq_inner.aq_parent

    def getSection(self):
        osparent = self.getOSParent()
        factory = getUtility(IVocabularyFactory, u'imio.project.core.content.project.categories_vocabulary')
        categories = factory(osparent)
        try:
            return categories.getTerm(osparent.categories).title.split(' - ')[0].encode('utf8')
        except IndexError:
            return ''

    def getDomain(self):
        osparent = self.getOSParent()
        factory = getUtility(IVocabularyFactory, u'imio.project.core.content.project.categories_vocabulary')
        categories = factory(osparent)
        try:
            return categories.getTerm(osparent.categories).title.split(' - ')[1].encode('utf8')
        except IndexError:
            return ''

    def getManagers(self):
        factory = getUtility(IVocabularyFactory, u'imio.project.core.content.project.manager_vocabulary')
        managers = factory(self.context)
        titles = []
        for manager in self.context.manager:
            titles.append(managers.getTerm(manager).title)
        return ', '.join(titles)
