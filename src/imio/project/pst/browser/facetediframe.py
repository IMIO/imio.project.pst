import pkg_resources
from zope.interface import implementer
from eea.facetednavigation.criteria.handler import Criteria as eeaCriteria
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from eea.facetednavigation.widgets.storage import Criterion
from persistent.list import PersistentList

class Criteria(eeaCriteria):
    """ Handle criteria
    """

    def __init__(self, context):
        """ Handle criteria
        """
        original_context = context
        super(Criteria, self).__init__(context)
        portal = api.portal.get()
        pst = portal.pst
        if self.context.portal_type == 'operationalobjective':
            self.context = pst.pstactions
        elif self.context.portal_type == 'strategicobjective':
            self.context = pst.operationalobjectives
        self.criteria = PersistentList(self._criteria())
        criterion = Criterion(**{'_cid_': u'restrictpath',
                         'hidden': u'True',
                         'default': unicode('/'+'/'.join(original_context.getPhysicalPath()[2:])),
                         'depth': u'',
                         'index': u'path',
                         'position': u'left',
                         'root': u'/',
                         'section': u'default',
                         'theme': u'green',
                         'title': u'path',
                         'widget': u'path'})
        self.criteria.append(criterion)

class Listing(BrowserView):
    index = ViewPageTemplateFile(
        pkg_resources.resource_filename(
        'collective.eeafaceted.z3ctable', 'browser/faceted-table-items.pt'))
