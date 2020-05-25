from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('imio.project.pst')
security.declarePublic('ecomptes import')
security.declarePublic('ecomptes export')
ecomptes_import = 'imio.project.pst: ecomptes import'
ecomptes_export = 'imio.project.pst: ecomptes export'
setDefaultRoles(ecomptes_import, ('Manager', 'Contributor'))
setDefaultRoles(ecomptes_export, ('Manager', 'Contributor'))
