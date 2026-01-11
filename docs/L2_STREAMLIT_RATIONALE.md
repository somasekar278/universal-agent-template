# L2 (Memory + RAG) - Streamlit Only

## Decision

**L2+ agents (assistant, planner, agentic_rag) require Streamlit UI.**

```bash
# ✅ Works
dat generate assistant my-assistant --ui streamlit

# ❌ Error
dat generate assistant my-assistant --ui gradio
dat generate assistant my-assistant --ui dash
```

---

## Rationale

### Official Template Capabilities

| Feature | Streamlit | Gradio | Dash |
|---------|-----------|--------|------|
| **Streaming** | ✅ Built-in | ❌ Not in template | ❌ Not in template |
| **Session State** | ✅ `st.session_state` | ⚠️  Requires `gr.State()` | ⚠️  Requires `dcc.Store` |
| **Persistent History** | ✅ Automatic | ❌ Manual implementation | ❌ Manual implementation |
| **Memory Integration** | ✅ 2 hours | ⚠️  8+ hours | ⚠️  12+ hours |

### Why Streamlit?

1. **Official Template Support**
   - The `e2e-chatbot-app` Streamlit template already has:
     - Session state management (`st.session_state.history`)
     - Streaming support (`query_endpoint_stream`)
     - Persistent conversation context across requests

2. **Minimal Modifications for L2**
   ```python
   # What's already there (L1)
   if "history" not in st.session_state:
       st.session_state.history = []

   # What L2 adds (simple injection)
   if "session_id" not in st.session_state:
       st.session_state.session_id = generate_session_id()
   
   # Replace in-memory history with MemoryManager
   st.session_state.history = memory_manager.get_history(session_id)
   ```

3. **No Custom Frontend Code**
   - **Philosophy**: Use official templates, don't build custom solutions
   - Gradio/Dash would require custom session management = violates v0.3.0 philosophy

### Why Not Gradio/Dash?

#### Gradio Issues:
- ❌ No streaming in official template (line 74-76 says "see docs for streaming")
- ❌ History is passed as function parameter, not persisted
- ❌ Would need custom `gr.State()` implementation
- ⏱️  Estimate: 8+ hours of custom work

#### Dash Issues:
- ❌ No streaming in official template
- ❌ Uses custom `DatabricksChatbot` component with unclear internals
- ❌ State management via Dash callbacks (complex)
- ⏱️  Estimate: 12+ hours of custom work

---

## Implementation Status

### ✅ L1 (Chatbot - No Memory)
All frameworks work great for stateless chatbots:
```bash
dat generate chatbot my-bot --ui streamlit   # ✅ Streaming
dat generate chatbot my-bot --ui gradio      # ✅ Batch
dat generate chatbot my-bot --ui dash        # ✅ Batch
```

### 🚧 L2 (Assistant - Memory + RAG)
Only Streamlit supported:
```bash
dat generate assistant my-assistant          # ✅ Auto-uses Streamlit
dat generate assistant doc-bot --enable-rag  # ✅ With RAG
```

### 📋 Future (If User Requests)
If there's a real user need for Gradio/Dash with memory:
1. Wait for official Databricks templates to add streaming + session state
2. OR: Build custom integration if there's strong demand

**Current Decision**: Don't build custom solutions unless there's a clear need.

---

## Error Messages

When users try L2 with non-Streamlit UI:

```bash
$ dat generate assistant my-bot --ui gradio

❌ ASSISTANT (L2+) requires Streamlit UI
   Reason: Official Databricks templates only support memory + streaming in Streamlit
   Gradio/Dash lack built-in session persistence and streaming

💡 Use: dat generate assistant my-bot --ui streamlit
```

---

## References

- **Official Templates**: [databricks/app-templates](https://github.com/databricks/app-templates)
- **Streamlit Template**: `e2e-chatbot-app` (lines 92-93: session state)
- **Gradio Template**: `gradio-chatbot-app` (lines 74-76: no streaming note)
- **Dash Template**: `dash-chatbot-app` (uses custom component)
- **Philosophy**: v0.3.0 decision to use official templates, not build custom frontend
