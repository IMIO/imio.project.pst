import os
from imio.project.pst import add_path


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
    out = []
    folder = self.templates
    templates_dir = add_path('profiles/default/templates')
    for id, filename in templates:
        filename_path = os.path.join(templates_dir, filename)
        try:
            f = open(filename_path, 'rb')
            file_content = f.read()
            f.close()
        except:
            continue
        out.append("Template '%s' updated with '%s'" % (id, filename))
        new_template = getattr(folder, id)
        new_template.setFile(file_content)
        new_template.setFilename(filename)
        new_template.setFormat("application/vnd.oasis.opendocument.text")
    return '\n'.join(out)
