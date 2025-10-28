.PHONY: help setup build build-plugin build-mcp build-all clean publish-plugin publish-mcp publish-all setup-publish

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build System
setup: ## Install Python dependencies for build script
	@echo "Installing build script dependencies..."
	@pip install -r requirements.txt
	@echo "✓ Dependencies installed"

build: build-all ## Build all artifacts (alias for build-all)

build-plugin: ## Build Rust plugin + JS bindings
	@python build.py plugin

build-mcp: ## Build TypeScript MCP server
	@python build.py mcp

build-all: ## Build both plugin and MCP server
	@python build.py all

clean: ## Clean all build artifacts
	@python build.py all --clean

# Publishing

setup-publish: ## Install Python dependencies for publish script
	@echo "Installing publish script dependencies..."
	@pip install -r requirements-publish.txt
	@echo "✓ Dependencies installed"

publish-plugin-patch: ## Publish plugin with patch version bump
	@./publish.py plugin --bump patch

publish-plugin-minor: ## Publish plugin with minor version bump
	@./publish.py plugin --bump minor

publish-plugin-major: ## Publish plugin with major version bump
	@./publish.py plugin --bump major

publish-mcp-patch: ## Publish MCP server with patch version bump
	@./publish.py mcp --bump patch

publish-mcp-minor: ## Publish MCP server with minor version bump
	@./publish.py mcp --bump minor

publish-mcp-major: ## Publish MCP server with major version bump
	@./publish.py mcp --bump major

publish-all-patch: ## Publish both packages with patch version bump
	@./publish.py all --bump patch

publish-all-minor: ## Publish both packages with minor version bump
	@./publish.py all --bump minor

publish-all-major: ## Publish both packages with major version bump
	@./publish.py all --bump major

dry-run-plugin: ## Dry run publish for plugin (patch bump)
	@./publish.py plugin --bump patch --dry-run

dry-run-mcp: ## Dry run publish for MCP server (patch bump)
	@./publish.py mcp --bump patch --dry-run

dry-run-all: ## Dry run publish for all packages (patch bump)
	@./publish.py all --bump patch --dry-run
