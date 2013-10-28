import os
from imio.project.pst import setuphandlers


def update_templates(self):
    """
        update pst templates
    """
    templates = [
        #('pstaction_template', 'fichepstaction.odt'),
        #('operationalobjective_template', 'ficheoo.odt'),
        ('pst_template', 'pst_full.odt'),
        #('status_template', 'tableaubord.odt'),
    ]

    folder = self.templates
    templates_dir = os.path.join(os.path.dirname(setuphandlers.__file__), 'profiles', 'default', 'templates')
    for id, filename in templates:
        filename_path = os.path.join(templates_dir, filename)
        try:
            f = open(filename_path, 'rb')
            file_content = f.read()
            f.close()
        except:
            continue
        new_template = getattr(folder, id)
        new_template.setFile(file_content)
        new_template.setFilename(filename)
        new_template.setFormat("application/vnd.oasis.opendocument.text")
