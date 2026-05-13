INSTALL_DIR := $(HOME)/bin
REPO_DIR    := $(shell pwd)

.PHONY: install deps update

## install – symlink all tools into ~/bin and install dependencies
install: deps
	@mkdir -p $(INSTALL_DIR)
	@for f in $(REPO_DIR)/bin/*; do \
		name=$$(basename $$f); \
		ln -sf $$f $(INSTALL_DIR)/$$name; \
		chmod +x $$f; \
		echo "  linked: $(INSTALL_DIR)/$$name → $$f"; \
	done
	@echo "✓  install done"

## deps – install Python dependencies for all tools
deps:
	@pip3 install --break-system-packages -q \
		$$(cat $(REPO_DIR)/*/requirements.txt 2>/dev/null | sort -u)
	@echo "✓  deps done"

## update – pull latest and reinstall
update:
	git pull --ff-only
	$(MAKE) install
