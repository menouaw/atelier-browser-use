import gradio as gr

from src.webui.webui_manager import WebuiManager
from src.webui.components.agent_settings_tab import create_agent_settings_tab
from src.webui.components.browser_settings_tab import create_browser_settings_tab
from src.webui.components.browser_use_agent_tab import create_browser_use_agent_tab
from src.webui.components.deep_research_agent_tab import create_deep_research_agent_tab
from src.webui.components.load_save_config_tab import create_load_save_config_tab
from src.webui.components.workshop_1_tab import create_workshop_1_tab
from src.webui.components.workshop_2_tab import create_workshop_2_tab
from src.webui.components.workshop_3_tab import create_workshop_3_tab

theme_map = {
    "Default": gr.themes.Default(),
    "Soft": gr.themes.Soft(),
    "Monochrome": gr.themes.Monochrome(),
    "Glass": gr.themes.Glass(),
    "Origin": gr.themes.Origin(),
    "Citrus": gr.themes.Citrus(),
    "Ocean": gr.themes.Ocean(),
    "Base": gr.themes.Base()
}


def create_ui(theme_name="Ocean"):
    css = """
    .gradio-container {
        width: 70vw !important; 
        max-width: 70% !important; 
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 10px !important;
    }
    .header-text {
        text-align: center;
        margin-bottom: 20px;
    }
    .tab-header-text {
        text-align: center;
    }
    .theme-section {
        margin-bottom: 10px;
        padding: 15px;
        border-radius: 10px;
    }
    """

    # dark mode in default
    js_func = """
    function refresh() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """

    ui_manager = WebuiManager()

    with gr.Blocks(
            title="Browser Use", theme=theme_map[theme_name], css=css, js=js_func,
    ) as demo:
        with gr.Row():
            gr.Markdown(
                """
                # 🌐 Browser Use
                ### Panorama des fonctionnalités d'agent web
                """,
                elem_classes=["header-text"],
            )

        with gr.Tabs():

            with gr.TabItem("⚙️ Param. Agent"):
                create_agent_settings_tab(ui_manager)

            with gr.TabItem("🌐 Param. Navigateur"):
                create_browser_settings_tab(ui_manager)

            with gr.TabItem("🤖 Exécuter l'agent"):
                create_browser_use_agent_tab(ui_manager)

            with gr.TabItem("🤖 Atelier Browser Use"):
                gr.Markdown(
                    """
                    ### Atelier sur l'utilisation de Browser Use
                    """,
                    elem_classes=["tab-header-text"],
                )
                with gr.Tabs():
                    with gr.TabItem("OrangeHRM"):
                        create_workshop_1_tab(ui_manager)
                    with gr.TabItem("Automation Exercise"):
                        create_workshop_2_tab(ui_manager)
                    with gr.TabItem("Stress-Test"):
                        create_workshop_3_tab(ui_manager)

            with gr.TabItem("🎁 Agents personnalisés"):
                gr.Markdown(
                    """
                    ### Agents construits à partir de Browser Use
                    """,
                    elem_classes=["tab-header-text"],
                )
                with gr.Tabs():
                    with gr.TabItem("Recherche approfondie"):
                        create_deep_research_agent_tab(ui_manager)

            with gr.TabItem("📁 Charger & Sauvegarder"):
                create_load_save_config_tab(ui_manager)

    return demo