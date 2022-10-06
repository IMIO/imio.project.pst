Changelog
=========

1.3.3 (unreleased)
----------------
- Added a new Users Summary template
  [fngaha]
- Fix WrongContainedType
  [fngaha]
- Migrated front_page
  [fngaha]
- Updated columns following pentests corrections
  [fngaha]
- improved progress state template, added new columns (deadline, progress, observation) and conditionnal format to title column
  [fngaha]
- Fix locales language in projectspace
  [fngaha]
- Differentiated actions from sub-actions in documents by color. Assigned light blue to sub-actions
  [fngaha]
- Always specify the type of project elements (OS, OO, A, SA)
  [fngaha]
- Updated templates by fixing different display condition :
  text "Sélection d’objectifs stratégiques", table of contents
  result_indicator, planned_end_date, representative_responsible, administrative_responsible, manager, projection,
  analytic_budget, budget for oos
  result_indicator, planned_end_date, representative_responsible, health_indicator, manager, projection,
  analytic_budget, budget, progress for actions and subactions
  [fngaha]
- Improved progress state model with a new type column,
  auto filters, style condition and fixed first line
  [fngaha]
- Added a new progress state document
  [fngaha]
- Fix document generation view display issue
  [fngaha]
- Activate all aldermen organizations
  [fngaha]
- configure the representative responsible local role
  [fngaha]
- Override the source of representative responsible vocabulary
  [fngaha]
- Added a filter "Which I am representative responsible" for operational objectives and pst actions
  [fngaha]
- Add a test user "1er échevin"
  [fngaha]
- Added representative responsible function in plonegroup config
  [fngaha]
- Added a plan filter in os, oo, act
  [fngaha]
- Added sub-actions in the follow template
  [fngaha]

1.3.2 (2021-10-05)
----------------
- Fix sitemap when there are annex on a task
  [fngaha]
- Updated front page
  [fngaha]
- Used and migrated text/x-html-safe for rich fields
  [fngaha]
- Added optional tasks in export report
  [fngaha]
- Added new health indicator vocabulary "pause"
  [fngaha]
- integrated imio.annex
  [fngaha]
- Added a new style "Title Sub-Task" in general style and applied it in detailed template to solve numbering problem
  [fngaha]
- Sorted tasks on parent position instead of path
  [fngaha]
- Configured hiding of oo fields in the "Detailed" report
  [fngaha]
- Added budget comment in budget schema
  [fngaha]
- Added new dashboard template for tasks editor follow-up
  [fngaha]

1.3.1 (2021-06-02)
----------------
- Added new dashboard template for manager follow-up
  [fngaha]
- Fix ddetail template
  [fngaha]
- Added a presentation option to the follow-up report
  [fngaha]
- Fix a document generation bug when result indicator is None
  [fngaha]
- Enabled categories column on action dashboard
  [fngaha]
- Adapt categories indexation
  [fngaha]
- Move symlink origin link to ContentLink viewlet
  [daggelpop,fngaha]
- Fix planned end date dashboard column when the same field on the operational objective is empty
  [fngaha]
- Added read & write TAL conditions on PST fields settings
  [daggelpop,fngaha]
- Fix ecompte export for CPAS by adapting "typeAdmin" tag
  [fngaha]
- Allowed web service actions on subactions
  [fngaha]
- Fix an error during setup complaining about `fct_management` missing value
  [mpeeters]
- Fix ecompte export issue (export now also contains subactions as actions)
  [fngaha]
- Split symlinked budget
  [daggelpop,fngaha,sgeulette]
- Added budget globalization management
  [daggelpop,sgeulette,fngaha]
- Added strategicobjective, operationalobjective, pstaction, task _columns to configure dashboards columns in pstprojectspace
  [fngaha]
- Moved strategicobjective, operationalobjective, pstaction, pstsubaction _fields config from registry to pstprojectspace
  [fngaha]
- Added plan and plan_values fields, updated ecomptes export and templates
  [fngaha]
- Added optional new style template without numbering
  [bleybaert]

1.3 (2020-03-05)
----------------

- Added content type settings to remove and/or reorder fields
  [sgeulette,fngaha]
- Added sustainable development goal field, column
  [sgeulette]
- Added responsible field on action
  [sgeulette]
- Updated budget fields
  [sgeulette]
- Improved result indicator
  [vpiret,sgeulette,bleybaert]
- Added map view to display as tree
  [daggelpop,sgeulette]
- Xml generation to export to ecomptes
  [daggelpop,mpeeters,sgeulette]
- Added subaction content
  [daggelpop,sgeulette]
- Added action_link content
  [vpiret,sgeulette]
- Gotten OO due date from actions due dates
  [vpiret,mpeeters]
- administrative_responsible has editor role on OO
  [sgeulette]
- Used collective.portlet.actions to display some actions
  [sgeulette]
- Simplified user and group overview listings
  [sgeulette]
- Removed actions green bar. Improved general interface
  [sgeulette]

1.2 (2019-06-23)
----------------

- Order management of items
  [sgeulette]
- Corrected history
  [sgeulette]
- Added step to configure imio.pm.wsclient
  [sgeulette]
- Added representative responsible field on action
  [sgeulette]
- Added templates with created state
  [sgeulette]
- Modified delete action
  [sgeulette]

1.1 (2019-01-15)
----------------

- Migrated to collective.eeafaceted.dashboard
  [sgeulette]
- Added archive action
  [sgeulette]
- Added marker interface on pst project
  [sgeulette]
- Improved export doc
  [sgeulette]
- Added task collections.
  [sgeulette]
- Added batch actions
  [sgeulette]
- Clean green bar. Added actions panel.
  [sgeulette]
- Integrated imio.pm.wsclient
  [sgeulette]
- Migrated all to dexterity
  [sgeulette]

1.0 (2016-12-08)
----------------

- Added dashboard
  [cmessiant]
- Reconfigure navigation portlet
  [sgeulette]
- Use collective.documentgenerator
  [sgeulette]
- Various corrections and improvements
  [sgeulette]

0.3.1 (2015-04-10)
------------------
- Update the front page text
- Move the reference number at the end of title
- Add a strategic objectives topic as a projectspace default page
- Use tabular view to pst collections
  [franck.ngaha@imio.be]

0.3 (2014-12-11)
----------------
- add a unique reference number on each project per project space
- Replace the vocabulary of the administrative service
- provide an excel export through collective.excelimportexport
- Provide some research topics in a portlet
- Update the title and body of front page
  [franck.ngaha@imio.be]

0.2 (2013-11-19)
----------------
- Replaced budget text field by datagrid field
- Replaced project_workflow by two different workflows adapted to local roles
- Use contact.plonegroup to manage services and manager field vocabulary
- Use manager field to give "add permission" on operationalobjective
- Use manager field to give "modify permission" on pstaction
- Add a generic full model used in document generation
- Added possibility to add annexes (Files) to different elements
- Rely on imio.migrator
- Use "categories" field on operationalobjective
- Added "observation" field to define the objective context

0.1 (2013-08-06)
----------------
- Initial release.
  [s.geulette@imio.be]
