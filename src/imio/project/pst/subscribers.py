# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.interfaces import ICollectionCategories
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from eea.facetednavigation.criteria.interfaces import ICriteria
from imio.helpers.content import set_to_annotation
from imio.pm.wsclient.browser.settings import notify_configuration_changed
from imio.project.pst.content.action import IPSTSubAction
from imio.project.pst.interfaces import IActionDashboardBatchActions
from imio.project.pst.interfaces import IImioPSTProject
from imio.project.pst.interfaces import IOODashboardBatchActions
from imio.project.pst.interfaces import IOSDashboardBatchActions
from imio.project.pst.interfaces import ITaskDashboardBatchActions
from plone import api
from plone.app.uuid.utils import uuidToPhysicalPath
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

import logging
import os


logger = logging.getLogger('imio.project.pst: subscribers')


def wsclient_configuration_changed(event):
    """ call original subscriber and do more stuff """
    if IRecordModifiedEvent.providedBy(event):
        # generated_actions changed, we need to update generated actions in portal_actions
        if event.record.fieldName == 'generated_actions':
            notify_configuration_changed(event)
            portal = api.portal.get()
            ids = []
            object_buttons = portal.portal_actions.object_buttons
            portlet_actions = portal.portal_actions.portlet
            for object_button in object_buttons.objectValues():
                if object_button.id.startswith('plonemeeting_wsclient_action_'):
                    ids.append(object_button.id)
                    if object_button.id in portlet_actions:
                        api.content.delete(portlet_actions[object_button.id])
                    api.content.copy(object_button, portlet_actions)
            arch_pos = portlet_actions.getObjectPosition('archive')
            for i, aid in enumerate(ids):
                portlet_actions.moveObjectToPosition(aid, arch_pos + i)


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
    """ pstsubaction and link too """
    # move into the created subaction any existing task found in its parent action
    action = obj.__parent__
    tasks = action.listFolderContents({'portal_type': 'task'})
    if getattr(obj, '_link_portal_type', '') == 'subaction_link' and tasks:
        raise Invalid("You cannot create a subaction link when there are tasks in action !")
    for task in tasks:
        api.content.move(task, obj)
    # we set a flag on the pstaction to indicate a subaction presence
    set_to_annotation('imio.project.pst.has_subactions', True, obj=action)


def pstsubaction_moved(obj, event):
    """  """
    if IObjectAddedEvent.providedBy(event):  # Already managed in above subscriber
        return
    if event.newParent == event.oldParent and event.newName != event.oldName:  # it's not a move but a rename
        return
    # When deleting an action with a subaction, we pass here but the event context is the action !!!!
    if IObjectRemovedEvent.providedBy(event) and obj != event.object:
        return
    # Move of delete
    # we manage the flag on the old pstaction to indicate a subaction presence
    if not event.oldParent.listFolderContents({'object_provides': IPSTSubAction.__identifier__}):
        set_to_annotation('imio.project.pst.has_subactions', False, obj=event.oldParent)
    # move into the moved subaction any existing task found in its new parent action
    if event.newParent:
        if getattr(obj, '_link_portal_type', '') == 'subaction_link':
            raise Invalid("You cannot move a subaction link. Create a new one !")
        tasks = event.newParent.listFolderContents({'portal_type': 'task'})
        for task in tasks:
            api.content.move(task, obj)
        # we set a flag on the pstaction to indicate a subaction presence
        set_to_annotation('imio.project.pst.has_subactions', True, obj=event.newParent)


def registry_changed(event):
    """  """
    if IRecordModifiedEvent.providedBy(event):
        if event.record.fieldName == 'pstaction_fields':
            api.portal.set_registry_record('imio.project.settings.pstsubaction_fields', event.newValue)
