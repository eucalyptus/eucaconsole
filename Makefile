# Handy shortcuts for development (and perhaps deployment)

# Add Compass watcher (Converts Sass .scss files to .css)
watch:
	compass watch eucaconsole/static

# Make i18n translations from Python and XHTML files
translations:
	python setup.py extract_messages
	python setup.py update_catalog
	python setup.py compile_catalog

# Handy way to test if our Chameleon-based XHTML templates are valid XML (for i18n)
xmltest:
	python setup.py extract_messages
