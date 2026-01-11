# Release v0.3.0 - Zero-Frontend Agent Generation

**Release Date**: January 11, 2026
**Package Size**: 190 KB (wheel) / 159 KB (source)

## 🎉 Major Changes

### Official Databricks UI Templates Integration
- **Zero custom frontend code** - Uses battle-tested Databricks templates
- **Auto-download on first use** - Templates cached in `~/.databricks-agent-toolkit/templates/`
- **Always up-to-date** - Clones from official GitHub repo

### Supported UI Frameworks
| Framework | Template | Streaming | Status |
|-----------|----------|-----------|--------|
| **Streamlit** | `e2e-chatbot-app` | ✅ Yes | Recommended |
| **Gradio** | `gradio-chatbot-app` | ❌ Batch | Supported |
| **Dash** | `dash-chatbot-app` | ❌ Batch | Supported |

### CLI Updates
```bash
# New --ui flag (default: streamlit)
dat generate chatbot my-bot --ui streamlit  # Streaming ✅
dat generate chatbot my-bot --ui gradio     # Simple UI
dat generate chatbot my-bot --ui dash       # Dash UI

# Removed --streaming flag (framework-dependent now)
# Changed default model to databricks-claude-sonnet-4
```

## ✅ What's Fixed

### Eliminated All JavaScript Bugs
- No more browser caching issues
- No more SSE parsing errors
- No more inline handler problems
- No more template literal conflicts

### Automated Configuration
- Auto-injects `SERVING_ENDPOINT` into `app.yaml`
- Auto-creates `databricks.yml` for Asset Bundles
- Auto-downloads templates on first use

### Production-Ready
- All 3 UI frameworks tested and working on Databricks Apps
- Streamlit has full streaming support
- Clean deployment workflow: Generate → Deploy → Run → View

## 📦 Installation

```bash
pip install databricks-agent-toolkit==0.3.0
```

### First-Time Setup
On first `dat generate`, templates auto-download (~20MB):
```
📥 Downloading Databricks app templates (first time only)...
✅ Templates downloaded to: ~/.databricks-agent-toolkit/templates
```

## 🚀 Quick Start

```bash
# Generate L1 chatbot with Streamlit
dat generate chatbot my-bot

# Deploy to Databricks
cd my-bot
databricks bundle deploy && databricks bundle run

# Open the app URL and test streaming!
```

## 🔧 Technical Details

### Template Source
- **Repo**: https://github.com/databricks/app-templates
- **Local Cache**: `~/.databricks-agent-toolkit/templates/`
- **First Use**: Auto-clones with `git clone --depth 1`

### What's Included in Package
- Core toolkit (190 KB)
- Jinja2 templates for custom scaffolds
- Memory, evaluation, optimization modules
- **Not included**: Docs, tests, examples, templates (auto-download)

### What's Excluded
- ❌ `docs/` - 16 markdown files
- ❌ `tests/` - Test suite
- ❌ `scripts/` - Build scripts
- ❌ `examples/` - Example apps
- ❌ Templates - Auto-downloaded on first use

## 📊 Breaking Changes

### Removed
- `--streaming` flag - Now framework-dependent
- Custom FastAPI templates - Use official templates instead

### Changed
- Default model: `databricks-meta-llama-3-1-70b-instruct` → `databricks-claude-sonnet-4`
- Template generation: Custom → Official Databricks templates

### Migration
Old apps need regeneration:
```bash
# Old (v0.2.x)
dat generate chatbot my-bot --streaming

# New (v0.3.0)
dat generate chatbot my-bot --ui streamlit  # Has streaming by default
```

## 🎯 Next Steps (L2 - Memory)

**Upcoming in v0.3.1:**
- Memory integration for L2 Assistant
- Lakebase connection for conversation history
- Session management UI components
- Gradio streaming support (optional)

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full details.

## 🐛 Known Issues

- L2 memory integration not yet implemented for official templates
- Gradio/Dash templates don't support streaming (by Databricks design)
- Memory UI components may appear in L1 apps (cosmetic only, no impact)

## 🙏 Credits

- **Databricks** for official app templates
- **Streamlit, Gradio, Dash** for UI frameworks
- **MLflow** for agent serving

---

**Ready to publish to PyPI!** 🚀
