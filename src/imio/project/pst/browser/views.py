# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from os.path import dirname

from lxml.etree import XMLSyntaxError

from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from collective.eeafaceted.dashboard.browser.overrides import DashboardFacetedTableView as DFTV
from collective.z3cform.datagridfield import DataGridFieldFactory
from imio.helpers.content import get_vocab
from imio.helpers.content import transitions
from imio.project.core import _ as _c
from imio.project.core.config import SUMMARIZED_FIELDS
from imio.project.pst import _
from imio.project.pst.content.action import IPSTAction
from lxml import etree
from plone import api
from plone.app.versioningbehavior.browser import VersionView as OVV
from plone.supermodel import model
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import EditForm
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import NO_VALUE
from zope import schema
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified

logger = logging.getLogger('imio.project.pst: views')


class ArchiveView(BrowserView):
    """
        Common methods
    """

    def archive(self):
        """ """
        portal = api.portal.get()
        new_pst = api.content.copy(self.context, portal, 'pst-tmp', False)
        self.context = api.content.rename(self.context, 'pst-2012-2018')
        self.context.title = u'PST 2013-2018'
        self.context.reindexObject()
        new_pst = api.content.rename(new_pst, 'pst')
        new_pst.title = u'PST 2019-2024'
        new_pst.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
        new_pst.reindexObject()
        new_pst.reindexObjectSecurity()
        new_pst.budget_years = [2019, 2020, 2021, 2022, 2023, 2024]
        del_view = new_pst.restrictedTraverse('clean_budget/delete')
        for fld in SUMMARIZED_FIELDS:
            del_view(fld)
        transitions(new_pst, ['publish_internally'])
        return self.request.RESPONSE.redirect(new_pst.absolute_url())


class PSTExportAsXML(BrowserView):

    def __init__(self, context, request):
        super(PSTExportAsXML, self).__init__(context, request)
        self.ploneview = getMultiAdapter((context, request), name='plone')
        self.plan_vocab = get_vocab(self.context, 'imio.project.core.content.project.plan_vocabulary')
        self.manager_vocab = get_vocab(self.context, 'imio.project.core.content.project.manager_vocabulary')
        self.repr_resp_vocab = get_vocab(self.context, 'imio.project.pst.content.operational.representative_responsible_vocabulary')

    def __call__(self, *args, **kwargs):

        schema_file_path = dirname(__file__) + '/../model/schema_import_ecomptes_201805V1.xsd'
        schema_root = etree.parse(open(schema_file_path, 'rb'))
        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)

        raw_xml = self.index()
        parsed_xml = etree.fromstring(raw_xml.encode("utf8"), parser)  # if invalid, raises XMLSyntaxError

        # self.request.RESPONSE.setHeader("Content-type", "text/xml")  # open in browser
        now = datetime.now()
        self.request.RESPONSE.setHeader('Content-Disposition', 'attachment;filename="export_iApst_pour_ecomptes_{}'
                                        '.xml"'.format(now.strftime('%Y%m%d')))
        return raw_xml

    @property
    def identifiants(self):
        now = datetime.now()
        return {
            'identifiant_id': now.strftime('%Y%m%d'),
            'exercice': getattr(self.context, 'current_fiscal_year') or now.year,
            'INS': getattr(self.context, 'INS_code') or '99999',
        }

    @property
    def strategic_objectives(self):
        brains = api.content.find(
            self.context,
            depth=1,
            object_provides="imio.project.pst.content.strategic.IStrategicObjective",
            sort_on='getObjPositionInParent',
        )
        return [brain.getObject() for brain in brains]

    def operational_objectives(self, os):
        brains = api.content.find(
            os,
            depth=1,
            object_provides="imio.project.pst.content.operational.IOperationalObjective",
            sort_on='getObjPositionInParent',
        )
        return [brain.getObject() for brain in brains]

    def actions_and_subactions(self, oo):
        brains = api.content.find(
            oo, depth=1,
            object_provides='imio.project.pst.content.action.IPSTAction',
            sort_on='getObjPositionInParent',
        )
        ret = []
        for brain in brains:
            obj = brain.getObject()
            if base_hasattr(obj, '_link_portal_type'):
                continue  # we escape action_link
            ret.append(obj)
            sub_brains = api.content.find(obj, depth=1, object_provides='imio.project.pst.content.action.IPSTSubAction',
                                          sort_on='getObjPositionInParent')
            for sub_brain in sub_brains:
                subobj = sub_brain.getObject()
                if base_hasattr(subobj, '_link_portal_type'):
                    continue  # we escape subaction_link
                ret.append(subobj)
        return ret

    def status(self, element):
        element_state = api.content.get_state(element)
        ecompte_status = {
            'created': 'NON_COMMENCE',
            'ongoing': 'EN_COURS',
            'achieved': 'TERMINE',
            'stopped': 'PROBLEME',
            'terminated': 'TERMINE',
            'to_be_scheduled': 'EN_ATTENTE',
        }
        return ecompte_status.get(element_state)

    def responsable(self, element):
        if element.administrative_responsible:
            term_id = element.administrative_responsible[0]
            return self.manager_vocab.getTerm(term_id).title
        else:
            return None

    def mandataire(self, element, oo=None):
        if element.representative_responsible:
            term_id = element.representative_responsible[0]
            return self.repr_resp_vocab.getTerm(term_id).title
        elif oo and oo.representative_responsible:
            term_id = oo.representative_responsible[0]
            return self.repr_resp_vocab.getTerm(term_id).title
        else:
            return None

    def departement(self, element):
        if element.manager:
            for term_id in element.manager:
                if term_id in self.manager_vocab:
                    return self.manager_vocab.getTerm(term_id).title
                else:
                    tit = ''
                    brains = self.context.portal_catalog(UID=term_id)
                    if brains:
                        tit = brains[0].get_full_title
                    logger.warning(u"{}: manager org not found uid='{}', tit='{}'".format(element, term_id, tit))
        else:
            return None

    def action_begin_date(self, action):
        if action.effective_begin_date:
            return action.effective_begin_date
        else:
            return action.planned_begin_date

    def action_end_date(self, action):
        if action.effective_end_date:
            return action.effective_end_date
        else:
            return action.planned_end_date

    def exercice(self, element):
        return element.created().year()

    def libelle(self, element):
        if element.portal_type == 'strategicobjective':
            return self.ploneview.cropText('OS.{0} - {1}'.format(
                element.reference_number,
                element.title.encode('utf8'),
            ), 252)
        elif element.portal_type == 'operationalobjective':
            return self.ploneview.cropText('OO.{0} - {1}'.format(
                element.reference_number,
                element.title.encode('utf8'),
            ), 252)
        elif element.portal_type == 'pstaction':
            return self.ploneview.cropText('A.{0} - {1}'.format(
                element.reference_number,
                element.title.encode('utf8'),
            ), 252)
        elif element.portal_type == 'pstsubaction':
            action = element.__parent__
            return self.ploneview.cropText('A.{0} - SA.{1} - {2}'.format(
                action.reference_number,
                element.reference_number,
                element.title.encode('utf8'),
            ), 252)

    def progress(self, action):
        try:
            prog = int(action.progress or 0)
        except ValueError:
            return 0
        return prog

    def plans(self, element):
        plans = []
        if base_hasattr(element, 'plan') and element.plan is not None:
            for term_id in element.plan:
                plans.append(self.plan_vocab.getTerm(term_id).title)
        return plans

    def organization_type(self):
        return self.context.organization_type.upper()


class IPSTImportFromEcomptesSchema(model.Schema):

    ecomptes_xml = schema.Bytes(
        title=_c(u"XML document exported from eComptes"),
        description=u'',
        required=True,
    )


class PSTImportFromEcomptes(Form):
    label = _c(u"Import data from eComptes")
    fields = Fields(IPSTImportFromEcomptesSchema)
    ignoreContext = True

    def parse_xml(self, data):
        schema_file_path = dirname(__file__) + '/../model/PST_eComptes_Export_201805V1.xsd'
        schema_root = etree.parse(open(schema_file_path, 'rb'))
        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)
        raw_xml = data.get('ecomptes_xml')
        parsed_xml = etree.fromstring(raw_xml, parser)  # if invalid, raises XMLSyntaxError
        return parsed_xml

    def update_pst(self, ecomptes_xml):
        modifications = {}
        all_articles_xml = ecomptes_xml.findall('.//Articles')
        for articles_xml in all_articles_xml:
            if not articles_xml.getchildren():
                continue
            element_xml = articles_xml.getparent()
            uid = element_xml.get('ElementId')
            element_dx = api.content.get(UID=uid)

            if element_dx:
                element_dx_articles = []
                for article_xml in articles_xml:
                    year = int(article_xml.xpath("Exercice/text()")[0])
                    # elementtree must be encoded and decoded to get unicode and not object
                    service = article_xml.xpath("Service/text()")[0].encode('utf8').decode('utf8')
                    btype = article_xml.xpath("Type/text()")[0].encode('utf8').decode('utf8')
                    article = article_xml.xpath("CodeArticle/text()")[0].encode('utf8').decode('utf8')
                    title = article_xml.xpath("Libelle/text()")[0].encode('utf8').decode('utf8')
                    amount = float(article_xml.xpath("Montant/text()")[0])
                    element_dx_articles.append({
                        'year': year,
                        'service': service,
                        'btype': btype,
                        'article': article,
                        'title': title,
                        'amount': amount,
                        # 'comment': u'',  Removed from schema
                    })
                element_dx.analytic_budget = sorted(element_dx_articles,
                                                    cmp=lambda x, y: cmp((x['year'], y['service'], y['btype'],
                                                                          x['article']),
                                                                         (y['year'], x['service'], x['btype'],
                                                                          y['article'])))
                modifications[element_dx.absolute_url_path()] = element_dx

        all_projections_xml = ecomptes_xml.findall('.//Projections')
        for projections_xml in all_projections_xml:
            if not projections_xml.getchildren():
                continue
            element_xml = projections_xml.getparent()
            uid = element_xml.get('ElementId')
            element_dx = api.content.get(UID=uid)

            if element_dx:
                projections = []
                for projection_xml in projections_xml:
                    # elementtree must be encoded and decoded to get unicode and not object
                    service = projection_xml.xpath("Service/text()")[0].encode('utf8').decode('utf8')
                    btype = projection_xml.xpath("Type/text()")[0].encode('utf8').decode('utf8')
                    group = projection_xml.xpath("GroupeEco/text()")[0].encode('utf8').decode('utf8')
                    title = projection_xml.xpath("Libelle/text()")[0].encode('utf8').decode('utf8')
                    exercices_xml = projection_xml.find('.//Exercices')
                    for exercice_xml in exercices_xml or []:
                        year = int(exercice_xml.get('Valeur'))
                        amount = float(exercice_xml.xpath("Montant/text()")[0])
                        projections.append({
                            'service': service,
                            'btype': btype,
                            'group': group,
                            'title': title,
                            'year': year,
                            'amount': amount,
                        })
                element_dx.projection = projections
                modifications[element_dx.absolute_url_path()] = element_dx

        for path in reversed(modifications.keys()):
            modified(modifications[path])

    @button.buttonAndHandler(_c(u'Import'), name='import')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            try:
                parsed_xml = self.parse_xml(data)
            except XMLSyntaxError:
                IStatusMessage(self.request).addStatusMessage(
                    _c(u'The imported document is not recognized as a valid eComptes export.'),
                    'error',
                )
            else:
                self.update_pst(parsed_xml)
                IStatusMessage(self.request).addStatusMessage(
                    _c(u'The XML document has been successfully imported.'),
                    'info',
                )


class VersionView(OVV):
    """ override of call from 1.2.10 """

    def __call__(self):
        version_id = self.request.get('version_id', None)
        if not version_id:
            raise ValueError(u'Missing parameter on the request: version_id')

        content_core_view = getMultiAdapter((self.context, self.request), name='content-core-version')
        html = content_core_view()
        return self._convert_download_links(html, version_id)


class OSOOFacetedTableView(DFTV):
    """ """

    def _getViewFields(self):
        """ We don't show parents column """
        return [elt[0] for elt in self.collection.selectedViewFields() if elt[0] != 'parents']


class ActionFacetedTableView(DFTV):
    """ """

    def _getViewFields(self):
        """ We don"t show parents column on an action with tasks """
        if self.context.portal_type == 'pstsubaction' or not self.request.get('has_subaction'):
            return [elt[0] for elt in self.collection.selectedViewFields()]
        else:
            return [elt[0] for elt in self.collection.selectedViewFields() if elt[0] != 'parents']


class BudgetSplitForm(EditForm):

    label = _(u"Split action budget")
    fields = Fields(IPSTAction).select('budget_split')
    fields['budget_split'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        if base_hasattr(self.context, 'symbolic_link'):
            return self.context._link
        else:
            return self.context

    @button.buttonAndHandler(PMF('Save'), name='save')
    def handleAdd(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Budget split saved"),
            "info",
        )

    @button.buttonAndHandler(PMF(u'return_to_view'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.get('URL1'))

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widget.columns[0]['mode'] = HIDDEN_MODE
        widgets['uid'].mode = HIDDEN_MODE

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['budget_split'].allow_reorder = False
        self.widgets['budget_split'].allow_insert = False
        self.widgets['budget_split'].allow_delete = False
        self.widgets['budget_split'].auto_append = False
        # Prevent pickling error when auto_append = False
        self.widgets['budget_split'].value = [{} if raw == NO_VALUE else raw for raw in
                                              self.widgets['budget_split'].value]
