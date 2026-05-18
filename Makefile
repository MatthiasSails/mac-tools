INSTALL_DIR := $(HOME)/bin
REPO_DIR    := $(shell pwd)

.PHONY: install deps shell update

## install – symlink all tools into ~/bin and install dependencies
install: brew deps shell
	@mkdir -p $(INSTALL_DIR)
	@for f in $(REPO_DIR)/bin/*; do \
		name=$$(basename $$f); \
		ln -sf $$f $(INSTALL_DIR)/$$name; \
		chmod +x $$f; \
		echo "  linked: $(INSTALL_DIR)/$$name → $$f"; \
	done
	@echo "✓  install done"

## brew – install Homebrew packages from Brewfile
brew:
	brew bundle install --file=$(REPO_DIR)/Brewfile
	@echo "✓  brew done"

## deps – create venv if needed and install dependencies
deps:
	@test -d $(REPO_DIR)/.venv || python3 -m venv $(REPO_DIR)/.venv
	@$(REPO_DIR)/.venv/bin/pip install -q -r $(REPO_DIR)/requirements.txt
	@echo "✓  deps done"

## shell – symlink bash dotfiles into $HOME
shell:
	@SHELL_DIR=$(REPO_DIR)/shell; \
	for f in bash_profile bashrc; do \
		src="$$SHELL_DIR/$$f"; \
		dst="$(HOME)/.$$f"; \
		if [ -L "$$dst" ]; then \
			echo "  $$dst → bereits Symlink"; \
		elif [ -f "$$dst" ]; then \
			mv "$$dst" "$$dst.before-mac-tools"; \
			ln -s "$$src" "$$dst"; \
			echo "  $$dst → $$src (backup: $$dst.before-mac-tools)"; \
		else \
			ln -s "$$src" "$$dst"; \
			echo "  linked: $$dst → $$src"; \
		fi; \
	done
	@echo "✓  shell done"

## update – pull latest and reinstall
update:
	git pull --ff-only
	$(MAKE) install
