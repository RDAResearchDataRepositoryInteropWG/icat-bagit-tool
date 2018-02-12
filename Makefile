PYTHON   = python


build:
	$(PYTHON) setup.py build

sdist:
	$(PYTHON) setup.py sdist


clean:
	rm -f *~
	rm -rf build

distclean: clean
	rm -f MANIFEST
	rm -f *.pyc
	rm -rf __pycache__
	rm -rf dist


.PHONY: build sdist clean distclean
