# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Literate is a **Literate Data Modeling** system that allows creating data models using natural language descriptions in Markdown format, then processes them into structured formats (JSON, YAML, HTML, PDF). It combines a domain-specific language (DSL) parser, AI integrations for model enhancement, diagram generation, and a Next.js web interface for model visualization.

## Architecture

### Core Components

- **ldm/** - Main Literate Data Modeling engine
  - `do_build_ldm.py` - Primary DSL parser and model builder (ldm/do_build_ldm.py:25-394)
  - `do_cycle.py` - Model refinement pipeline with AI feedback (ldm/do_cycle.py:7-62)
  - `ldm_parse_fns.py` - Parsing functions for different element types
  - `ldm_renderers.py` - Output renderers (HTML, Markdown, PDF)

- **dull_dsl/** - Domain-Specific Language parser
  - `dull_parser_classes.py` - Parser class definitions for different line types
  - `dull_build.py` - DSL build system

- **ai_apis/** - AI service integrations
  - `class_ai_assistant.py` - Base AI assistant class (ai_apis/class_ai_assistant.py:12-50)
  - `class_ai_claude.py` - Claude API integration
  - `class_ai_openrouter.py` - OpenRouter API integration
  - `do_ai.py` - AI orchestration script

- **utils/** - Shared utilities
  - `util_all_fmk.py` - Core FMK utility functions
  - `class_container.py` - Data container classes
  - Various format converters (HTML, PDF, diagrams)

- **ldm_site/** - Next.js web interface for model visualization
  - SPARQL/RDF integration for semantic data queries
  - TypeScript/React frontend

### Data Flow

1. **Input**: Markdown files with structured annotations (e.g., `ldm/ldm_models/Literate/Literate.md`)
2. **Parsing**: DSL parser processes markdown into structured data
3. **Processing**: Model builders create JSON/YAML representations
4. **Enhancement**: AI APIs can provide feedback and improvements
5. **Output**: Multiple formats (HTML, PDF, diagrams) generated
6. **Visualization**: Next.js site provides web interface

## Common Development Commands

### Python Environment
```bash
# Setup with Poetry
poetry install

# Activate environment (if not using poetry shell)
poetry shell
```

### Main Build Process
```bash
# Build LDM models (primary entry point)
python ldm/do_build_ldm.py

# Run model processing cycle
python ldm/do_cycle.py
```

### Next.js Web Interface
```bash
# Navigate to web interface directory
cd ldm_site

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
npm start
```

### AI Integration
```bash
# Run AI processing
python ai_apis/do_ai.py

# Test specific AI providers
python trials/try_claude.py
```

### Utilities and Diagrams
```bash
# Generate diagrams
python diagrams/do_graph.py
python diagrams/do_plantweb.py

# Process utilities
python utils/util_cycle.py
```

## Model Directory Structure

Models are stored in `ldm/ldm_models/[ModelName]/`:
- `ModelName.md` - Source markdown file
- `ModelName_results/` - Generated outputs (JSON, HTML, PDF)
- `ModelName_cycles/` - AI refinement iterations

## Configuration

- **pyproject.toml** - Poetry dependencies and Python project configuration
- **ai_configs/** - AI model configurations (OpenRouter, Together)
- **ldm_site/package.json** - Node.js dependencies for web interface
- **Settings in ldm/do_build_ldm.py:333-342** - Core model processing specifications

## Key File Patterns

- **Parser specifications**: `ldm/do_build_ldm.py:34-331` defines DSL grammar
- **Model outputs**: Generated files follow pattern `ModelName_[stage]_[format].[ext]`
- **AI contexts**: Documents in `ai_docs/` provide context for AI processing
- **Utilities**: `utils/util_*.py` files contain specialized processing functions

## Development Notes

- Uses Poetry for Python dependency management
- Supports multiple AI providers (Claude, OpenAI, OpenRouter)
- Generates multiple output formats from single markdown source
- Web interface uses TypeScript/Next.js with Tailwind CSS
- Extensive diagram generation capabilities (Mermaid, PlantUML)