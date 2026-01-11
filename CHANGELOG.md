# Changelog

## [0.3.0] - 2026-01-11

### 🎉 Major Release: Official Databricks UI Templates Integration

### Added
- **Zero-Frontend Agent Generation**: Integrated official Databricks app templates (Streamlit, Gradio, Dash)
- **`--ui` flag**: Choose UI framework: `--ui streamlit|gradio|dash` (default: streamlit)
- **DatabricksTemplateIntegrator**: Automated template copying and customization
- **Auto-configuration**: Automatically configures `SERVING_ENDPOINT` in `app.yaml`
- **Auto-bundling**: Adds `databricks.yml` for Asset Bundle deployment
- **Template validation**: Warns about streaming support differences

### Changed
- **Removed `--streaming` flag**: Streaming is now framework-dependent (Streamlit has it, Gradio/Dash don't)
- **Updated default model**: Changed from `databricks-meta-llama-3-1-70b-instruct` to `databricks-claude-sonnet-4`
- **CLI output**: Now shows streaming status per UI framework
- **Simplified workflow**: Generate → Deploy → Run → View (no local testing needed for L2+)

### Fixed
- **JavaScript bugs eliminated**: No more custom frontend code to maintain
- **Browser caching issues**: Official templates handle cache correctly
- **SSE parsing**: Official Streamlit template has battle-tested streaming
- **Endpoint configuration**: Automatically injects model endpoint into app config

### Tested
- ✅ **Streamlit** (`e2e-chatbot-app`): Full streaming support, tested and working
- ✅ **Gradio** (`gradio-chatbot-app`): Batch responses, tested and working
- ✅ **Dash** (`dash-chatbot-app`): Batch responses, tested and working

### Breaking Changes
- **Removed custom FastAPI templates**: Use official Databricks templates instead
- **`--streaming` flag removed**: Controlled by UI framework choice
- **Old generated apps**: Need regeneration with `dat generate chatbot <name> --ui streamlit`

### Documentation
- Updated CLI examples to show `--ui` usage
- Added streaming support comparison table
- Documented template integration architecture

### Technical Details
- Uses `databricks-app-templates-research` as template source
- Copies entire template directory, then customizes
- Injects `databricks.yml` for Bundle deployment
- Replaces `valueFrom: "serving-endpoint"` with direct model endpoint value

## [0.2.3] - 2026-01-07

### Added
- CLI now supports `--model` flag to specify custom model endpoint
- CLI now supports `--enable-rag` flag for L2 assistants
- CLI now supports `--streaming` flag to control streaming behavior
- CLI now supports `--output-dir` flag for custom output location
- Changed default model to `databricks-meta-llama-3-1-70b-instruct`

### Fixed (L2 Assistant)
- Fixed L2 `invoke_handler` to handle both dict and ResponsesAgentRequest inputs
- Fixed L2 ResponsesAgentResponse output format with correct nested structure
- Fixed L2 JavaScript parsing for non-streaming responses
- Added full streaming support to L2 with correct SSE parsing
- Updated L2 to respect `streaming` config (was hardcoded to false)

## [0.2.2] - 2026-01-06

### Fixed
- ✅ Correct ResponsesAgent output format: `{"type": "message", "content": [{"type": "output_text", "text": "..."}]}`
- ✅ Added required `id` field to output messages
- ✅ Fixed `/invocations` endpoint (not `/api/invocations`)
- ✅ Fixed JavaScript to parse nested ResponsesAgent format: `data.output[0].content[0].text`
- ✅ Both streaming and non-streaming modes now work end-to-end

### Changed
- Optimized `agent.py` from 100 to 89 lines (11% reduction)
- Removed debug error handling for cleaner production code
- Simplified message extraction logic

### Verified
- ✅ Non-streaming: Returns complete response instantly
- ✅ Streaming: Word-by-word with configurable 50ms delay
- ✅ API tested with curl before deployment
- ✅ Deployed and tested on Databricks Apps

## [0.2.1] - 2026-01-06

### Fixed
- ✅ Correct import path for MLflow AgentServer: `mlflow.genai.agent_server.server`
- ✅ Updated requirements to `mlflow>=3.6.0` for full AgentServer support
- ✅ Fixed session management in L2 assistant templates
- ✅ Improved async handling in `@invoke` and `@stream` decorators

### Changed
- Refactored both L1 (chatbot) and L2 (assistant) to use official `@invoke`/`@stream` pattern
- Removed all manual `/api/invocations` implementations (AgentServer auto-handles)
- Simplified server initialization with AgentServer auto-discovery of decorators

## [0.2.0] - 2026-01-06

### Added
- Short CLI aliases: `dbat` and `dat` (easier to type!)
- FastAPI-based agent backends with OpenAPI schema
- Streaming support via Server-Sent Events (SSE)
- Auto-generated API documentation at `/docs`
- Compatibility with all 6 official Databricks UI templates
- Automated monitoring for upstream template changes

### Changed
- **Breaking**: Migrated from Flask to FastAPI
- **Breaking**: New file structure: `agent.py` + `start_server.py` (replaces `app.py`)
- **Breaking**: API endpoint: `/api/invocations` (OpenAI format, replaces `/api/chat`)
- Simplified streaming implementation (server-side delay)
- Updated all templates to follow official Databricks patterns

### Removed
- Flask dependency
- Complex client-side streaming logic
- AgentServer fallback (simplified)

## [0.1.x] - Earlier versions

Previous releases before OpenAI API migration.
