# -*- coding: utf-8 -*-
"""Custom columns."""
from collective.eeafaceted.z3ctable import _ as _cez
from collective.eeafaceted.z3ctable.columns import ActionsColumn
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import PrettyLinkColumn
from collective.eeafaceted.z3ctable.columns import VocabularyColumn
from collective.task.interfaces import ITaskMethods
from imio.project.pst.adapters import UNSET_DATE_VALUE


class HistoryActionsColumn(ActionsColumn):

    header = _cez("header_actions")
    header_js = '<script type="text/javascript">jQuery(document).ready(initializeOverlays);' \
                'jQuery(document).ready(preventDefaultClickTransition);</script>'
    params = {'showHistory': True, 'showActions': False}
    view_name = 'actions_panel'


class CategoriesColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.categories_vocabulary'


class PlannedBeginDateColumn(DateColumn):

    ignored_value = UNSET_DATE_VALUE


class PlannedEndDateColumn(DateColumn):

    ignored_value = UNSET_DATE_VALUE


class EffectiveBeginDateColumn(DateColumn):

    ignored_value = UNSET_DATE_VALUE


class EffectiveEndDateColumn(DateColumn):

    ignored_value = UNSET_DATE_VALUE


class PriorityColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.priority_vocabulary'


class HealthIndicatorColumn(VocabularyColumn):

    vocabulary = u'imio.project.pst.content.action.health_indicator_vocabulary'


class ProgressColumn(BaseColumn):

    pass


class ManagerColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.manager_vocabulary'


class TaskParentColumn(PrettyLinkColumn):

    params = {'showContentIcon': True, 'target': '_blank'}
    header = _cez('header_task_parent')

    def renderCell(self, item):
        obj = self._getObject(item)
        parent = ITaskMethods(obj).get_highest_task_parent(task=False)
        return PrettyLinkColumn.getPrettyLink(self, parent)


class AssignedGroupColumn(VocabularyColumn):

    vocabulary = u'imio.project.core.content.project.manager_vocabulary'


class AssignedUserColumn(MemberIdColumn):

    attrName = u'assigned_user'


class DueDateColumn(DateColumn):

    attrName = u'due_date'
