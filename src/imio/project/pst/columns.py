# -*- coding: utf-8 -*-
"""Custom columns."""
from collective.eeafaceted.z3ctable import _ as _cez

from imio.dashboard.columns import ActionsColumn


class HistoryActionsColumn(ActionsColumn):

    header = _cez("header_actions")
    header_js = '<script type="text/javascript">jQuery(document).ready(initializeOverlays);' \
                'jQuery(document).ready(preventDefaultClickTransition);</script>'
    params = {'showHistory': True, 'showActions': False}
    view_name = 'actions_panel'
