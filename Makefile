.PHONY: install dist clean

build:
	python -m build

install:
	python setup.py install --force

dist:
	python setup.py bdist_wheel

clean:
	rm -rf build/ dist/ *.egg-info/
