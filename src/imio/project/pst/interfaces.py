# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IImioProjectPSTLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""

# TODO : Remove this interface after version 1.4 and replace its use in old migrations by IPSTProjectSpace
class IImioPSTProject(Interface):
    """Marker interface for a PST project"""


class IPSTDashboard(Interface):

    """Marker interface for all ia.pst dashboards."""


class IOSDashboard(IPSTDashboard):

    """Marker interface for os dashboard."""


class IOSDashboardBatchActions(IOSDashboard, IBatchActionsMarker):

    """Marker interface for os dashboard with batch actions."""


class IOODashboard(IPSTDashboard):

    """Marker interface for oo dashboard."""


class IOODashboardBatchActions(IOODashboard, IBatchActionsMarker):

    """Marker interface for oo dashboard with batch actions."""


class IActionDashboard(IPSTDashboard):

    """Marker interface for action dashboard."""


class IActionDashboardBatchActions(IActionDashboard, IBatchActionsMarker):

    """Marker interface for action dashboard with batch actions."""


class ITaskDashboard(IPSTDashboard):

    """Marker interface for task dashboard."""


class ITaskDashboardBatchActions(ITaskDashboard, IBatchActionsMarker):

    """Marker interface for task dashboard with batch actions."""
