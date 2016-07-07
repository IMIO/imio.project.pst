# -*- coding: utf-8 -*-
"""Custom columns."""
from collective.eeafaceted.z3ctable import _ as _cez
from collective.eeafaceted.z3ctable.columns import VocabularyColumn

from imio.dashboard.columns import ActionsColumn
from imio.project.pst import _


class HistoryActionsColumn(ActionsColumn):

    header = _cez("header_actions")
    header_js = '<script type="text/javascript">jQuery(document).ready(initializeOverlays);' \
                'jQuery(document).ready(preventDefaultClickTransition);</script>'
    params = {'showHistory': True, 'showActions': False}
    view_name = 'actions_panel'


class CategoriesColumn(VocabularyColumn):

    attrName = u'categories'
    vocabulary = u'imio.project.core.content.project.categories_vocabulary'
