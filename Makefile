SPECFILE            = $(shell find -maxdepth 1 -type f -name *.spec)
SPECFILE_NAME       = python-collectd_nfsiostat
SPECFILE_VERSION    = $(shell awk '$$1 == "Version:"  { print $$2 }' $(SPECFILE) )
SPECFILE_RELEASE    = $(shell awk '$$1 == "Release:"  { print $$2 }' $(SPECFILE) )
TARFILE             = $(SPECFILE_NAME)-$(SPECFILE_VERSION).tgz
DIST               ?= $(shell rpm --eval %{dist})

sources:
	tar -zcvf $(TARFILE) --exclude-vcs --transform 's,^,$(SPECFILE_NAME)-$(SPECFILE_VERSION)/,' *

clean:
	rm -rf build/ $(TARFILE)

rpm: sources
	rpmbuild -bb --define 'dist $(DIST)' --define "_topdir $(PWD)/build" --define '_sourcedir $(PWD)' $(SPECFILE)

srpm: sources
	rpmbuild -bs --define 'dist $(DIST)' --define "_topdir $(PWD)/build" --define '_sourcedir $(PWD)' $(SPECFILE)
