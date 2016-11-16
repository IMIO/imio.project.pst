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

${SELENIUM_RUN_ON_FAILURE}  Debug
${OS}  etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient
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

Consultation
# partie 2.2.1 Visualisation d'un élément
    Enable autologin as  pstreader
    Set autologin username  pstreader
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation pst.png  css=.site-plone  id=portal-footer-wrapper
    Go to  ${PLONE_URL}/pst/${OS}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation os.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS}/${OO}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation oo.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation action.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS}/${OO}/${Action}/${task}
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
    Go to  ${PLONE_URL}/pst/${OS}/${OO}/${Action}
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

*** Keywords ***
Suite Setup
    Open test browser
    Set Window Size  1280  1200
    Set Suite Variable  ${CROP_MARGIN}  2
