# -*- coding: utf-8 -*-
"""Custom columns."""
from collective.eeafaceted.z3ctable import _ as _cez
from collective.eeafaceted.z3ctable.columns import ActionsColumn
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import IconsColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import PrettyLinkColumn
from collective.eeafaceted.z3ctable.columns import VocabularyColumn
from collective.task.interfaces import ITaskMethods
from DateTime import DateTime
from imio.prettylink.interfaces import IPrettyLink
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.pst.adapters import UNSET_DATE_VALUE
from plone import api
from Products.CMFPlone.utils import base_hasattr
from zope.i18n import translate
from zope.component import getMultiAdapter

import cgi


class IconTitleColumn(PrettyLinkColumn):
    params = {'showContentIcon': True, 'display_tag_title': False}


class ActionIconTitleColumn(PrettyLinkColumn):

    def getPrettyLink(self, item):
        pl = IPrettyLink(item)
        pl.display_tag_title = False
        if base_hasattr(pl.context, '_link_portal_type'):
            pl.additionalCSSClasses = ['contenttype-{}'.format(pl.context._link_portal_type)]
        else:
            pl.additionalCSSClasses = ['contenttype-{}'.format(pl.context.portal_type)]
        pl.contentValue = self.contentValue(item)
        return pl.getLink()


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

    def getCSSClasses(self, item):
        css = self.cssClasses.copy()
        value = self.getValue(item)
        if not value or value == 'None' or value == self.ignored_value:
            td = css.get('td', None)
            if td:
                td = td + '_warn'
                css.update({'td': td})
        return css

    def renderCell(self, item):
        res = u'-'
        value = self.getValue(item)
        if not value or value == 'None' or value == self.ignored_value:
            item_obj = item.getObject()
            if item_obj.portal_type == 'operationalobjective':
                value = item_obj.get_max_planned_end_date_of_contained_brains(
                    ["pstaction", "action_link", "pstsubaction", "subaction_link"])
            elif item_obj.portal_type == 'pstaction':
                value = item_obj.get_max_planned_end_date_of_contained_brains(["pstsubaction", "subaction_link"])
        if value:
            if isinstance(value, DateTime):
                value = value.asdatetime().date()
            res = api.portal.get_localized_time(datetime=value, long_format=self.long_format, time_only=self.time_only)
            if self.use_caching:
                cached_result = self._get_cached_result(value)
                if cached_result:
                    res = cached_result
                else:
                    self._store_cached_result(value, res)
        return res


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


class ResponsibleColumn(VocabularyColumn):
    vocabulary = u'imio.project.pst.ActionEditorsVocabulary'


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
    """
        * always rendered on searches
        * only rendered on context when displaying tasks
    """

    sort_index = 'path'

    def __init__(self, context, request, table):
        super(ParentsColumn, self).__init__(context, request, table)
        self.ploneview = getMultiAdapter((context, request), name='plone')

    def get_parents(self, ret, obj):
        parent = obj.aq_inner.aq_parent
        while not IProjectSpace.providedBy(parent):
            title = u' {}'.format(self.ploneview.cropText(parent.title, 35))
            ret.append(u'<a href="{}" target="_blank" title="{}" class="contenttype-{}">'
                       u'<span class="pretty_link_content">{}</span></a>'.format(parent.absolute_url(),
                                                                                 cgi.escape(parent.title,
                                                                                            quote=True),
                                                                                 parent.portal_type,
                                                                                 title))
            parent = parent.aq_inner.aq_parent

    def renderCell(self, item):
        ret = []
        obj = self._getObject(item)
        # task dashboard
        if item.portal_type == 'task':
            parent = obj.aq_inner.aq_parent
            # walking on tasks
            while parent.portal_type not in ('pstaction', 'pstsubaction'):
                title = u' {}'.format(self.ploneview.cropText(parent.title, 35))
                ret.append(u'<a href="{}" target="_blank" title="{}" class="contenttype-task">'
                           u'<span class="pretty_link_content">{}</span></a>'.format(parent.absolute_url(),
                                                                                     cgi.escape(parent.title,
                                                                                                quote=True),
                                                                                     title))
                obj = parent
                parent = parent.aq_inner.aq_parent
            # on a search : adding action level
            if self.context.portal_type not in ('pstaction', 'pstsubaction'):
                self.get_parents(ret, obj)
        else:
            self.get_parents(ret, obj)

        if ret:
            return '<ul class="parents_col"><li>%s</li></ul>' % ('</li>\n<li>'.join(reversed(ret)))
        else:
            return '-'


class SubOrganizationTitle(PrettyLinkColumn):
    """
        Do not use OrgaPrettyLinkWithAdditionalInfosColumn
    """

    def contentValue(self, item):
        """Display get_full_title instead title."""
        path = '/'.join(item.getPhysicalPath())
        title = item.get_full_title(first_index=1)
        if (path.endswith('/plonegroup-organization/echevins') or path.endswith('/plonegroup-organization/services')):
            title = u'<span class="pg_org_category">=> {0}</span>'.format(title)
        return u'{0} <span class="discreet">({1})</span>'.format(title, item.UID())


class SDGsColumn(IconsColumn):
    attrName = u'sdgs'

    def titleValue(self, item, val):
        return translate(u'{}_title'.format(val), domain='collective.behavior.sdg', context=self.request)

    def srcValue(self, item, val):
        return '{}/++resource++collective.behavior.sdg/sdg-{}-nb.svg'.format(self.table.portal_url, val)
