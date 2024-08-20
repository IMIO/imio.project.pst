from plone.restapi.serializer.dxcontent import SerializeToJson
from plone.restapi.interfaces import ISerializeToJson
from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
from Acquisition import aq_parent,aq_inner
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter
from collective.symlink.content.symlink import ISymlink, ISymlinkMarker
from plone.restapi.serializer.converters import json_compatible

@implementer(ISerializeToJson)
@adapter(ISymlink, Interface)
class SymlinkToJson(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        version = "current" if version is None else version

        obj = self.getVersion(version)
        parent = aq_parent(aq_inner(obj))
        parent_summary = getMultiAdapter(
            (parent, self.request), ISerializeToJsonSummary
        )()
        source_summary = getMultiAdapter(
            (obj._link, self.request), ISerializeToJsonSummary
        )() if obj._link else None
        if source_summary:
            source_summary["UID"]=obj._link.UID()
        result = {
            "@id": obj.absolute_url(),
            "id": obj.id,
            "@type": "symlink",
            "parent": parent_summary,
            "UID": obj.UID(),
            "source": source_summary,
        }

        return result

@implementer(ISerializeToJsonSummary)
@adapter(ISymlink, Interface)
class SymlinkToJsonSummary(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        summary = json_compatible(
            {
                "@id": self.context.absolute_url(),
                "@type": "symlink",
                "title": self.context.title,
                 "UID": self.context.UID(),
            }
        )
        return summary
    
# @implementer(ISerializeToJson)
# @adapter(ISymlinkMarker, Interface)
# class SymlinkMarkerToJson(SerializeToJson):
#     def __call__(self, version=None, include_items=True):
#         version = "current" if version is None else version

#         obj = self.getVersion(version)
#         parent = aq_parent(aq_inner(obj))
#         parent_summary = getMultiAdapter(
#             (parent, self.request), ISerializeToJsonSummary
#         )()
#         result = {
#             "@id": obj.absolute_url(),
#             "id": obj.id,
#             "@type": "symlinkmarker",
#             "parent": parent_summary,
           
#         }

#         return result