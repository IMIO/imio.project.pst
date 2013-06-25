import os
import time
import appy.pod.renderer
from StringIO import StringIO
from zope.component import getMultiAdapter, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.schema.interfaces import IVocabularyFactory
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from imio.project.pst.interfaces import IListContainedDexterityObjectsForDisplay
from imio.project.pst import _


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

    def textFieldToHtml(self, fieldname, obj=None):
        """
            transform text field in html format
        """
        return self.get(fieldname, obj=obj).replace('\r\n', '<br />')

    def get(self, fieldname, obj=None, default=''):
        """
            get an attr and encode it if necessary.
            if attr is None, return default
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        value = getattr(the_obj, fieldname)
        if value is None:
            return default
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return value

    def vocValue(self, vocabulary, fieldname, obj=None):
        """
            get the title of a vocabulary value
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        factory = getUtility(IVocabularyFactory, vocabulary)
        voc = factory(the_obj)
        value = voc.getTerm(self.get(fieldname, obj=the_obj)).title
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return value

    def vocValues(self, vocabulary, fieldname, obj=None, sep=None):
        """
            get the titles of a list vocabulary values
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        factory = getUtility(IVocabularyFactory, vocabulary)
        voc = factory(the_obj)
        values = []
        for token in self.get(fieldname, obj=the_obj, default=[]):
            value = voc.getTerm(token).title
            if isinstance(value, unicode):
                value = value.encode('utf8')
            values.append(value)
        if sep:
            return sep.join(values)
        return values

    def getState(self, obj=None, wf_id=None):
        """
            get the workflow state
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        return self.context.portal_workflow.getInfoFor(the_obj, 'review_state', wf_id=wf_id)

    def getObjectDGM(self, obj):
        """
            get the object 'document-generation-methods' view
        """
        try:
            return getMultiAdapter((obj, self.request), name=u'document-generation-methods')
        except ComponentLookupError:
            return None


class DocumentGenerationPSTMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for pst
    """

    def getStrategicObjectives(self):
        """
            get a list of contained strategic objectives
        """
        pcat = self.context.portal_catalog
        brains = pcat(portal_type='strategicobjective',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      sort_on='getObjPositionInParent')
        sos = {}
        for brain in brains:
            obj = brain.getObject()
            try:
                (section, domain) = self.vocValue(u'imio.project.core.content.project.categories_vocabulary',
                                                  'categories', obj=obj).split(' - ')
                if section not in sos:
                    sos[section] = {}
                if domain not in sos[section]:
                    sos[section][domain] = []
                sos[section][domain].append(obj)
            except ValueError:
                smi = IStatusMessage(self.request)
                smi.addStatusMessage(_("Cannot split this category '${cat}' with ' - ' separator",
                                       mapping={'cat': obj.categories}), type='error')
                print "Error splitting cat %s" % obj.categories
        return sos


class DocumentGenerationSOMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for strategicobjective
    """

    def getSection(self):
        """
            get the first part of a category value
        """
        try:
            return self.vocValue(u'imio.project.core.content.project.categories_vocabulary',
                                 'categories').split(' - ')[0]
        except IndexError:
            return ''

    def getDomain(self):
        """
            get the second part of a category value
        """
        try:
            return self.vocValue(u'imio.project.core.content.project.categories_vocabulary',
                                 'categories').split(' - ')[0]
        except IndexError:
            return ''

    def getOperationalObjectives(self):
        """
            get a list of contained operational objectives
        """
        pcat = self.context.portal_catalog
        brains = pcat(portal_type='operationalobjective',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      sort_on='getObjPositionInParent')
        oos = []
        for brain in brains:
            oos.append(brain.getObject())
        return oos


class DocumentGenerationOOMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for operationalobjective
    """

    def formatResultIndicator(self, expected=True, sep='<br />'):
        """
            return the result indicator as a string
        """
        rows = []
        for row in self.context.result_indicator:
            rows.append("%s = %d" % (row['label'].encode('utf8'), expected and row['value'] or row['reached_value']))
        return sep.join(rows)

    def getActions(self):
        """
            return a list of contained pstactions
        """
        pcat = self.context.portal_catalog
        brains = pcat(portal_type='pstaction',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1})
        return [brain.getObject() for brain in brains]


class DocumentGenerationPSTActionMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for PSTAction
    """

    def getSOParent(self):
        """
            get the strategic objective parent
        """
        return self.getParent().aq_inner.aq_parent

    def formatHealthIndicator(self):
        """
            Return the health indicator details with a specific html class following the health indicator field
        """
        return '<p class="fa-attr-valeur-%s">%s</p>' % (self.context.health_indicator.encode('utf8'),
                                                        self.get('health_indicator_details').replace('\r\n', '<br />'))
