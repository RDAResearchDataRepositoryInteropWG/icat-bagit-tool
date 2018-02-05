PYTHON   = python


build:
	$(PYTHON) setup.py build

sdist:
	$(PYTHON) setup.py sdist


clean:
	rm -f *~ src/*~
	rm -rf build

distclean: clean
	rm -f MANIFEST
	rm -f *.pyc src/*.pyc
	rm -rf __pycache__ src/__pycache__
	rm -rf dist


.PHONY: build sdist clean distclean
