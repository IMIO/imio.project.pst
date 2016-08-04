# -*- coding: utf-8 -*-
"""Custom columns."""
from collective.eeafaceted.z3ctable import _ as _cez
from collective.eeafaceted.z3ctable.columns import (
    BaseColumn, DateColumn, VocabularyColumn)

from imio.dashboard.columns import ActionsColumn


class HistoryActionsColumn(ActionsColumn):

    header = _cez("header_actions")
    header_js = '<script type="text/javascript">jQuery(document).ready(initializeOverlays);' \
                'jQuery(document).ready(preventDefaultClickTransition);</script>'
    params = {'showHistory': True, 'showActions': False}
    view_name = 'actions_panel'


class CategoriesColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.categories_vocabulary'


class PlannedBeginDateColumn(DateColumn):

    pass


class PlannedEndDateColumn(DateColumn):

    pass


class EffectiveBeginDateColumn(DateColumn):

    pass


class EffectiveEndDateColumn(DateColumn):

    pass


class PriorityColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.priority_vocabulary'


class HealthIndicatorColumn(VocabularyColumn):

    vocabulary = u'imio.project.pst.content.action.health_indicator_vocabulary'


class ProgressColumn(BaseColumn):

    pass


class ManagerColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.manager_vocabulary'
