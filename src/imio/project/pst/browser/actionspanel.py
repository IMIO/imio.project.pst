# -*- coding: utf-8 -*-
from imio.actionspanel.browser.viewlets import ActionsPanelViewlet
from imio.actionspanel.browser.views import ActionsPanelView
from zope.component import getMultiAdapter


class ProjectSpaceActionsPanelView(ActionsPanelView):
    """
      This manage the view displaying actions on projectspace.
    """

    transitions = [
        'hide',
        'reject',
        'show_internally',
        'publish_internally',
    ]

    def __init__(self, context, request):
        super(ProjectSpaceActionsPanelView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.ACCEPTABLE_ACTIONS = ('paste', 'delete', 'archive', )

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


class SortTransitionsActionsPanelView(ActionsPanelView):
    """
      This manage the view displaying actions on context.
    """

    transitions = []

    def __init__(self, context, request):
        super(SortTransitionsActionsPanelView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.ACCEPTABLE_ACTIONS = ('cut', 'copy', 'paste', 'delete', )

    def sortTransitions(self, lst):
        """ Sort transitions following transitions list order """
        tr_order = dict([(val, i) for (i, val) in enumerate(self.transitions)])
        lst.sort(lambda x, y: cmp(tr_order[x['id']], tr_order[y['id']]))


class ObjectivesActionsPanelView(SortTransitionsActionsPanelView):

    transitions = [
        'back_to_created',
        'back_to_ongoing',
        'begin',
        'achieve',
    ]


class PSTActionsPanelView(SortTransitionsActionsPanelView):

    transitions = [
        'back_to_created',
        'back_to_ongoing',
        'back_to_be_scheduled',
        'begin',
        'set_to_be_scheduled',
        'finish',
        'stop',
    ]


# VIEWLETS #

class PstActionsPanelViewlet(ActionsPanelViewlet):
    """
        Override render method for pst document
    """

    def renderViewlet(self):
        view = getMultiAdapter((self.context, self.request), name='actions_panel')
        return view(useIcons=False, showTransitions=True, showOwnDelete=False, showAddContent=True)
