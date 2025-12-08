# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import streamlit as st

from llama_stack_ui.distribution.ui.modules.api import llama_stack_api


def fetch_models_from_xc_url():
    """Fetch models from the XC URL and update session state"""
    xc_url = st.session_state.get("xc_url", "http://llamastack:8321")
    
    # Set loading state
    st.session_state["models_loading"] = True
    st.session_state["models_error"] = None
    st.session_state["models_list"] = []
    
    # Fetch models from XC URL
    success, models_list, error_message = llama_stack_api.fetch_models_from_url(xc_url)
    
    # Update session state based on results
    st.session_state["models_loading"] = False
    
    if success and models_list:
        st.session_state["models_list"] = models_list
        st.session_state["models_error"] = None
        st.session_state["connection_status"] = "success"
    else:
        st.session_state["models_list"] = []
        st.session_state["models_error"] = error_message or "Failed to fetch models"
        st.session_state["connection_status"] = "error"


def models():
    """
    Inspect available models and display details for a selected one.
    Now supports dynamic XC URL configuration.
    """
    st.header("Models")
    
    # Initialize session state
    if "xc_url" not in st.session_state:
        st.session_state["xc_url"] = "http://llamastack:8321"
    if "models_list" not in st.session_state:
        st.session_state["models_list"] = []
    if "models_loading" not in st.session_state:
        st.session_state["models_loading"] = False
    if "models_error" not in st.session_state:
        st.session_state["models_error"] = None
    if "connection_status" not in st.session_state:
        st.session_state["connection_status"] = None
    if "models_fetched" not in st.session_state:
        st.session_state["models_fetched"] = False

    # XC URL input field
    st.subheader("LlamaStack Configuration")
    
    xc_url = st.text_input(
        "XC URL",
        value=st.session_state["xc_url"],
        help="Enter the LlamaStack endpoint URL to fetch models from",
        key="xc_url_input",
        on_change=lambda: st.session_state.update({"models_fetched": False})
    )
    
    # Update session state if URL changed
    if xc_url != st.session_state["xc_url"]:
        st.session_state["xc_url"] = xc_url
        st.session_state["models_fetched"] = False
    
    # Auto-fetch models when URL changes or on first load
    if not st.session_state["models_fetched"] and xc_url and not st.session_state["models_loading"]:
        with st.spinner("🔄 Fetching models from XC URL..."):
            fetch_models_from_xc_url()
        st.session_state["models_fetched"] = True
        st.rerun()
    
    # Display connection status
    if st.session_state["connection_status"] == "success":
        st.success("✅ Connected to LlamaStack endpoint")
    elif st.session_state["connection_status"] == "error" and st.session_state["models_error"]:
        st.error(f"❌ {st.session_state['models_error']}")
    
    # Show loading state
    if st.session_state["models_loading"]:
        st.info("🔄 Fetching models from XC URL...")
        return
    
    # Display models section
    st.subheader("Available Models")
    
    models_list = st.session_state["models_list"]
    
    if not models_list and st.session_state["models_error"]:
        st.info("No models available. Please check your XC URL configuration.")
        return
    elif not models_list:
        # Fallback to default endpoint for backward compatibility
        try:
            models_list = llama_stack_api.client.models.list()
            if models_list:
                st.info("Using default endpoint. Configure XC URL above to use a different LlamaStack instance.")
        except Exception:
            st.info("No models available. Please configure a valid XC URL.")
            return
    
    if not models_list:
        st.info("No models available.")
        return

    # Filter models to only include LLM models (exclude embedding models, etc.)
    llm_models = [model for model in models_list if hasattr(model, 'api_model_type') and model.api_model_type == "llm"]
    
    if not llm_models:
        st.info("No LLM models available from this endpoint.")
        return

    # Create models info dictionary from filtered LLM models
    models_info = {m.identifier: m.to_dict() for m in llm_models}

    # Let user select and view a model
    selected_model = st.selectbox("Select a model", list(models_info.keys()))
    if selected_model:
        st.json(models_info[selected_model], expanded=True)
