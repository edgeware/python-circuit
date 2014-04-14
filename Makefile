all:

prepare:

check: frosted pep8

pep8:
	pep8 circuit

frosted:
	frosted -vb -r circuit

test:
	python setup.py test

build:

dist:

clean:
	git clean -fdx
