# AI Sentinel: Virtual Security Assistant (Technical Documentation)

## Overview
The Virtual Security Assistant (VSA) is a conversational interface designed to provide users with immediate, context-aware security guidance based on the "AI Sentinel" detection results and organizational policies.

## Backend Implementation
The VSA is implemented as a specialized LLM-driven class within `src/agents.py`.

### 1. Core Logic (`SecurityAdvisor` class)
- **Engine**: OpenAI (GPT-4) or Ollama (Llama 3.2).
- **Context Injection**: The assistant receives a serialized snapshot of the current analysis results, including risk scores, reasoning, and metadata.
- **System Prompting**: A specialized "SOC Advisor" prompt defines its persona: professional, strict but helpful, and focused on organizational security policies.

### 2. State Management
- **Chat History**: Persisted in the Streamlit `session_state` to allow multi-turn conversations.
- **Dynamic Context**: The context is updated every time a new analysis is run, ensuring the assistant always speaks to the latest data.

### 3. Integration Tools
- **LangChain**: Used for message management and LLM interaction.
- **Python-Dotenv**: Loads configuration and API keys.

## Frontend Implementation
- **Streamlit**: Uses `st.chat_message` and `st.chat_input` for a modern, familiar UI.
- **Contextual Awareness**: The UI automatically feeds the current dashboard results into the backend advisor when a query is made.

## Security Controls
- The assistant is restricted from revealing internal secrets but encouraged to explain "Why" a request was blocked based on the `policies.py` definitions.
