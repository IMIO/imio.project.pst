from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize import forever
from plone.portlets.interfaces import IPortletDataProvider

from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implements

from .. import _


def getPSTFolder():
    portal = getSite()
    return portal['pst']


class IMainImioProjectPstPortlet(IPortletDataProvider):
    """
        Principal portlet for imio.project.pst containing actions, ...
    """


class Assignment(base.Assignment):
    implements(IMainImioProjectPstPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Main imio.project.pst Portlet")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('portlet_mainimioprojectpst.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()
        self.anonymous = portal_state.anonymous()
        self.member = portal_state.member()

    @property
    def available(self):
        """
          Defines if the portlet is available in the context
        """
        return not self.anonymous

    def render(self):
        return self._template()

    def getOSsCreated(self):
        return self.portal.portal_catalog(id = 'strategicobjective-created')

    def getOSsOngoing(self):
        return self.portal.portal_catalog(id = 'strategicobjective-ongoing')

    def getOSsAchieved(self):
        return self.portal.portal_catalog(id = 'strategicobjective-achieved')

    # def getOOsIAmManager(self):
        # current_user = api.user.get_current()
        # user_groups = api.group.get_groups(username=current_user.id)
        # user_groups_id = [user_group.id for user_group in user_groups]
        # return self.portal.portal_catalog(portal_type = 'operationalobjective', manager = user_groups_id)

    # def getOOsIAmAdministrativeResponsible(self):
        # current_user = api.user.get_current()
        # user_groups = api.group.get_groups(username=current_user.id)
        # user_groups_id = [user_group.id for user_group in user_groups]
        # return self.portal.portal_catalog(portal_type = 'operationalobjective', administrative_responsible = user_groups_id)

    def getOOsCreated(self):
        return self.portal.portal_catalog(id = 'operationalobjective-created')

    def getOOsOngoing(self):
        return self.portal.portal_catalog(id = 'operationalobjective-ongoing')

    def getOOsAchieved(self):
        return self.portal.portal_catalog(id = 'operationalobjective-achieved')

    # def getActionsIAmManager(self):
        # current_user = api.user.get_current()
        # user_groups = api.group.get_groups(username=current_user.id)
        # user_groups_id = [user_group.id for user_group in user_groups]
        # return self.portal.portal_catalog(portal_type = 'pstactions', manager = user_groups_id)

    def getActionsCreated(self):
        return self.portal.portal_catalog(id = 'pstaction-created')

    def getActionsOngoing(self):
        return self.portal.portal_catalog(id = 'pstaction-ongoing')

    def getActionsStopped(self):
        return self.portal.portal_catalog(id = 'pstaction-stopped')

    def getActionsTerminated(self):
        return self.portal.portal_catalog(id = 'pstaction-terminated')

    def getActionsToBeScheduled(self):
        return self.portal.portal_catalog(id = 'pstaction-to_be_scheduled')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
