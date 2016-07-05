from datetime import datetime

from collective.excelexport.datasources.base import BaseContentsDataSource
from collective.excelexport.exportables.base import BaseExportableFactory
from collective.excelexport.exportables.dexterityfields import ChoiceFieldRenderer
from collective.excelexport.exportables.dexterityfields import CollectionFieldRenderer
from collective.excelexport.exportables.dexterityfields import DateFieldRenderer
from collective.excelexport.exportables.dexterityfields import FieldRenderer
from collective.excelexport.exportables.dexterityfields import RichTextFieldRenderer
from collective.excelexport.exportables.dexterityfields import get_ordered_fields
from collective.excelexport.exportables.dexterityfields import get_exportable
from collective.excelexport.exportables.dexterityfields import ParentField
from collective.excelexport.exportables.dexterityfields import GrandParentField
from collective.excelexport.interfaces import IStyles
from zope.component import getAdapter
from plone.dexterity.interfaces import IDexterityFTI

from imio.project.core.content.projectspace import IProjectSpace

from plone import api

from zope.interface import Interface
from zope.component import adapts
from zope.component import getMultiAdapter


def _render_header(renderer, exportable):
    header = renderer.render_header(exportable)
    if exportable.portal_type == 'strategicobjective':
        header = u'O.S. ' + header
    if exportable.portal_type == 'operationalobjective':
        header = u'O.O. ' + header
    if exportable.portal_type == 'pstaction':
        header = u'A. ' + header
    return header


class PSTActionContentsDataSource(BaseContentsDataSource):
    """Export the contents of a pst folder
    """
    adapts(IProjectSpace, Interface)

    excluded_factories = u'fields'
    excluded_exportables = [
                'effective',
                'expires',
                'categories',
                'budget',
                'budget_comments',
                'visible_for',
                'observation',
                'comments',
                'health_indicator_details',
                'work_plan',
                'language',
                'contributors',
                'rights',
                'changeNote',
                'description',
                'subjects',
                ]

    def get_filename(self):
        return "%s-%s.xls" % (
                datetime.now().strftime("%d-%m-%Y"), self.context.getId())

    def get_objects(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='pstaction')
        return [b.getObject() for b in brains]


class PSTActionFieldsFactory(BaseExportableFactory):
    adapts(IDexterityFTI, Interface, Interface)
    portal_types = ('pstaction',)

    def get_exportables(self):
        portal_types = api.portal.get_tool('portal_types')
        action_fti = portal_types['pstaction']
        oo_fti = portal_types['operationalobjective']
        os_fti = portal_types['strategicobjective']
        fields = []
        fields.extend([get_exportable(
            field[1], self.context, self.request)
            for field in get_ordered_fields(action_fti)])
        fields.extend([get_exportable(
            ParentField(field[1]), self.context, self.request)
            for field in get_ordered_fields(oo_fti)])
        fields.extend([get_exportable(
            GrandParentField(field[1]), self.context, self.request)
            for field in get_ordered_fields(os_fti)])
        return fields


class PSTReferenceNumberRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTCategoriesRenderer(ChoiceFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(ChoiceFieldRenderer, self)


class PSTPriorityRenderer(ChoiceFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(ChoiceFieldRenderer, self)


class PSTBudgetRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTBudgetCommentsRenderer(RichTextFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(RichTextFieldRenderer, self)


class PSTManagerRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTVisibleForRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTExtraConcernedPeopleRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTResultIndicatorRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTPlannedBeginDateRenderer(DateFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(DateFieldRenderer, self)


class PSTEffectiveBeginDateRenderer(DateFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(DateFieldRenderer, self)


class PSTPlannedEndDateRenderer(DateFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(DateFieldRenderer, self)


class PSTEffectiveEndDateRenderer(DateFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(DateFieldRenderer, self)


class PSTProgressRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTObservationRenderer(RichTextFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(RichTextFieldRenderer, self)


class PSTCommentsRenderer(RichTextFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(RichTextFieldRenderer, self)


class PSTRepresentativeResponsibleRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTAdministrativeResponsibleRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTHealthIndicatorRenderer(ChoiceFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(ChoiceFieldRenderer, self)


class PSTHealthIndicatorDetailsRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTWorkPlanRenderer(RichTextFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(RichTextFieldRenderer, self)


class PSTTitleRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTDescriptionRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTSubjectsRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTLanguageRenderer(ChoiceFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(ChoiceFieldRenderer, self)


class PSTCreatorsRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)


class PSTContributorsRenderer(CollectionFieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)

    def render_header(self):
        return _render_header(CollectionFieldRenderer, self)

class PSTRightsRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)


class PSTChangeNoteRenderer(FieldRenderer):
    def render_style(self, obj, base_style):
        self.portal_type = obj.portal_type
        return getAdapter(self, interface=IStyles, name=obj.portal_type)
    def render_header(self):
        return _render_header(FieldRenderer, self)
