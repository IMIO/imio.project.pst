#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	/srv/python275/bin/virtualenv --no-setuptools .
	bin/python ez_setup.py
	bin/easy_install -U "distribute==0.6.49"
	./bin/python bootstrap.py -v 2.1.1

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 5

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: cleanall
cleanall:
	rm -fr develop-eggs downloads eggs parts .installed.cfg
