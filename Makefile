# SPDX-License-Identifier: MIT

VERSION ?= 0.3.2+git$(shell date "+%Y%m%d")
DATE ?= $(shell date "+%a %b %d %Y")

INSTALL = install
CARGO = cargo
CARGOFLAGS =
RONN = ronn
PKG_CONFIG = pkg-config
PREFIX = /usr

SYSTEMD_UTIL_DIR := $(shell $(PKG_CONFIG) --variable=systemdutildir systemd)
SYSTEMD_SYSTEM_UNIT_DIR := $(shell $(PKG_CONFIG) --variable=systemdsystemunitdir systemd)
SYSTEMD_SYSTEM_GENERATOR_DIR := $(shell $(PKG_CONFIG) --variable=systemdsystemgeneratordir systemd)

export SYSTEMD_UTIL_DIR
export SYSTEMD_SYSTEM_UNIT_DIR
export SYSTEMD_SYSTEM_GENERATOR_DIR

.PHONY: all
all: bin systemd man

.PHONY: vendor
vendor:
	@mkdir -p .cargo
	@$(CARGO) vendor > .cargo/config.toml

.PHONY: bin
bin:
	@$(CARGO) build --release $(CARGOFLAGS)

.PHONY: systemd
systemd:
	@sed -e 's,@SYSTEMD_SYSTEM_GENERATOR_DIR@,$(SYSTEMD_SYSTEM_GENERATOR_DIR),' \
		< units/systemd-zram-setup@.service.in \
		> units/systemd-zram-setup@.service

.PHONY: man
man:
	@$(RONN) --organization="zram-generator developers" man/*.md

.PHONY: test
test:
	@$(CARGO) test --release $(CARGOFLAGS)

.PHONY: install
install: install.bin install.conf install.systemd install.man

install.bin:
	$(INSTALL) -Dpm755 target/release/zram-generator -t $(DESTDIR)$(SYSTEMD_SYSTEM_GENERATOR_DIR)/

install.conf:
	$(INSTALL) -Dpm644 zram-generator.conf.example -t $(DESTDIR)$(PREFIX)/share/doc/zram-generator/

install.systemd:
	$(INSTALL) -Dpm644 units/systemd-zram-setup@.service -t $(DESTDIR)$(SYSTEMD_SYSTEM_UNIT_DIR)/

install.man:
	$(INSTALL) -Dpm644 man/zram-generator.8 -t $(DESTDIR)$(PREFIX)/share/man/man8/
	$(INSTALL) -Dpm644 man/zram-generator.conf.5 -t $(DESTDIR)$(PREFIX)/share/man/man5/

.PHONY: clean
clean:
	@$(CARGO) clean
	@rm -f units/systemd-zram-setup@.service

.PHONY: dist-gzip
dist-gzip:
	tar -zcv \
		--exclude='./.git' \
		-f ../zram-generator_$(VERSION).orig.tar.gz .

.PHONY: deb
deb:
	dch -v $(VERSION)-1 __VERSION__
	sed "/^\s*\* __VERSION__/d" -i debian/changelog
	debuild -us -uc

.PHONY: rpm
rpm:
	cp zram-generator.spec ../zram-generator_$(VERSION)-1.spec
	sed "s/__VERSION__/$(VERSION)/g" -i ../zram-generator_$(VERSION)-1.spec
	sed "s/__DATE__/$(DATE)/g" -i ../zram-generator_$(VERSION)-1.spec
