# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from imio.actionspanel.browser.viewlets import ActionsPanelViewlet
from imio.actionspanel.browser.views import ActionsPanelView
from plone import api
from plone.memoize import ram
from zope.component import getMultiAdapter


def actionspanelview_cachekey(method,
                              self,
                              useIcons=True,
                              showOwnDelete=False,
                              showActions=True,
                              showAddContent=False,
                              showArrows=True,
                              **kwargs):
    """ cachekey method using only modified params. Must be adapted if changes !!
        We will add the following informations:
        * context
        * modification date
        * review state
        * current user
        * user groups
        * paste
    """
    user = self.request['AUTHENTICATED_USER']
    return (useIcons, showOwnDelete, showActions, showAddContent, showArrows,
            self.context, user.getId(), self.context.modified(), api.content.get_state(self.context, default=None),
            sorted(user.getGroups()), self.parent.cb_dataValid(),
            showArrows and self.parent.getObjectPosition(self.context.id) or 0)


class ProjectSpaceActionsPanelView(ActionsPanelView):
    """
      This manage the view displaying actions on projectspace.
    """

    transitions = [
        'hide', 'reject',
        'show_internally', 'publish_internally',
    ]

    def __init__(self, context, request):
        super(ProjectSpaceActionsPanelView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.SECTIONS_TO_RENDER += (
            'renderExportAsXML',
        )
        self.ACCEPTABLE_ACTIONS = ('paste', 'delete', 'archive', )

    def showExportAsXML(self):
        return self.context.restrictedTraverse('pst-utils').is_in_user_groups(
            user=self.member, groups=['pst_editors']
        )

    def renderExportAsXML(self):
        """
          Render export to XML button.
        """
        if self.showExportAsXML():
            return ViewPageTemplateFile("actions_panel_export_as_xml.pt")(self)
        return ''

    def sortTransitions(self, lst):
        """ Sort transitions following transitions list order """
        tr_dict = {}
        new_lst = []
        for item in lst:
            tr_dict[item['id']] = item
        for transition in self.transitions:
            if transition in tr_dict:
                new_lst.append(tr_dict[transition])
        del lst[:]
        for item in new_lst:
            lst.append(item)

    def _returnTo(self, ):
        """ What URL should I return to after moving the element and page is refreshed. """
        return self.request.get('URL1')

    @ram.cache(actionspanelview_cachekey)
    def __call__(self,  # default values will be used in dashboards !
                 useIcons=True,
                 #showTransitions=True,
                 #appendTypeNameToTransitionLabel=False,
                 #showEdit=True,
                 #showExtEdit=False,
                 showOwnDelete=False,
                 showActions=True,
                 showAddContent=False,
                 #showHistory=False,
                 #showHistoryLastEventHasComments=True,
                 showArrows=True,
                 arrowsPortalTypeAware=True,
                 **kwargs):
        return super(ProjectSpaceActionsPanelView, self).__call__(
            useIcons=useIcons,
            #showTransitions=showTransitions,
            #appendTypeNameToTransitionLabel=appendTypeNameToTransitionLabel,
            #showEdit=showEdit,
            #showExtEdit=showExtEdit,
            showOwnDelete=showOwnDelete,
            showActions=showActions,
            showAddContent=showAddContent,
            #showHistory=showHistory,
            #showHistoryLastEventHasComments=showHistoryLastEventHasComments,
            showArrows=showArrows,
            arrowsPortalTypeAware=arrowsPortalTypeAware,
            **kwargs)


class SortTransitionsActionsPanelView(ActionsPanelView):
    """
      This manage the view displaying actions on context.
    """

    transitions = []

    def __init__(self, context, request):
        super(SortTransitionsActionsPanelView, self).__init__(context, request)
        self.context = context
        self.parent = context.aq_parent
        self.request = request
        self.ACCEPTABLE_ACTIONS = ('cut', 'copy', 'paste', 'delete', )

    def sortTransitions(self, lst):
        """ Sort transitions following transitions list order """
        tr_order = dict([(val, i) for (i, val) in enumerate(self.transitions)])
        lst.sort(lambda x, y: cmp(tr_order[x['id']], tr_order[y['id']]))

    def _returnTo(self, ):
        """ What URL should I return to after moving the element and page is refreshed. """
        return self.request.get('URL1')

    @ram.cache(actionspanelview_cachekey)
    def __call__(self,  # default values will be used in dashboards !
                 useIcons=True,
                 #showTransitions=True,
                 #appendTypeNameToTransitionLabel=False,
                 #showEdit=True,
                 #showExtEdit=False,
                 showOwnDelete=False,
                 showActions=True,
                 showAddContent=False,
                 #showHistory=False,
                 #showHistoryLastEventHasComments=True,
                 showArrows=True,
                 arrowsPortalTypeAware=True,
                 **kwargs):
        return super(SortTransitionsActionsPanelView, self).__call__(
            useIcons=useIcons,
            #showTransitions=showTransitions,
            #appendTypeNameToTransitionLabel=appendTypeNameToTransitionLabel,
            #showEdit=showEdit,
            #showExtEdit=showExtEdit,
            showOwnDelete=showOwnDelete,
            showActions=showActions,
            showAddContent=showAddContent,
            #showHistory=showHistory,
            #showHistoryLastEventHasComments=showHistoryLastEventHasComments,
            showArrows=showArrows,
            arrowsPortalTypeAware=arrowsPortalTypeAware,
            **kwargs)

    def get_wsclient_actions(self):
        """ Return wsclient actions """
        ret = []
        object_buttons = self.portal.portal_actions.object_buttons
        for object_button in object_buttons.objectValues():
            if object_button.id.startswith('plonemeeting_wsclient_action_'):
                ret.append(object_button.id)
        return ret


class ObjectivesActionsPanelView(SortTransitionsActionsPanelView):

    transitions = [
        'back_to_created', 'back_to_ongoing',
        'begin', 'achieve',
    ]


class PSTActionsPanelView(SortTransitionsActionsPanelView):

    def __init__(self, context, request):
        super(PSTActionsPanelView, self).__init__(context, request)
        self.ACCEPTABLE_ACTIONS = list(self.ACCEPTABLE_ACTIONS) + self.get_wsclient_actions()

    transitions = [
        'back_to_created', 'back_to_ongoing', 'back_to_be_scheduled',
        'begin', 'set_to_be_scheduled', 'finish', 'stop',
    ]


class TaskActionsPanelView(SortTransitionsActionsPanelView):

    def __init__(self, context, request):
        super(TaskActionsPanelView, self).__init__(context, request)
        self.ACCEPTABLE_ACTIONS = list(self.ACCEPTABLE_ACTIONS) + self.get_wsclient_actions()

    transitions = [
        'back_in_created', 'back_in_to_assign', 'back_in_to_do', 'back_in_progress', 'back_in_realized',
        'do_to_assign', 'do_to_do', 'do_in_progress', 'do_realized', 'do_closed'
    ]


class ContactActionsPanelView(ActionsPanelView):

    def __init__(self, context, request):
        super(ContactActionsPanelView, self).__init__(context, request)
        self.ACCEPTABLE_ACTIONS = ('cut', 'copy', 'paste', 'delete', )


# VIEWLETS #

class PstActionsPanelViewlet(ActionsPanelViewlet):
    """ actions panel viewlet """

    def renderViewlet(self):
        if self.show():
            view = getMultiAdapter((self.context, self.request), name='actions_panel')
            return view(useIcons=False, showTransitions=True, showOwnDelete=False, showAddContent=True,
                        showActions=True, showArrows=False, arrowsPortalTypeAware=False)
