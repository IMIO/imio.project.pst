import pkg_resources
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

from eea.facetednavigation.browser.app.view import FacetedContainerView
from eea.facetednavigation.criteria.handler import Criteria as eeaCriteria
from eea.facetednavigation.widgets.storage import Criterion

from imio.project.core.browser.views import ContainerFolderListingView


class FacetedContainerFolderListingView(
        ContainerFolderListingView,
        FacetedContainerView):
    def __init__(self, context, request):
        ContainerFolderListingView.__init__(self, context, request)
        FacetedContainerView.__init__(self, context, request)


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

        self.criteria = self._criteria()
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
        self.criteria = self.criteria + [criterion]


class Listing(BrowserView):
    index = ViewPageTemplateFile(
        pkg_resources.resource_filename(
        'collective.eeafaceted.z3ctable', 'browser/faceted-table-items.pt'))
