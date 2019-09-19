# -*- coding: utf-8 -*-

from datetime import datetime
from plone.namedfile.file import NamedBlobFile
from imio.helpers.content import richtextval
from . import add_path

TMPL_DIR = add_path('profiles/default/templates')


def get_styles_templates():
    return [
        {'cid': 1, 'cont': 'templates', 'id': 'style', 'title': u'Style général', 'type': 'StyleTemplate',
         'attrs': {'odt_file': NamedBlobFile(data=open('%s/style.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'style.odt', contentType='applications/odt')},
         'trans': ['publish_internally']}
    ]


def get_templates(cids):
    return [
        {'cid': 10, 'cont': 'templates', 'id': 'detail', 'title': u'Détaillé', 'type': 'ConfigurablePODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'],
                   'context_variables': [{'name': u'with_tasks', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 15, 'cont': 'templates', 'id': 'detail-tasks', 'title': u'Détaillé avec tâches',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'],
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 20, 'cont': 'templates', 'id': 'ddetail', 'title': u'Détaillé', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "context.getPortalTypeName() == 'pstaction')",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 25, 'cont': 'templates', 'id': 'ddetail-tasks', 'title': u'Détaillé avec tâches',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "",
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 30, 'cont': 'templates', 'id': 'follow', 'title': u'Suivi', 'type': 'ConfigurablePODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'],
                   'context_variables': [{'name': u'with_tasks', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 35, 'cont': 'templates', 'id': 'follow-tasks', 'title': u'Suivi avec tâches',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'],
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 40, 'cont': 'templates', 'id': 'dfollow', 'title': u'Suivi', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "context.getPortalTypeName() == 'pstaction')",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 45, 'cont': 'templates', 'id': 'dfollow-tasks', 'title': u'Suivi avec tâches',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "",
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 80, 'cont': 'templates', 'id': 'export', 'title': u'Export', 'type': 'ConfigurablePODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'pod_portal_types': ['projectspace', 'strategicobjective',
                   'operationalobjective', 'pstaction'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'odt_file': NamedBlobFile(data=open('%s/export.ods' % TMPL_DIR, 'r').read(),
                                             filename=u'export.ods', contentType='applications/ods')}},

        {'cid': 85, 'cont': 'templates', 'id': 'dexport', 'title': u'Export', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'pod_formats': ['ods'], 'tal_condition': "python:"
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "context.getPortalTypeName() == 'pstaction') and context.restrictedTraverse('pst-utils')"
                   ".is_in_user_groups(user=member, groups=['pst_editors'])",
                   'odt_file': NamedBlobFile(data=open('%s/export.ods' % TMPL_DIR, 'r').read(),
                                             filename=u'export.ods', contentType='applications/ods')}},

        {'cid': 100, 'cont': 'templates', 'id': 'detail-all', 'title': u'Détaillé (Tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}, {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 105, 'cont': 'templates', 'id': 'detail-tasks-all', 'title': u'Détaillé avec tâches (tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'},
                                         {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 110, 'cont': 'templates', 'id': 'ddetail-all', 'title': u'Détaillé (Tout)',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors']) and "
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "context.getPortalTypeName() == 'pstaction')",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}, {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 115, 'cont': 'templates', 'id': 'ddetail-tasks-all', 'title': u'Détaillé avec tâches (Tout)',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'},
                                         {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/detail.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'detail.odt', contentType='applications/odt')}},

        {'cid': 120, 'cont': 'templates', 'id': 'follow-all', 'title': u'Suivi (Tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}, {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 125, 'cont': 'templates', 'id': 'follow-tasks-all', 'title': u'Suivi avec tâches (Tout)',
         'type': 'ConfigurablePODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'pod_portal_types': ['projectspace',
                   'strategicobjective', 'operationalobjective', 'pstaction'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'},
                                         {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 130, 'cont': 'templates', 'id': 'dfollow-all', 'title': u'Suivi (Tout)', 'type': 'DashboardPODTemplate',
         'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors']) and "
                   "not((context.getPortalTypeName() == 'Folder' and context.getId() == 'tasks') or "
                   "context.getPortalTypeName() == 'pstaction')",
                   'context_variables': [{'name': u'with_tasks', 'value': u''}, {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},

        {'cid': 135, 'cont': 'templates', 'id': 'dfollow-tasks-all', 'title': u'Suivi avec tâches (Tout)',
         'type': 'DashboardPODTemplate', 'trans': ['publish_internally'],
         'attrs': {'style_template': [cids[1].UID()], 'pod_formats': ['odt'], 'tal_condition': "python:"
                   "context.restrictedTraverse('pst-utils').is_in_user_groups(user=member, groups=['pst_editors'])",
                   'context_variables': [{'name': u'with_tasks', 'value': u'1'},
                                         {'name': u'skip_states', 'value': u''}],
                   'odt_file': NamedBlobFile(data=open('%s/suivi.odt' % TMPL_DIR, 'r').read(),
                                             filename=u'suivi.odt', contentType='applications/odt')}},
    ]


def get_os_oo_ac_data(groups, currentYear):
    return [
        {
            'title': u'Etre une commune qui offre un service public moderne, efficace et efficient',
            'categories': [u'volet-interne-adm-generale-amelioration-administration',
                           u'volet-interne-adm-generale-accessibilite-administration'],
            'budget': [{'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear}],
            'budget_comments': richtextval(u''),
            'operationalobjectives': [
                {
                    'title': u"Diminuer le temps d'attente de l'usager au guichet population de 20% dans les 12 mois "
                             u"à venir",
                    u'result_indicator':
                    [
                        {'value': 20, 'label': u'Diminution du temps d\'attente (en %)', 'reached_value': 0},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2013, 12, 31)),
                    'representative_responsible': ['1er-echevin'],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-population'], groups['service-etat-civil']],
                    'extra_concerned_people': u'',
                    'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear}],
                    'comments': richtextval(u''),
                    'actions': [
                        {'title': u'Engager 2 agents pour le Service Population',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 200.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 215.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear},
                                    {'amount': 250.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                    {'amount': 100.0, 'budget_type': 'europe', 'year': currentYear+1},
                                    {'amount': 115.50, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear+1},
                                    {'amount': 1111.00, 'budget_type': 'province', 'year': currentYear+1},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'tasks': [
                             {'title': u'Rédiger le profil de fonction',
                              'assigned_group': groups['service-population'], 'assigned_user': 'agent'},
                             {'title': u'Ajouter une annonce sur le site internet',
                              'assigned_group': groups['service-informatique']},
                         ]
                         },
                        {'title': u'Créer un guichet supplémentaire dans les 3 mois',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 200.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 215.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear},
                                    {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'tasks': [
                             {'title': u'Réparer le guichet',
                              'assigned_group': groups['service-travaux']},
                         ]
                         },
                        {'title': u'Mettre en ligne sur le site internet différents documents "population" à '
                                  u'télécharger de chez soi',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 1500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 18500.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 2000.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear},
                                    {'amount': 3000.0, 'budget_type': 'province', 'year': currentYear},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'tasks': [
                             {'title': u'Expliquer au service comment éditer sur le site internet',
                              'assigned_group': groups['service-informatique']},
                         ]
                         },
                    ]
                },
                {
                    'title': u'Optimiser l\'accueil au sein de l\'administration communale',
                    u'result_indicator':
                    [
                        {'value': 50, 'label': u'Pourcentage minimum de visiteurs satisfaits (document de satisfaction '
                                               u'à remplir) sur un an', 'reached_value': 0},
                        {'value': 5, 'label': u'Pourcentage maximum de plaintes (document de plainte à disposition)',
                         'reached_value': 0},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2013, 12, 31)),
                    'representative_responsible': ['1er-echevin'],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-population'], groups['service-etat-civil']],
                    'extra_concerned_people': u'',
                    'budget': [],
                    'comments': richtextval(u''),
                    'actions': [
                        {'title': u'Placer des pictogrammes de guidance',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 50.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 250.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 15.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear},
                                    {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear+1},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
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
                         'manager': [groups['service-population'], groups['service-travaux']],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 600.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                    {'amount': 841.0, 'budget_type': 'europe', 'year': currentYear+1},
                                    {'amount': 1552.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear+1},
                                    {'amount': 123.0, 'budget_type': 'ville', 'year': currentYear+1},
                                    ],
                         'health_indicator': u'risque',
                         'health_indicator_details': u'Problème, retard dû à l\'exécution du marché',
                         'comments': richtextval(u''),
                         },
                        {'title': u'Mettre en place des permanences sur rendez-vous',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                         'extra_concerned_people': u'',
                         'budget': [],
                         'health_indicator': u'risque',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
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
                    'title': u'Doter la commune de compétences en matière énergétique pour fin 2014 compte tenu du '
                             u'budget',
                    u'result_indicator':
                    [
                        {'value': 2, 'label': u'Nombre de personnes engagées fin 2014', 'reached_value': 0},
                        {'value': 8, 'label': u'Nombre de personnes formées fin 2014', 'reached_value': 0},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2014, 12, 31)),
                    'representative_responsible': ['4eme-echevin'],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-de-lurbanisme']],
                    'extra_concerned_people': u'',
                    'budget': [],
                    'comments': richtextval(u''),
                    'actions': [
                        {'title': u'Procéder à l\'engagement d\'un conseiller en énergie',
                         'manager': [groups['service-de-lurbanisme'], ],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'tasks': [
                             {'title': u'Rédiger le profil de fonction de conseiller en énergie',
                              'assigned_group': groups['service-population']},
                             {'title': u'Ajouter une annonce sur le site internet',
                              'assigned_group': groups['service-informatique']},
                         ]
                         },
                        {'title': u'Répondre à l\'appel à projet "écopasseur" de la Wallonie',
                         'manager': [groups['service-de-lurbanisme'], ],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 0.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 50.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 5.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear},
                                    {'amount': 215.0, 'budget_type': 'ville', 'year': currentYear+1},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u'')
                         },
                        {'title': u'Inscrire systématiquement les agents du service travaux aux formations '
                                  u'énergétiques',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 9, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 550.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 5250.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 515.55, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear+1},
                                    {'amount': 5215.0, 'budget_type': 'ville', 'year': currentYear+1},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u'')
                         },
                    ]
                },
                {
                    'title': u'Réduire la consommation énergétique de la maison commune de 15% sur l\'année 2013',
                    u'result_indicator':
                    [
                        {'value': 2000, 'label': u'Diminution du nombre de litres de mazout au 31 12 2013',
                         'reached_value': 0},
                    ],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2013, 12, 31)),
                    'representative_responsible': ['1er-echevin'],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-de-lurbanisme']],
                    'extra_concerned_people': u'',
                    'budget': [],
                    'comments': richtextval(u''),
                    'actions': [
                        {'title': u'Réaliser un audit énergétique de l\'administration communale',
                         'manager': [groups['service-de-lurbanisme'], ],
                         'planned_end_date': datetime.date(datetime(2013, 06, 30)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+2},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+3},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u''),
                         'tasks': [
                             {'title': u'Écrire le cahier des charges',
                              'assigned_group': groups['cellule-marches-publics']},
                             {'title': u'Choisir le prestataire',
                              'assigned_group': groups['service-de-lurbanisme']},
                         ]
                         },
                        {'title': u'En fonction des résultats, procéder à l\'isolation du bâtiment',
                         'manager': [groups['service-travaux']],
                         'planned_end_date': datetime.date(datetime(2013, 10, 31)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+1},
                                    {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+2},
                                    {'amount': 1000.0, 'budget_type': 'wallonie', 'year': currentYear+3},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'',
                         'comments': richtextval(u'')
                         },
                        {'title': u'En fonction des résultats, installer une pompe à chaleur',
                         'manager': [groups['service-population'], ],
                         'planned_end_date': datetime.date(datetime(2013, 10, 31)),
                         'extra_concerned_people': u'',
                         'budget': [{'amount': 500.0, 'budget_type': 'europe', 'year': currentYear+2},
                                    {'amount': 500.0, 'budget_type': 'federal', 'year': currentYear+2},
                                    {'amount': 500.0, 'budget_type': 'wallonie', 'year': currentYear+2},
                                    {'amount': 500.0, 'budget_type': 'autres', 'year': currentYear+2},
                                    ],
                         'health_indicator': u'bon',
                         'health_indicator_details': u'Devenu sans objet compte tenu des résultats de l\'audit',
                         'comments': richtextval(u'')
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
                             u'réduire la présence de déchets de 90% au 31 12 2015',
                    u'result_indicator': [{'value': 50, 'label': u'Nombre de sacs poubelles récoltés '
                                          u'chaque année et à l\'échéance (31 12 2015)',
                                          'reached_value': 0}],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2015, 12, 31)),
                    'representative_responsible': ['2eme-echevin', '3eme-echevin'],
                    'administrative_responsible': [groups['secretariat-communal']],
                    'manager': [groups['service-proprete'], groups['service-travaux']],
                    'extra_concerned_people': u'Police\r\nAgents constatateurs communaux\r\nAgent sanctionnateur '
                                              u'communal\r\nStewards urbains',
                    'budget': [],
                    'budget_comments': richtextval(u'Fonds propres (en cours de chiffrage) et subventions (dossier '
                                                   u'introduit pour l\'engagement de deux stewards urbains)'),
                    'comments': richtextval(u''),
                    'actions': [
                        {'title': u'Installer des distributeurs de sacs "ramasse crottes", dans les parcs '
                                  u'(entrée et sortie)',
                         'manager': [groups['service-proprete'], ],
                         'planned_end_date': datetime.date(datetime(2014, 06, 30)),
                         'extra_concerned_people': u'La firme adjudicatrice au terme du marché public',
                         'budget': [{'amount': 12500.0, 'budget_type': 'wallonie', 'year': currentYear},
                                    {'amount': 2500.0, 'budget_type': 'europe', 'year': currentYear},
                                    {'amount': 250.0, 'budget_type': 'federation-wallonie-bruxelles',
                                     'year': currentYear},
                                    {'amount': 250.0, 'budget_type': 'province', 'year': currentYear},
                                    ],
                         'budget_comments': richtextval(u'1000 euros\r\nBudget ordinaire\r\nArticle budgétaire '
                                                        u'n°: ...'),
                         'health_indicator': u'risque',
                         'health_indicator_details': u'Agent traitant malade pour minimum 3 mois -> risque de retard '
                                                     u'dans le planning',
                         'comments': richtextval(u'Attendre le placement des nouvelles poubelles (avant le '
                                                 u'01/12/2013)'),
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
