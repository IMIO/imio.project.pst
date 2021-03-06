from eea.facetednavigation.browser.app.view import FacetedContainerView
from eea.facetednavigation.criteria.handler import Criteria as eeaCriteria
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.widgets.storage import Criterion
from imio.helpers.browser.views import ContainerFolderListingView
from imio.project.core.utils import getProjectSpace
from imio.project.core.content.projectspace import IProjectSpace
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import pkg_resources


class FacetedContainerFolderListingView(ContainerFolderListingView, FacetedContainerView):

    def __init__(self, context, request):
        ContainerFolderListingView.__init__(self, context, request)
        FacetedContainerView.__init__(self, context, request)

    def has_subactions(self):
        return self.context.listFolderContents({'portal_type': 'pstsubaction'})


def get_criteria_holder(context):
    pst = getProjectSpace(context)
    if IProjectSpace.providedBy(context):
        return pst.strategicobjectives
    elif context.portal_type == 'strategicobjective':
        return pst.operationalobjectives
    elif context.portal_type == 'operationalobjective':
        return pst.pstactions
    elif context.portal_type == 'pstaction':
        if context.listFolderContents({'portal_type': 'pstsubaction'}):
            context.REQUEST.set('has_subaction', True)
            return pst.pstactions
        else:
            context.REQUEST.set('has_subaction', False)
            return pst.tasks
    elif context.portal_type == 'pstsubaction':
        return pst.tasks
    elif not IFacetedNavigable.providedBy(context):
        return pst

    return context


restrict_pt_to = {'operationalobjective': u'pstaction', 'pstaction': u'pstsubaction'}


class Criteria(eeaCriteria):
    """ Handle criteria
    """

    def __init__(self, context):
        """ Handle criteria
        """
        original_context = context
        super(Criteria, self).__init__(context)
        self.context = get_criteria_holder(context)

        self.criteria = []
        for crit in self._criteria():
            if crit.widget == u'sorting':
                criterion = Criterion(**{
                    '_cid_': u'c0',
                    'title': u'Sort on',
                    'position': u'top',
                    'section': u'default',
                    'hidden': u'True',
                    'default': u'getObjPositionInParent',
                    'widget': u'sorting'})
                self.criteria.append(criterion)
                continue
            self.criteria.append(crit)
        portal_path = len(original_context.portal_url.getPortalPath())
        criterion = Criterion(**{
            '_cid_': u'restrictpath',
            'hidden': u'True',
            'default': unicode('/'.join(original_context.getPhysicalPath())[portal_path:]),
            'depth': u'',
            'index': u'path',
            'position': u'left',
            'root': u'/',
            'section': u'default',
            'theme': u'green',
            'title': u'path',
            'widget': u'path'})
        self.criteria.append(criterion)

        if self.context.id == 'pstactions' and context.portal_type in ('operationalobjective', 'pstaction'):
            criterion = Criterion(**{
                '_cid_': u'portaltype',
                'hidden': u'True',
                'default': restrict_pt_to[context.portal_type],
                'index': u'portal_type',
                'position': u'left',
                'section': u'default',
                'title': u'Portal type',
                'count': u'False',
                'widget': u'text'})
            self.criteria.append(criterion)


class Listing(BrowserView):
    index = ViewPageTemplateFile(
        pkg_resources.resource_filename(
            'collective.eeafaceted.z3ctable', 'browser/faceted-table-items.pt'))
