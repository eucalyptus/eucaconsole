
watch:
	compass watch koala/static

translations:
	python setup.py extract_messages
	python setup.py update_catalog
	python setup.py compile_catalog
