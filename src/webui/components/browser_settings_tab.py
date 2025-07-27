import os
from distutils.util import strtobool
import gradio as gr
import logging
from gradio.components import Component

from src.webui.webui_manager import WebuiManager
from src.utils import config

logger = logging.getLogger(__name__)

async def close_browser(webui_manager: WebuiManager):
    """
    Close browser
    """
    if webui_manager.bu_current_task and not webui_manager.bu_current_task.done():
        webui_manager.bu_current_task.cancel()
        webui_manager.bu_current_task = None

    if webui_manager.bu_browser_context:
        logger.info("⚠️ Closing browser context when changing browser config.")
        await webui_manager.bu_browser_context.close()
        webui_manager.bu_browser_context = None

    if webui_manager.bu_browser:
        logger.info("⚠️ Closing browser when changing browser config.")
        await webui_manager.bu_browser.close()
        webui_manager.bu_browser = None

def create_browser_settings_tab(webui_manager: WebuiManager):
    """
    Creates a browser settings tab.
    """
    input_components = set(webui_manager.get_components())
    tab_components = {}

    with gr.Group():
        with gr.Row():
            browser_binary_path = gr.Textbox(
                label="Chemin du navigateur",
                lines=1,
                interactive=True,
                placeholder="e.g. '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome'"
            )
            browser_user_data_dir = gr.Textbox(
                label="Chemin des données utilisateur du navigateur",
                lines=1,
                interactive=True,
                placeholder="Laisser vide si vous utilisez vos données utilisateur par défaut",
            )
    with gr.Group():
        with gr.Row():
            use_own_browser = gr.Checkbox(
                label="Utiliser mon navigateur",
                value=bool(strtobool(os.getenv("USE_OWN_BROWSER", "false"))),
                info="Utiliser votre instance de navigateur existante",
                interactive=True
            )
            keep_browser_open = gr.Checkbox(
                label="Garder le navigateur ouvert",
                value=bool(strtobool(os.getenv("KEEP_BROWSER_OPEN", "true"))),
                info="Garder le navigateur ouvert entre les tâches",
                interactive=True
            )
            headless = gr.Checkbox(
                label="Mode Headless",
                value=False,
                info="Exécuter le navigateur sans GUI",
                interactive=True
            )
            disable_security = gr.Checkbox(
                label="Désactiver la sécurité",
                value=False,
                info="Désactiver la sécurité du navigateur",
                interactive=True
            )

    with gr.Group():
        with gr.Row():
            window_w = gr.Number(
                label="Largeur de la fenêtre",
                value=1280,
                info="Largeur de la fenêtre du navigateur",
                interactive=True
            )
            window_h = gr.Number(
                label="Hauteur de la fenêtre",
                value=1100,
                info="Hauteur de la fenêtre du navigateur",
                interactive=True
            )
    with gr.Group():
        with gr.Row():
            cdp_url = gr.Textbox(
                label="URL CDP",
                value=os.getenv("BROWSER_CDP", None),
                info="URL CDP pour le débogage distant du navigateur",
                interactive=True,
            )
            wss_url = gr.Textbox(
                label="URL WSS",
                info="URL WSS pour le débogage distant du navigateur",
                interactive=True,
            )
    with gr.Group():
        with gr.Row():
            save_recording_path = gr.Textbox(
                label="Chemin d'enregistrement",
                placeholder="e.g. ./tmp/record_videos",
                info="Chemin pour enregistrer les enregistrements du navigateur",
                interactive=True,
            )

            save_trace_path = gr.Textbox(
                label="Chemin d'enregistrement",
                placeholder="e.g. ./tmp/traces",
                info="Chemin pour enregistrer les traces de l'agent",
                interactive=True,
            )

        with gr.Row():
            save_agent_history_path = gr.Textbox(
                label="Chemin d'enregistrement",
                value="./tmp/agent_history",
                info="Chemin pour enregistrer l'historique de l'agent",
                interactive=True,
            )
            save_download_path = gr.Textbox(
                label="Chemin d'enregistrement",
                value="./tmp/downloads",
                info="Chemin pour enregistrer les fichiers téléchargés",
                interactive=True,
            )
    tab_components.update(
        dict(
            browser_binary_path=browser_binary_path,
            browser_user_data_dir=browser_user_data_dir,
            use_own_browser=use_own_browser,
            keep_browser_open=keep_browser_open,
            headless=headless,
            disable_security=disable_security,
            save_recording_path=save_recording_path,
            save_trace_path=save_trace_path,
            save_agent_history_path=save_agent_history_path,
            save_download_path=save_download_path,
            cdp_url=cdp_url,
            wss_url=wss_url,
            window_h=window_h,
            window_w=window_w,
        )
    )
    webui_manager.add_components("browser_settings", tab_components)

    async def close_wrapper():
        """Wrapper for handle_clear."""
        await close_browser(webui_manager)

    headless.change(close_wrapper)
    keep_browser_open.change(close_wrapper)
    disable_security.change(close_wrapper)
    use_own_browser.change(close_wrapper)
