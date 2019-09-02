# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.interfaces import ICollectionCategories
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from eea.facetednavigation.criteria.interfaces import ICriteria
from imio.project.pst.interfaces import IActionDashboardBatchActions
from imio.project.pst.interfaces import IImioPSTProject
from imio.project.pst.interfaces import IOODashboardBatchActions
from imio.project.pst.interfaces import IOSDashboardBatchActions
from imio.project.pst.interfaces import ITaskDashboardBatchActions
from plone import api
from plone.app.uuid.utils import uuidToPhysicalPath
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.interface import alsoProvides
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

import os
import logging

logger = logging.getLogger('imio.project.pst: subscribers')


def projectspace_created(obj, event):
    """When a projectspace is created, if it is not the PST, we constrain types to ('project', )"""

    alsoProvides(obj, IOSDashboardBatchActions)

    if not IImioPSTProject.providedBy(obj):
        behaviour = ISelectableConstrainTypes(obj)
        behaviour.setConstrainTypesMode(1)
        behaviour.setLocallyAllowedTypes(['project', ])
        behaviour.setImmediatelyAddableTypes(['project', ])


def projectspace_moved(obj, event):
    """ When a projectspace is renamed, we correct collections """
    if IObjectRemovedEvent.providedBy(event):
        return
    portal = api.portal.get()
    path = '/'.join(obj.getPhysicalPath())
    # correct path criteria in collections
    for brain in portal.portal_catalog(path=path, portal_type='DashboardCollection'):
        ob = brain.getObject()
        query = ob.query
        for elt in query:
            if elt['i'] == 'path':
                elt['v'] = path
        ob.query = query
    # correct default collection
    for brain in portal.portal_catalog(path=path, object_provides=ICollectionCategories.__identifier__):
        ob = brain.getObject()
        criterion = getCollectionLinkCriterion(ob)
        criterias = ICriteria(ob)
        old_uid = criterias.get(criterion.__name__).get('default')
        old_path = uuidToPhysicalPath(old_uid)
        old_id = os.path.basename(old_path)
        if old_path.endswith('/{}/{}'.format(ob.id, old_id)):
            default_col = ob[old_id].UID()
            _updateDefaultCollectionFor(ob, default_col)
            logger.info('Replaced default col {} by {} on {}'.format(old_uid, default_col, ob.absolute_url()))
        else:
            raise ValueError("Cannot update default col on {}".format(ob.absolute_url()))


def strategic_created(obj, event):
    """  """
    alsoProvides(obj, IOODashboardBatchActions)


def operational_created(obj, event):
    """  """
    alsoProvides(obj, IActionDashboardBatchActions)


def pstaction_created(obj, event):
    """  """
    alsoProvides(obj, ITaskDashboardBatchActions)


def pstsubaction_created(obj, event):
    """  """

    # move into the created subaction any existing task found in its parent action
    action = obj.__parent__
    tasks = action.listFolderContents({'portal_type': 'task'})
    for task in tasks:
        api.content.move(task, obj)
