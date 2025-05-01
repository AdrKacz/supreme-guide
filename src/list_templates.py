import os

def list_templates():
    folder = 'mail'
    templates = []
    for filename in os.listdir(folder):
        if filename.endswith('.html'):
            templates.append(os.path.join(folder, filename))
    return sorted(templates)