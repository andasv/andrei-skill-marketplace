SKILL_NAME := ai-espresso-skill
VERSION := $(shell cat VERSION.md | tr -d '[:space:]')
DIST_DIR := dist
ZIP_NAME := $(SKILL_NAME)-v$(VERSION).zip
SKILL_LINK := $(HOME)/.claude/skills/ai-espresso

# Files to include in the ZIP
DIST_FILES := \
	VERSION.md \
	README.md \
	SKILL.md \
	Makefile \
	sources.md \
	guidelines.md \
	.gitignore \
	evals/evaluator.md \
	evals/evals.json \
	references/html-template.md \
	output/.gitkeep

.PHONY: help zip clean list version bump-patch bump-minor bump-major install uninstall

help: ## Show available commands
	@echo "ai-espresso-skill v$(VERSION)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

version: ## Print current version
	@echo $(VERSION)

list: ## Show files that would be included in the ZIP
	@echo "Files in $(ZIP_NAME):"
	@for f in $(DIST_FILES); do echo "  $$f"; done

zip: ## Build versioned distribution ZIP
	@mkdir -p $(DIST_DIR)
	@rm -f $(DIST_DIR)/$(ZIP_NAME)
	@# Create a temp directory with the skill name prefix for clean zip structure
	@TMPDIR=$$(mktemp -d) && \
	STAGE="$$TMPDIR/$(SKILL_NAME)" && \
	mkdir -p "$$STAGE" && \
	for f in $(DIST_FILES); do \
		mkdir -p "$$STAGE/$$(dirname $$f)"; \
		cp "$$f" "$$STAGE/$$f"; \
	done && \
	cd "$$TMPDIR" && \
	zip -r "$(CURDIR)/$(DIST_DIR)/$(ZIP_NAME)" "$(SKILL_NAME)" && \
	rm -rf "$$TMPDIR"
	@echo ""
	@echo "Created: $(DIST_DIR)/$(ZIP_NAME)"
	@ls -lh $(DIST_DIR)/$(ZIP_NAME)

clean: ## Remove dist/ directory
	rm -rf $(DIST_DIR)
	@echo "Cleaned."

bump-patch: ## Increment patch version (0.5.0 → 0.5.1) and rebuild ZIP
	@echo $(VERSION) | awk -F. '{printf "%d.%d.%d\n", $$1, $$2, $$3+1}' > VERSION.md
	@echo "Version bumped: $(VERSION) → $$(cat VERSION.md | tr -d '[:space:]')"
	@$(MAKE) zip

bump-minor: ## Increment minor version (0.5.0 → 0.6.0) and rebuild ZIP
	@echo $(VERSION) | awk -F. '{printf "%d.%d.0\n", $$1, $$2+1}' > VERSION.md
	@echo "Version bumped: $(VERSION) → $$(cat VERSION.md | tr -d '[:space:]')"
	@$(MAKE) zip

bump-major: ## Increment major version (0.5.0 → 1.0.0) and rebuild ZIP
	@echo $(VERSION) | awk -F. '{printf "%d.0.0\n", $$1+1}' > VERSION.md
	@echo "Version bumped: $(VERSION) → $$(cat VERSION.md | tr -d '[:space:]')"
	@$(MAKE) zip

install: ## Symlink skill to ~/.claude/skills/ai-espresso
	@if [ -L "$(SKILL_LINK)" ]; then \
		echo "Symlink already exists: $(SKILL_LINK)"; \
	elif [ -e "$(SKILL_LINK)" ]; then \
		echo "Error: $(SKILL_LINK) exists but is not a symlink. Remove it first."; \
		exit 1; \
	else \
		ln -s "$(CURDIR)" "$(SKILL_LINK)"; \
		echo "Installed: $(SKILL_LINK) → $(CURDIR)"; \
	fi

uninstall: ## Remove skill symlink from ~/.claude/skills/
	@if [ -L "$(SKILL_LINK)" ]; then \
		rm "$(SKILL_LINK)"; \
		echo "Removed: $(SKILL_LINK)"; \
	else \
		echo "No symlink found at $(SKILL_LINK)"; \
	fi
