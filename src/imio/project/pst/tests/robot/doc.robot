*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot
Resource  common.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging
Library  Selenium2Screenshots

Suite Setup  Suite Setup
Suite Teardown  Close all browsers

*** Variables ***

#${BROWSER}  GoogleChrome
${BROWSER}  Firefox
${SELENIUM_RUN_ON_FAILURE}  Debug
${OS1}  etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient
${OS2}  etre-une-commune-ou-il-fait-bon-vivre-dans-un-cadre-agreable-propre-et-en-toute-securite
${OO}  diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois-a-venir
${Action}  engager-2-agents-pour-le-service-population
${task}  rediger-le-profil-de-fonction

*** Test cases ***

Premiers pas
# partie 2.1 Premiers pas
    Go to  ${PLONE_URL}
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-1 accès à l'application.png  css=.site-plone  id=portal-footer-wrapper
    Enable autologin as  psteditor
    #Log in  encodeur  Project69!
    Go to  ${PLONE_URL}
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-1 page d'accueil.png  id=portal-header  id=parent-fieldname-description
    Capture and crop page screenshot  doc/utilisation/2-1 fil d'ariane.png  id=breadcrumbs-you-are-here  id=breadcrumbs-home

Visualisation
# partie 2.2.1 Visualisation d'un élément
    Enable autologin as  pstreader
    Set autologin username  pstreader
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation pst.png  css=.site-plone  id=portal-footer-wrapper
    Go to  ${PLONE_URL}/pst/${OS1}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation os.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation oo.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation action.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}/${task}
    Wait until element is visible  formfield-form-widgets-ITask-due_date  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation tache.png  css=.site-plone  id=portal-column-content

Menu courrier
# partie 2.2.2 Menu de recherches prédéfinies
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-2 menu recherches.png  css=.portletWidgetCollection
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-2 navigation.png  css=.portletNavigationTree

Tableaux de bord
# partie 2.2.3 Tableaux de bord
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Select collection  pst/operationalobjectives/all
    Capture and crop page screenshot  doc/utilisation/2-2-3 tableaux de bord général.png  id=content
    Click element  css=.faceted-sections-buttons-more
    Wait until element is visible  id=top---advanced---widgets  10
    Sleep  1
    Capture and crop page screenshot  doc/utilisation/2-2-3 tableaux de bord filtres avances.png  id=top---advanced---widgets
    # Go to  ${PLONE_URL}/filtre_add.png
    # Sleep  1
    # Capture and crop page screenshot  doc/utilisation/2-2-3 tableaux de bord filtres avances icone.png  css=body img

Génération de documents
# partie 2.2.4 Génération de documents
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Capture and crop page screenshot  doc/utilisation/2-2-4 génération liste documents.png  css=#viewlet-below-content-title #doc-generation-view li
    Capture and crop page screenshot  doc/utilisation/2-2-4 génération document élément.png  css=.documentFirstHeading  id=doc-generation-view
    Capture and crop page screenshot  doc/utilisation/2-2-4 génération document tb.png  css=#pst-folder-listing legend  css=.faceted-table-results thead

Modification
# partie 2.3 Modification
    Enable autologin as  psteditor
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst/${OS2}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-3 modification barre verte.png  id=viewlet-above-content  id=edit-bar  css=.documentFirstHeading
    Go to  ${PLONE_URL}/pst/${OS2}/edit
    Wait until element is visible  formfield-form-widgets-comments  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-3 modification financement dernière ligne.png  id=formfield-form-widgets-budget
    Input text  name=form.widgets.budget.0.widgets.amount  1000
    Click element  css=#formfield-form-widgets-budget label
    Sleep  0.5
    Capture and crop page screenshot  doc/utilisation/2-3 modification financement ligne ajoutée.png  id=formfield-form-widgets-budget
    Capture and crop page screenshot  doc/utilisation/2-3 modification boutons.png  id=form-buttons-save  id=form-buttons-cancel
    Click button  id=form-buttons-cancel
    Sleep  0.3

Tâche
# partie 2.5 Ajout d'une tâche
    Enable autologin as  psteditor
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}/++add++task
    Wait until element is visible  cke_form.widgets.ITask.task_description  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-5-1 tache ajout vierge.png  id=content
    Input text  name=form.widgets.title  Placer le CV dans notre référentiel
    Click button  id=form-buttons-save
    Sleep  0.5
    Capture and crop page screenshot  doc/utilisation/2-5-1 tache ajout complete.png  id=content
    ${UID} =  Path to uid  /${PLONE_SITE_ID}/pst/${OS1}/${OO}/${Action}/placer-le-cv-dans-notre-referentiel
    Fire transition  ${UID}  do_to_assign
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}/placer-le-cv-dans-notre-referentiel
    Wait until element is visible  css=#plone-contentmenu-workflow span.state-to_assign  10
    Capture and crop page screenshot  doc/utilisation/2-5-1 tache ajout to assign.png  id=content
# partie 2.7.2 Visualisation d'une tâche
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.5
    Capture and crop page screenshot  doc/utilisation/2-5-2 tache dans action.png  id=content
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Select collection  pst/tasks/all
    Wait until element is visible  css=.th_header_assigned_group  10
    Capture and crop page screenshot  doc/utilisation/2-5-2 tache dans tableau.png  id=content

Contacts
# partie 3.3 Contacts
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/contacts
    Wait until element is visible  css=#organizations a  10
    Capture and crop page screenshot  doc/configuration/3-3 annuaire.png  id=portal-header  id=content
    Go to  ${PLONE_URL}/contacts/plonegroup-organization
    Wait until element is visible  css=a.addnewcontactfromorganization  10
    Update element style  id=organization  width  400px !important
    Sleep  1
    Capture and crop page screenshot  doc/configuration/3-3 mon organisation.png  css=h1.org  id=sub_organizations
    Go to  ${PLONE_URL}/contacts/plonegroup-organization/services
    Wait until element is visible  css=a.addnewcontactfromorganization  10
    Update element style  id=organization  width  400px !important
    Sleep  1
    Capture and crop page screenshot  doc/configuration/3-3 mes services.png  css=h1.org  id=sub_organizations
    Click element  user-name
    Wait until element is visible  css=li#personaltools-plone_setup  10
    Capture and crop page screenshot  doc/configuration/3-3 configuration site.png  id=livesearch0  css=dd.actionMenuContent
    Go to  ${PLONE_URL}/@@overview-controlpanel
    Wait until page contains  Configuration de module  10
    Update element style  css=dl.warning  display  None
    ${note50}  Add pointy note  css=.configlets li a[href$="/@@contact-plonegroup-settings"]  C'est là  position=top  color=blue
    Capture and crop page screenshot  doc/configuration/3-3 lien config services.png  css=h2:nth-of-type(2)  css=h2:nth-of-type(3)  ${note50}
    Remove element  ${note50}
    # datagridfield doesn't work in robot
    #Go to  ${PLONE_URL}/@@contact-plonegroup-settings
    #Wait until element is visible  id=pg-orga-link  10
    #Capture and crop page screenshot  doc/configuration/3-3 config services.png  id=content
    Go to  ${PLONE_URL}/@@usergroup-usermembership?userid=psteditor
    Wait until element is visible  css=table.listing  10
    Capture and crop page screenshot  doc/configuration/3-3 groupes plone.png  id=content

*** Keywords ***
Suite Setup
    Open test browser
    Set Window Size  1280  4000
    Set Suite Variable  ${CROP_MARGIN}  2
