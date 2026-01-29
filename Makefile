.PHONY: help setup build test launch context context-audit clean validate plan fmt \
	check manager manager-check manager-force manager-tick manager-reset research \
	cycle pre-commit

# Paths
PROJECT_DIR := project
MANAGER_DIR := .manager
SCRIPTS_DIR := scripts

help:
	@echo "Context generation commands:"
	@echo "  make context         - Generate manager context (.manager/context.xml)"
	@echo "  make context-audit   - Generate timestamped context for auditors"
	@echo ""
	@echo "Setup and run:"
	@echo "  make setup           - Run full RunPod setup"
	@echo "  make build           - Build Cairo project"
	@echo "  make test            - Run Cairo tests"
	@echo "  make launch          - Launch autonomous agents"
	@echo ""
	@echo "Validation commands:"
	@echo "  make validate        - Run pre-commit validation gates"
	@echo "  make plan            - Print current agent plan"
	@echo ""
	@echo "Formatting commands:"
	@echo "  make fmt             - Format Cairo code"
	@echo "  make check           - Check Cairo formatting"
	@echo ""
	@echo "Manager protocol:"
	@echo "  make manager         - Sync with manager (if threshold reached)"
	@echo "  make manager-force   - Force manager sync now"
	@echo "  make manager-check   - Check if sync needed"
	@echo "  make manager-tick    - Increment call count"
	@echo "  make manager-reset   - Reset call count"
	@echo "  make research Q=\"x\" - Research query via Perplexity"
	@echo ""
	@echo "Workflow:"
	@echo "  make cycle           - Build, test, tick manager"
	@echo "  make pre-commit      - Format, build, test"
	@echo ""
	@echo "Cleanup commands:"
	@echo "  make clean           - Remove generated context files"

context:
	@mkdir -p context
	@echo "Generating context..."
	@DATE=$$(date '+%Y-%m-%d_%H-%M-%S_%Z'); \
	OUTPUT_FILE="context/context-$${DATE}.xml"; \
	cp repomix.config.json repomix.config.json.bak && \
	jq ".output.filePath = \"$$OUTPUT_FILE\"" repomix.config.json > repomix.config.json.tmp && \
	mv repomix.config.json.tmp repomix.config.json && \
	(repomix --config repomix.config.json || (mv repomix.config.json.bak repomix.config.json && exit 1)) && \
	cp "$$OUTPUT_FILE" context/context.xml && \
	jq ".output.filePath = \"context/context.xml\"" repomix.config.json > repomix.config.json.tmp && \
	mv repomix.config.json.tmp repomix.config.json && \
	rm -f repomix.config.json.bak && \
	echo "✅ Context written to $$OUTPUT_FILE"

context-audit:
	@echo "Generating full project context..."
	@DATE=$$(date '+%Y-%m-%d_%H-%M-%S_%Z'); \
	OUTPUT_FILE="context/context-$${DATE}.xml"; \
	cp repomix.config.json repomix.config.json.bak && \
	jq ".output.filePath = \"$$OUTPUT_FILE\"" repomix.config.json > repomix.config.json.tmp && \
	mv repomix.config.json.tmp repomix.config.json && \
	(repomix --config repomix.config.json || (mv repomix.config.json.bak repomix.config.json && exit 1)) && \
	jq ".output.filePath = \"context/context.xml\"" repomix.config.json > repomix.config.json.tmp && \
	mv repomix.config.json.tmp repomix.config.json && \
	rm -f repomix.config.json.bak && \
	echo "✅ Context written to $$OUTPUT_FILE"

clean:
	@echo "Cleaning generated context files..."
	rm -f context*.xml
	rm -f context-*-*.xml
	rm -f repomix.config.json.bak
	rm -f repomix.config.json.tmp
	rm -f context/*.xml

validate:
	@bash scripts/validate.sh

plan:
	@cat PLAN.md

setup:
	bash scripts/setup-runpod.sh

build:
	cd $(PROJECT_DIR) && scarb build

test:
	cd $(PROJECT_DIR) && snforge test

fmt:
	cd $(PROJECT_DIR) && scarb fmt

check:
	cd $(PROJECT_DIR) && scarb fmt --check

launch:
	bash scripts/launch.sh

manager-check:
	python $(SCRIPTS_DIR)/manager_sync.py --check

manager:
	python $(SCRIPTS_DIR)/manager_sync.py

manager-force: context
	python $(SCRIPTS_DIR)/manager_sync.py --force

manager-tick:
	python $(SCRIPTS_DIR)/manager_sync.py --increment

manager-reset:
	python $(SCRIPTS_DIR)/manager_sync.py --reset

research:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make research Q=\"your query\""; \
		exit 1; \
	fi
	python $(SCRIPTS_DIR)/manager_sync.py --research "$(Q)"

cycle: build test manager-tick manager-check

pre-commit: fmt check build test
