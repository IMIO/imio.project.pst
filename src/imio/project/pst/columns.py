# -*- coding: utf-8 -*-
"""Custom columns."""
from imio.dashboard.columns import ActionsColumn


class HistoryActionsColumn(ActionsColumn):

    header_js = '<script type="text/javascript">jQuery(document).ready(initializeOverlays);' \
                'jQuery(document).ready(preventDefaultClickTransition);</script>'
    params = {'showHistory': True, 'showActions': False}
    view_name = 'actions_panel'
