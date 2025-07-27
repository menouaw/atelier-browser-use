import json
import os

import gradio as gr
from gradio.components import Component
from typing import Any, Dict, Optional
from src.webui.webui_manager import WebuiManager
from src.utils import config
import logging
from functools import partial

logger = logging.getLogger(__name__)


def update_model_dropdown(llm_provider):
    """
    Update the model name dropdown with predefined models for the selected provider.
    """
    # Use predefined models for the selected provider
    if llm_provider in config.model_names:
        return gr.Dropdown(choices=config.model_names[llm_provider], value=config.model_names[llm_provider][0],
                           interactive=True)
    else:
        return gr.Dropdown(choices=[], value="", interactive=True, allow_custom_value=True)


async def update_mcp_server(mcp_file: str, webui_manager: WebuiManager):
    """
    Update the MCP server.
    """
    if hasattr(webui_manager, "bu_controller") and webui_manager.bu_controller:
        logger.warning("⚠️ Close controller because mcp file has changed!")
        await webui_manager.bu_controller.close_mcp_client()
        webui_manager.bu_controller = None

    if not mcp_file or not os.path.exists(mcp_file) or not mcp_file.endswith('.json'):
        logger.warning(f"{mcp_file} is not a valid MCP file.")
        return None, gr.update(visible=False)

    with open(mcp_file, 'r') as f:
        mcp_server = json.load(f)

    return json.dumps(mcp_server, indent=2), gr.update(visible=True)


def create_agent_settings_tab(webui_manager: WebuiManager):
    """
    Creates an agent settings tab.
    """
    input_components = set(webui_manager.get_components())
    tab_components = {}

    with gr.Group():
        with gr.Column():
            override_system_prompt = gr.Textbox(label="Écraser les instructions par défaut", lines=4, interactive=True)
            extend_system_prompt = gr.Textbox(label="Étendre les instructions par défaut", lines=4, interactive=True, value="Réponds en français.")

    with gr.Group():
        mcp_json_file = gr.File(label="Serveur MCP (json)", interactive=True, file_types=[".json"])
        mcp_server_config = gr.Textbox(label="Configuration MCP", lines=6, interactive=True, visible=False)

    with gr.Group():
        with gr.Row():
            llm_provider = gr.Dropdown(
                choices=[provider for provider, model in config.model_names.items()],
                label="Fournisseur LLM",
                value=os.getenv("DEFAULT_LLM", "google"),
                info="Sélectionnez le fournisseur LLM",
                interactive=True
            )
            llm_model_name = gr.Dropdown(
                label="Modèle LLM",
                choices=config.model_names[os.getenv("DEFAULT_LLM", "google")],
                value=config.model_names[os.getenv("DEFAULT_LLM", "google")][0],
                interactive=True,
                allow_custom_value=True,
                info="Sélectionnez un modèle dans la liste déroulante ou tapez un nom de modèle personnalisé"
            )
        with gr.Row():
            llm_temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.6,
                step=0.1,
                label="Température LLM",
                info="Contrôle la randomisation des sorties du modèle",
                interactive=True
            )

            use_vision = gr.Checkbox(
                label="Utiliser la vision",
                value=True,
                info="Activer la vision (Entrée de capture d'écran en surbrillance dans LLM)",
                interactive=True
            )

            ollama_num_ctx = gr.Slider(
                minimum=2 ** 8,
                maximum=2 ** 16,
                value=16000,
                step=1,
                label="Longueur du contexte Ollama",
                info="Contrôle la longueur maximale du contexte que le modèle doit gérer (moins = plus rapide)",
                visible=False,
                interactive=True
            )

        with gr.Row():
            llm_base_url = gr.Textbox(
                label="URL de base",
                value="",
                info="URL de l'API (si nécessaire)"
            )
            llm_api_key = gr.Textbox(
                label="Clef API",
                type="password",
                value="",
                info="Votre clef API (laisser vide pour utiliser .env)"
            )

    with gr.Group():
        with gr.Row():
            planner_llm_provider = gr.Dropdown(
                choices=[provider for provider, model in config.model_names.items()],
                label="Fournisseur LLM",
                info="Sélectionnez le fournisseur LLM",
                value=None,
                interactive=True
            )
            planner_llm_model_name = gr.Dropdown(
                label="Modèle LLM",
                interactive=True,
                allow_custom_value=True,
                info="Sélectionnez un modèle dans la liste déroulante ou tapez un nom de modèle personnalisé"
            )
        with gr.Row():
            planner_llm_temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.6,
                step=0.1,
                label="Température LLM",
                info="Contrôle la randomisation des sorties du modèle",
                interactive=True
            )

            planner_use_vision = gr.Checkbox(
                label="Utiliser la vision",
                value=False,
                info="Activer la vision (Entrée de capture d'écran en surbrillance dans LLM)",
                interactive=True
            )

            planner_ollama_num_ctx = gr.Slider(
                minimum=2 ** 8,
                maximum=2 ** 16,
                value=16000,
                step=1,
                label="Longueur du contexte Ollama",
                info="Contrôle la longueur maximale du contexte que le modèle doit gérer (moins = plus rapide)",
                visible=False,
                interactive=True
            )

        with gr.Row():
            planner_llm_base_url = gr.Textbox(
                label="URL de base",
                value="",
                info="URL de l'API (si nécessaire)"
            )
            planner_llm_api_key = gr.Textbox(
                label="Clef API",
                type="password",
                value="",
                info="Votre clef API (laisser vide pour utiliser .env)"
            )

    with gr.Row():
        max_steps = gr.Slider(
            minimum=1,
            maximum=1000,
            value=100,
            step=1,
            label="Nombre maximum d'étapes",
            info="Nombre maximum d'étapes que l'agent pourra effectuer",
            interactive=True
        )
        max_actions = gr.Slider(
            minimum=1,
            maximum=100,
            value=10,
            step=1,
            label="Nombre maximum d'actions",
            info="Nombre maximum d'actions que l'agent pourra effectuer par étape",
            interactive=True
        )

    with gr.Row():
        max_input_tokens = gr.Number(
            label="Nombre maximum de jetons",
            value=128000,
            precision=0,
            interactive=True
        )
        tool_calling_method = gr.Dropdown(
            label="Méthode d'appel d'outil",
            value="auto",
            interactive=True,
            allow_custom_value=True,
            choices=['function_calling', 'json_mode', 'raw', 'auto', 'tools', "None"],
            visible=True
        )
    tab_components.update(dict(
        override_system_prompt=override_system_prompt,
        extend_system_prompt=extend_system_prompt,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        llm_temperature=llm_temperature,
        use_vision=use_vision,
        ollama_num_ctx=ollama_num_ctx,
        llm_base_url=llm_base_url,
        llm_api_key=llm_api_key,
        planner_llm_provider=planner_llm_provider,
        planner_llm_model_name=planner_llm_model_name,
        planner_llm_temperature=planner_llm_temperature,
        planner_use_vision=planner_use_vision,
        planner_ollama_num_ctx=planner_ollama_num_ctx,
        planner_llm_base_url=planner_llm_base_url,
        planner_llm_api_key=planner_llm_api_key,
        max_steps=max_steps,
        max_actions=max_actions,
        max_input_tokens=max_input_tokens,
        tool_calling_method=tool_calling_method,
        mcp_json_file=mcp_json_file,
        mcp_server_config=mcp_server_config,
    ))
    webui_manager.add_components("agent_settings", tab_components)

    llm_provider.change(
        fn=lambda x: gr.update(visible=x == "ollama"),
        inputs=llm_provider,
        outputs=ollama_num_ctx
    )
    llm_provider.change(
        lambda provider: update_model_dropdown(provider),
        inputs=[llm_provider],
        outputs=[llm_model_name]
    )
    planner_llm_provider.change(
        fn=lambda x: gr.update(visible=x == "ollama"),
        inputs=[planner_llm_provider],
        outputs=[planner_ollama_num_ctx]
    )
    planner_llm_provider.change(
        lambda provider: update_model_dropdown(provider),
        inputs=[planner_llm_provider],
        outputs=[planner_llm_model_name]
    )

    async def update_wrapper(mcp_file):
        """Wrapper for handle_pause_resume."""
        update_dict = await update_mcp_server(mcp_file, webui_manager)
        yield update_dict

    mcp_json_file.change(
        update_wrapper,
        inputs=[mcp_json_file],
        outputs=[mcp_server_config, mcp_server_config]
    )
