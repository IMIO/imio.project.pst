# -*- coding: utf-8 -*-
import os
from datetime import datetime

from collective.iconifiedcategory.utils import calculate_category_id
from imio.project.pst.utils import get_echevins_config
from plone import api, namedfile
from plone.namedfile.file import NamedBlobFile
from imio.helpers.content import richtextval
from . import add_path

TMPL_DIR = add_path('profiles/default/templates')


def get_styles_templates():
    return [
        {'cid': 1, 'cont': 'templates', 'id': 'style', 'title': u'Style général', 'type': 'StyleTemplate',
         'attrs': {'odt_file': NamedBlobFile(data=open('%s/style.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'style.odt', contentType='applications/odt')},
         'trans': ['publish_internally']},
        {'cid': 2, 'cont': 'templates', 'id': 'style_wo_nb', 'title': u'Style sans numérotation',
         'type': 'StyleTemplate',
         'attrs': {'odt_file': NamedBlobFile(data=open('%s/style_wo_nb.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'style_wo_nb.odt', contentType='applications/odt')},
         'trans': ['publish_internally']}
    ]


def get_main_templates(cids):
    return [
        {'cid': 10, 'cont': 'templates', 'id': 'detail', 'title': u'Détaillé', 'type': 'ConfigurablePODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'without_oo_fields', 'value': u','},
                   ],
                   'is_reusable': True,
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 30, 'cont': 'templates', 'id': 'follow', 'title': u'Suivi', 'type': 'ConfigurablePODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'is_reusable': True,
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 80, 'cont': 'templates', 'id': 'export', 'title': u'Export', 'type': 'ConfigurablePODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'pod_portal_types': ['pstprojectspace', 'strategicobjective',
                   'operationalobjective', 'pstaction', 'pstsubaction'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}],
                   'is_reusable': True,
                   'odt_file': NamedBlobFile(data=open('%s/export.ods' % TMPL_DIR, 'r').read(),
                                             filename=u'export.ods', contentType='applications/ods')}},

        {'cid': 90, 'cont': 'templates', 'id': 'managers', 'title': u'Suivi gestionnaires',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'pod_portal_types': ['pstaction', 'pstsubaction'], 'tal_condition': "python:"
                    "context.getPortalTypeName() == 'Folder' and context.getId() == 'pstactions'",
                   'is_reusable': True,
                   'odt_file': NamedBlobFile(data=open('%s/managers.ods' % TMPL_DIR, 'r').read(),
                                             filename=u'managers.ods', contentType='applications/ods')}},

        {'cid': 150, 'cont': 'templates', 'id': 'editors', 'title': u'Suivi editeurs',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'pod_portal_types': ['pstaction', 'pstsubaction'], 'tal_condition': "python:"
                    "context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks'",
                   'is_reusable': True,
                   'odt_file': NamedBlobFile(data=open('%s/editors.ods' % TMPL_DIR, 'r').read(),
                                             filename=u'editors.ods', contentType='applications/ods')}},
    ]


def get_templates(cids):
    return [
        {'cid': 15, 'cont': 'templates', 'id': 'detail-tasks', 'title': u'Détaillé avec tâches',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 20, 'cont': 'templates', 'id': 'ddetail', 'title': u'Détaillé', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or "
                   "context.getPortalTypeName() == 'pstsubaction')",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 25, 'cont': 'templates', 'id': 'ddetail-tasks', 'title': u'Détaillé avec tâches',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 35, 'cont': 'templates', 'id': 'follow-tasks', 'title': u'Suivi avec tâches',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},

        {'cid': 40, 'cont': 'templates', 'id': 'dfollow', 'title': u'Suivi', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or "
                   "context.getPortalTypeName() == 'pstsubaction')",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},

        {'cid': 45, 'cont': 'templates', 'id': 'dfollow-tasks', 'title': u'Suivi avec tâches',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},

        {'cid': 85, 'cont': 'templates', 'id': 'dexport', 'title': u'Export', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'tal_condition': "python:"
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or "
                   "context.getPortalTypeName() == 'pstsubaction') and "
                   "context.restrictedTraverse('pst-utils')"
                   ".is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}],
                   'pod_template_to_use': cids[80].UID()}},

        {'cid': 95, 'cont': 'templates', 'id': 'dmanagers', 'title': u'Suivi gestionnaires',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'tal_condition': "python:"
                   "context.getPortalTypeName() == 'Folder' and context.getId() == 'pstactions'",
                   'pod_template_to_use': cids[90].UID()}},

        {'cid': 155, 'cont': 'templates', 'id': 'deditors', 'title': u'Suivi éditeurs',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'tal_condition': "python:"
                    "context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks'",
                   'pod_template_to_use': cids[150].UID()}},

        {'cid': 100, 'cont': 'templates', 'id': 'detail-all', 'title': u'Détaillé (Tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 105, 'cont': 'templates', 'id': 'detail-tasks-all', 'title': u'Détaillé avec tâches (tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 110, 'cont': 'templates', 'id': 'ddetail-all', 'title': u'Détaillé (Tout)',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors']) and "
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or "
                   "context.getPortalTypeName() == 'pstsubaction')",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 115, 'cont': 'templates', 'id': 'ddetail-tasks-all', 'title': u'Détaillé avec tâches (Tout)',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'without_oo_fields', 'value': u','}
                   ],
                   'pod_template_to_use': cids[10].UID()}},

        {'cid': 120, 'cont': 'templates', 'id': 'follow-all', 'title': u'Suivi (Tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},

        {'cid': 125, 'cont': 'templates', 'id': 'follow-tasks-all', 'title': u'Suivi avec tâches (Tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['pstprojectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'],
                   'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},

        {'cid': 130, 'cont': 'templates', 'id': 'dfollow-all', 'title': u'Suivi (Tout)', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors']) and "
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "(context.getPortalTypeName() == 'pstaction' and not context.has_subactions()) or "
                   "context.getPortalTypeName() == 'pstsubaction')",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u''},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},

        {'cid': 135, 'cont': 'templates', 'id': 'dfollow-tasks-all', 'title': u'Suivi avec tâches (Tout)',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [
                       {'name': u'with_tasks', 'value': u'1'},
                       {'name': u'skip_states', 'value': u''},
                       {'name': u'option_0', 'value': u'1'},
                       {'name': u'option_1', 'value': u''},
                   ],
                   'pod_template_to_use': cids[30].UID()}},
    ]


def get_os_oo_ac_data(site, groups, currentYear):
    echevins = get_echevins_config(site)
    filename = u'annex_test.pdf'
    current_path = os.path.dirname(__file__)
    f = open(os.path.join(current_path, 'model', filename), 'r')
    annex_file = namedfile.NamedBlobFile(f.read(), filename=filename)
    return [
        {
            'title': u'Etre une commune qui offre un service public moderne, efficace et efficient',
            'categories': [u'volet-interne-adm-generale-amelioration-administration',
                           u'volet-interne-adm-generale-accessibilite-administration'],
            'budget': [{'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''}],
            'budget_comments': richtextval(u''),
            'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
            'operationalobjectives': [
                {
                    'title': u"Diminuer le temps d'attente de l'usager au guichet population de 20% dans les 12 mois "
                             u"à venir",
                    'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                   u'volet-interne-adm-generale-accessibilite-administration'],
                    u'result_indicator':
                    [
                        {'value': 20, 'label': u'Diminution du temps d\'attente (en %)', 'reached_value': 0,
                         'year': 2020},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2020, 12, 31)),
                    'representative_responsible': [echevins['1er-echevin']],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-population'], groups['service-etat-civil']],
                    'extra_concerned_people': u'',
                    'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''}],
                    'comments': richtextval(u''),
                    'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                    'actions': [
                        {'title': u'Engager 2 agents pour le Service Population',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 200.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 215.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear,
                              'budget_comment': u''},
                             {'amount': 250.0, 'budget_type': 'wallonie', 'year': currentYear+1, 'budget_comment': u''},
                             {'amount': 100.0, 'budget_type': 'europe', 'year': currentYear+1, 'budget_comment': u''},
                             {'amount': 115.50, 'budget_type': 'federation-wallonie-bruxelles',
                             'year': currentYear+1, 'budget_comment': u''},
                             {'amount': 1111.00, 'budget_type': 'province', 'year': currentYear+1,
                              'budget_comment': u''},
                             ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                         'annexes': [
                             {
                                 'id': 'annex_test',
                                 'title': u'Annex test',
                                 'content_category': calculate_category_id(
                                     site.categorization.annexes.get('annexes-pst')
                                 ),
                              'file': annex_file
                             }
                         ],
                         'tasks': [
                             {'title': u'Rédiger le profil de fonction',
                              'assigned_group': groups['service-population'], 'assigned_user': 'agent'},
                             {'title': u'Ajouter une annonce sur le site internet',
                              'assigned_group': groups['service-informatique']},
                         ]
                         },
                        {'title': u'Créer un guichet supplémentaire dans les 3 mois',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 200.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 215.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear,
                              'budget_comment': u''},
                             {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear, 'budget_comment': u''},
                            ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                         'tasks': [
                             {'title': u'Réparer le guichet',
                              'assigned_group': groups['service-travaux']},
                         ]
                         },
                        {'title': u'Mettre en ligne sur le site internet différents documents "population" à '
                                  u'télécharger de chez soi',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2020, 9, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 1500.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 18500.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 2000.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear,
                              'budget_comment': u''},
                             {'amount': 3000.0, 'budget_type': 'province', 'year': currentYear, 'budget_comment': u''},
                            ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'sdgs': ['13'],
                         'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                         'tasks': [
                             {'title': u'Expliquer au service comment éditer sur le site internet',
                              'assigned_group': groups['service-informatique']},
                         ]
                         },
                    ]
                },
                {
                    'title': u'Optimiser l\'accueil au sein de l\'administration communale',
                    'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                   u'volet-interne-adm-generale-accessibilite-administration'],
                    u'result_indicator':
                    [
                        {'value': 50, 'label': u'Pourcentage minimum de visiteurs satisfaits (document de satisfaction '
                                               u'à remplir) sur un an', 'reached_value': 0, 'year': 2020},
                        {'value': 5, 'label': u'Pourcentage maximum de plaintes (document de plainte à disposition)',
                         'reached_value': 0, 'year': 2020},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2020, 12, 31)),
                    'representative_responsible': [echevins['1er-echevin']],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-population'], groups['service-etat-civil']],
                    'extra_concerned_people': u'',
                    'budget': [],
                    'comments': richtextval(u''),
                    'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                    'actions': [
                        {'title': u'Placer des pictogrammes de guidance',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 50.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 250.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 15.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear,
                              'budget_comment': u''},
                             {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear+1, 'budget_comment': u''},
                            ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'sdgs': ['10'],
                         'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                         'tasks': [
                             {'title': u'Acheter/fournir des pictogrammes de guidance',
                              'assigned_group': groups['service-travaux']},
                             {'title': u'Analyser où placer les pictogrammes',
                              'assigned_group': groups['service-population']},
                             {'title': u'Fixer les pictogrammes de guidance',
                              'assigned_group': groups['service-travaux']},
                         ]
                         },
                        {'title': u'Installer une rampe d\'accès pour PMR',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-population'], groups['service-travaux']],
                         'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 600.0, 'budget_type': 'wallonie', 'year': currentYear+1, 'budget_comment': u''},
                             {'amount': 841.0, 'budget_type': 'europe', 'year': currentYear+1, 'budget_comment': u''},
                             {'amount': 1552.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear+1,
                              'budget_comment': u''},
                             {'amount': 123.0, 'budget_type': 'ville', 'year': currentYear+1, 'budget_comment': u''},
                            ],
                         'health_indicator': u'risque',
                         'health_indicator_details': u'Problème, retard dû à l\'exécution du marché',
                         'comments': richtextval(u''),
                         'sdgs': ['10'],
                         'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                         },
                        {'title': u'Mettre en place des permanences sur rendez-vous',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2020, 9, 30)),
                         'extra_concerned_people': u'',
                         'budget': [],
                         'health_indicator': u'risque',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'plan': [u'plan-de-formation-du-personnel', u'plan-de-gestion'],
                         'tasks': [
                             {'title': u'Établir le mode de fonctionnement pour les permanences',
                              'assigned_group': groups['secretariat-communal']},
                         ]
                         },
                    ]
                },
            ],
        },
        {
            'title': u'Etre une commune qui s\'inscrit dans la lignée des accords de réductions '
                     u'des gaz à effet de serre afin d\'assurer le développement durable',
            'categories': [u'volet-externe-dvp-politiques-energie', u'volet-externe-dvp-politiques-environnement'],
            'budget': [],
            'budget_comments': richtextval(u''),
            'operationalobjectives': [
                {
                    'title': u'Doter la commune de compétences en matière énergétique pour fin 2021 compte tenu du '
                             u'budget',
                    'categories': [u'volet-externe-dvp-politiques-energie',
                                   u'volet-externe-dvp-politiques-environnement'],
                    u'result_indicator':
                    [
                        {'value': 2, 'label': u'Nombre de personnes engagées fin 2021', 'reached_value': 0,
                         'year': 2020},
                        {'value': 8, 'label': u'Nombre de personnes formées fin 2021', 'reached_value': 0,
                         'year': 2020},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2021, 12, 31)),
                    'representative_responsible': [echevins['4eme-echevin']],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-de-lurbanisme']],
                    'extra_concerned_people': u'',
                    'budget': [],
                    'comments': richtextval(u''),
                    'sdgs': ['13'],
                    'actions': [
                        {'title': u'Procéder à l\'engagement d\'un conseiller en énergie',
                         'categories': [u'volet-externe-dvp-politiques-energie',
                                        u'volet-externe-dvp-politiques-environnement'],
                         'manager': [groups['service-de-lurbanisme'], ],
                         'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'sdgs': ['13'],
                         'tasks': [
                             {'title': u'Rédiger le profil de fonction de conseiller en énergie',
                              'assigned_group': groups['service-population']},
                             {'title': u'Ajouter une annonce sur le site internet',
                              'assigned_group': groups['service-informatique']},
                         ]
                         },
                        {'title': u'Répondre à l\'appel à projet "écopasseur" de la Wallonie',
                         'categories': [u'volet-externe-dvp-politiques-energie',
                                        u'volet-externe-dvp-politiques-environnement'],
                         'manager': [groups['service-de-lurbanisme'], ],
                         'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 0.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 50.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 5.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear,
                              'budget_comment': u''},
                             {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear+1, 'budget_comment': u''},
                            ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'sdgs': ['13'],
                         },
                        {'title': u'Inscrire systématiquement les agents du service travaux aux formations '
                                  u'énergétiques',
                         'categories': [u'volet-externe-dvp-politiques-energie',
                                        u'volet-externe-dvp-politiques-environnement'],
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2020, 9, 30)),
                         'extra_concerned_people': u'',
                         'budget': [
                             {'amount': 550.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 5250.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 515.55, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear+1,
                              'budget_comment': u''},
                             {'amount': 5215.0, 'budget_type': 'ville', 'year': currentYear+1, 'budget_comment': u''},
                            ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'sdgs': ['13'],
                         },
                    ]
                },
                {
                    'title': u'Réduire la consommation énergétique des bâtiments communaux de 20% d\'ici 2024',
                    'categories': [u'volet-externe-dvp-politiques-energie',
                                   u'volet-externe-dvp-politiques-environnement'],
                    u'result_indicator':
                    [
                        {'value': 20000, 'label': u'Diminution du nombre de litres de mazout au 31 12 2020',
                         'reached_value': 0, 'year': 2020},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2024, 12, 31)),
                    'representative_responsible': [echevins['1er-echevin']],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-de-lurbanisme']],
                    'extra_concerned_people': u'',
                    'budget': [],
                    'comments': richtextval(u''),
                    'sdgs': ['13'],
                    'actions': [
                        {
                            'title': u'Réduire la consommation énergétique de l\'administration communale',
                            'categories': [u'volet-externe-dvp-politiques-energie',
                                           u'volet-externe-dvp-politiques-environnement'],
                            'manager': [groups['service-de-lurbanisme'], ],
                            'planned_end_date': datetime.date(datetime(2024, 06, 30)),
                            'extra_concerned_people': u'',
                            'health_indicator': u'bon',
                            'health_indicator_details': u'',
                            'comments': richtextval(u''),
                            'sdgs': ['13'],
                            'subactions': [{
                                'title': u'Réaliser un audit énergétique du bâtiment',
                                'categories': [u'volet-externe-dvp-politiques-energie',
                                               u'volet-externe-dvp-politiques-environnement'],
                                'manager': [groups['service-de-lurbanisme'], ],
                                'planned_end_date': datetime.date(datetime(2020, 06, 30)),
                                'extra_concerned_people': u'',
                                'budget': [
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear,
                                     'budget_comment': u''},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+1,
                                     'budget_comment': u''},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+2,
                                     'budget_comment': u''},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+3,
                                     'budget_comment': u''},
                                ],
                                'health_indicator': u'bon',
                                'health_indicator_details': u'',
                                'comments': richtextval(u''),
                                'sdgs': ['13'],
                                'tasks': [
                                    {'title': u'Écrire le cahier des charges',
                                     'assigned_group': groups['cellule-marches-publics'],
                                     'due_date': datetime.date(datetime(2020, 04, 30))},
                                    {'title': u'Choisir le prestataire',
                                     'assigned_group': groups['service-de-lurbanisme'],
                                     'due_date': datetime.date(datetime(2020, 03, 31))},
                                ]},
                                {'title': u'En fonction des résultats, procéder à l\'isolation du bâtiment',
                                 'categories': [u'volet-externe-dvp-politiques-energie',
                                                u'volet-externe-dvp-politiques-environnement'],
                                 'manager': [groups['service-travaux']],
                                 'planned_end_date': datetime.date(datetime(2020, 10, 31)),
                                 'extra_concerned_people': u'',
                                 'budget': [
                                     {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear,
                                      'budget_comment': u''},
                                     {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+1,
                                      'budget_comment': u''},
                                     {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+2,
                                      'budget_comment': u''},
                                     {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+3,
                                      'budget_comment': u''},
                                    ],
                                 'health_indicator': u'bon',
                                 'health_indicator_details': u'',
                                 'comments': richtextval(u''),
                                 'sdgs': ['13'],
                                 },
                                {'title': u'En fonction des résultats, remplacer le système de chauffage',
                                 'categories': [u'volet-externe-dvp-politiques-energie',
                                                u'volet-externe-dvp-politiques-environnement'],
                                 'manager': [groups['service-population'], ],
                                 'planned_end_date': datetime.date(datetime(2020, 10, 31)),
                                 'extra_concerned_people': u'',
                                 'budget': [
                                     {'amount': 500.0, 'budget_type': 'europe', 'year': currentYear+2,
                                      'budget_comment': u''},
                                     {'amount': 500.0, 'budget_type': 'federal', 'year': currentYear+2,
                                      'budget_comment': u''},
                                     {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+2,
                                      'budget_comment': u''},
                                     {'amount': 500.0, 'budget_type': 'autres', 'year': currentYear+2,
                                      'budget_comment': u''},
                                    ],
                                 'health_indicator': u'bon',
                                 'health_indicator_details': u'Devenu sans objet compte tenu des résultats de l\'audit',
                                 'comments': richtextval(u''),
                                 'sdgs': ['13'],
                                 },
                            ]
                        },
                        {
                            'title': u'Réduire la consommation énergétique du hangar communal',
                            'categories': [u'volet-externe-dvp-politiques-energie',
                                           u'volet-externe-dvp-politiques-environnement'],
                            'manager': [groups['service-de-lurbanisme'], ],
                            'planned_end_date': datetime.date(datetime(2024, 06, 30)),
                            'extra_concerned_people': u'',
                            'health_indicator': u'bon',
                            'health_indicator_details': u'',
                            'comments': richtextval(u''),
                            'sdgs': ['13'],
                            'subactions_link': [
                            ]
                        },
                    ]
                },
            ],
        },
        {
            'title': u'Etre une commune où il fait bon vivre dans un cadre agréable, propre et en toute sécurité',
            'categories': [u'volet-externe-dvp-politiques-proprete-securite-publique',
                           u'volet-externe-dvp-politiques-amenagement-territoire'],
            'budget': [],
            'budget_comments': richtextval(u''),
            'operationalobjectives': [
                {
                    'title': u'Assurer la propreté dans l\'ensemble des parcs de la commune de manière à '
                             u'réduire la présence de déchets de 90% au 31 12 2022',
                    'categories': [u'volet-externe-dvp-politiques-proprete-securite-publique',
                                   u'volet-externe-dvp-politiques-amenagement-territoire'],
                    u'result_indicator': [{'value': 50, 'label': u'Nombre de sacs poubelles récoltés '
                                          u'chaque année et à l\'échéance (31 12 2022)',
                                          'reached_value': 0, 'year': 2020}],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2022, 12, 31)),
                    'representative_responsible': [echevins['2eme-echevin'], echevins['3eme-echevin']],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-proprete'], groups['service-travaux']],
                    'extra_concerned_people': u'Police\r\nAgents constatateurs communaux\r\nAgent sanctionnateur '
                                              u'communal\r\nStewards urbains',
                    'budget': [],
                    'budget_comments': richtextval(u'Fonds propres (en cours de chiffrage) et subventions (dossier '
                                                   u'introduit pour l\'engagement de deux stewards urbains)'),
                    'comments': richtextval(u''),
                    'sdgs': ['03', '11'],
                    'actions': [
                        {'title': u'Installer des distributeurs de sacs "ramasse crottes", dans les parcs '
                                  u'(entrée et sortie)',
                         'categories': [u'volet-interne-adm-generale-amelioration-administration',
                                        u'volet-interne-adm-generale-accessibilite-administration'],
                         'manager': [groups['service-proprete'], ],
                         'planned_end_date': datetime.date(datetime(2021, 06, 30)),
                         'extra_concerned_people': u'La firme adjudicatrice au terme du marché public',
                         'budget': [
                             {'amount': 12500.0, 'budget_type': 'wallonie', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 2500.0, 'budget_type': 'europe', 'year': currentYear, 'budget_comment': u''},
                             {'amount': 250.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': currentYear,
                              'budget_comment': u''},
                             {'amount': 250.0, 'budget_type': 'province', 'year': currentYear, 'budget_comment': u''},
                            ],
                         'budget_comments': richtextval(u'1000 euros\r\nBudget ordinaire\r\nArticle budgétaire '
                                                        u'n°: ...'),
                         'health_indicator': u'risque',
                         'health_indicator_details': u'Agent traitant malade pour minimum 3 mois -> risque de retard '
                                                     u'dans le planning',
                         'comments': richtextval(u'Attendre le placement des nouvelles poubelles (avant le '
                                                 u'01/12/2020)'),
                         'sdgs': ['11'],
                         'tasks': [
                             {'title': u'Commander des distributeurs de sacs',
                              'assigned_group': groups['service-travaux']},
                             {'title': u'Placer les distributeurs de sacs',
                              'assigned_group': groups['service-travaux']},
                         ]
                         },
                    ]
                },
            ],
        },
    ]

# SDGS
# 01 Pas de pauvreté
# 02 Faim \"zéro\"
# 03 Bonne santé et bien-être
# 04 Éducation de qualité
# 05 Égalité entre les sexes
# 06 Eau propre et assainissement
# 07 Énergie propre et d'un coût abordable
# 08 Travail décent et croissance économique
# 09 Industrie, innovation et infrastructure
# 10 Inégalités réduites
# 11 Villes et communautés durables
# 12 Consommation et production responsables
# 13 Mesures relatives à la lutte contre les changements climatiques
# 14 Vie aquatique
# 15 Vie terrestre
# 16 Paix, justice et institutions efficaces
# 17 Partenariats pour la réalisation des objectifs
