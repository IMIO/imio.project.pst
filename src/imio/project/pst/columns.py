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
from imio.project.core.utils import getProjectSpace
from imio.project.pst.adapters import UNSET_DATE_VALUE
from zope.component import getMultiAdapter

import cgi


class HistoryActionsColumn(ActionsColumn):

    params = {'showHistory': True, 'showActions': True}

    def renderCell(self, item):
        self.params['showArrows'] = (self.request.form.get('c0[]', '') == 'getObjPositionInParent')
        return super(HistoryActionsColumn, self).renderCell(item)


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


class ParentsColumn(BaseColumn):

    sort_index = 'path'

    def __init__(self, context, request, table):
        super(ParentsColumn, self).__init__(context, request, table)
        self.ploneview = getMultiAdapter((context, request), name='plone')

    def renderCell(self, item):
        ret = []
        obj = self._getObject(item)
        if item.portal_type == 'pstaction':
            parent = obj.aq_inner.aq_parent
            if getattr(getProjectSpace(self), 'use_ref_number', True):
                title = u'OO.{}'.format(parent.reference_number)
            else:
                title = u'OO: {}'.format(self.ploneview.cropText(parent.title, 35))
            ret.append(u'<a href="{}" target="_blank" title="{}">'
                       u'<span class="pretty_link_content">{}</span></a>'.format(parent.absolute_url(),
                                                                                 cgi.escape(parent.title,
                                                                                            quote=True),
                                                                                 title))
            obj = parent
        if item.portal_type in ('operationalobjective', 'pstaction'):
            parent = obj.aq_inner.aq_parent
            if getattr(getProjectSpace(self), 'use_ref_number', True):
                title = u'OS.{}'.format(parent.reference_number)
            else:
                title = u'OS: {}'.format(self.ploneview.cropText(parent.title, 35))
            ret.insert(0, u'<a href="{}" target="_blank" title="{}">'
                       u'<span class="pretty_link_content">{}</span></a>'.format(parent.absolute_url(),
                                                                                 cgi.escape(parent.title,
                                                                                            quote=True),
                                                                                 title))
        if ret:
            return '<ul class="parents_col"><li>%s</li></ul>' % ('</li>\n<li>'.join(ret))
        else:
            return '-'


class SubOrganizationTitle(PrettyLinkColumn):
    """
        Do not use OrgaPrettyLinkWithAdditionalInfosColumn
    """

    def contentValue(self, item):
        """Display get_full_title instead title."""
        path = '/'.join(item.getPhysicalPath())
        prefix = u''
        if (path.endswith('/plonegroup-organization/echevins') or path.endswith('/plonegroup-organization/services')):
            prefix = u'=> '
        return u'{2}{0} <span class="discreet">({1})</span>'.format(
            item.get_full_title(first_index=1), item.UID(), prefix)
