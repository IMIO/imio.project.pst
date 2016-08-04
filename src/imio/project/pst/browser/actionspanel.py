# -*- coding: utf-8 -*-
from imio.actionspanel.browser.views import ActionsPanelView


class SortTransitionsActionsPanelView(ActionsPanelView):

    transitions = []

    def sortTransitions(self, lst):
        """ Sort transitions following transitions list order """
        tr_order = dict([(val, i) for (i, val) in enumerate(self.transitions)])
        lst.sort(lambda x, y: cmp(tr_order[x['id']], tr_order[y['id']]))


class PSTActionsPanelView(SortTransitionsActionsPanelView):

    transitions = [
        'begin',
        'set_to_be_scheduled',
        'stop',
        'finish',
        'back_to_created',
        'back_to_ongoing',
        'back_to_be_scheduled',
    ]


class ObjectivesActionsPanelView(SortTransitionsActionsPanelView):

    transitions = [
        'begin',
        'back_to_created',
        'achieve',
        'back_to_ongoing',
    ]
