from nicegui import ui

from gui.components.buttons import back_button
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.page_title import page_title
from gui.routes import get_path
from gui.services.settings_service import API_KEY_FIELDS, MODEL_FIELDS, load_settings, save_settings


XAI_USAGE_URL = "https://console.x.ai/team/default/usage"


@ui.page(get_path("Settings"))
def settings_page() -> None:
    page_shell(get_path("Settings"))
    settings = load_settings()
    inputs: dict[str, ui.input] = {}

    def save() -> None:
        save_settings(
            {
                key: field.value or ""
                for key, field in inputs.items()
            }
        )
        ui.notify("Settings saved to .env", type="positive")

    def reset() -> None:
        fresh_settings = load_settings()
        for key, field in inputs.items():
            field.value = fresh_settings.get(key, "")
        ui.notify("Settings reloaded", type="info")

    with content():
        back_button(get_path("Home"))
        page_title("Settings", "Manage credentials, model choices, theme, and xAI usage access.")

        with ui.row().classes("w-full items-stretch gap-5"):
            with ui.card().classes("surface flex-1 p-6 gap-4"):
                with ui.row().classes("w-full items-center justify-between"):
                    with ui.column().classes("gap-1"):
                        ui.label("Appearance").classes("text-xl font-semibold")
                        ui.label("Choose the interface theme for this browser.").classes("muted text-sm")

                    theme_switch = ui.switch("Dark theme", value=False)
                    theme_switch.on_value_change(
                        lambda event: ui.run_javascript(
                            f"""
                            const isDark = {str(bool(event.value)).lower()};
                            localStorage.setItem('anc-theme', isDark ? 'dark' : 'light');
                            document.body.classList.toggle('anc-dark', isDark);
                            """
                        )
                    )

                ui.run_javascript(
                    """
                    const isDark = localStorage.getItem('anc-theme') === 'dark';
                    document.body.classList.toggle('anc-dark', isDark);
                    """
                )

                async def sync_theme_switch() -> None:
                    is_dark = await ui.run_javascript(
                        "localStorage.getItem('anc-theme') === 'dark'"
                    )
                    theme_switch.value = bool(is_dark)

                ui.timer(0.1, sync_theme_switch, once=True)

            with ui.card().classes("surface flex-1 p-6 gap-4"):
                ui.label("xAI Usage").classes("text-xl font-semibold")
                ui.label("Open xAI Usage Explorer to review spend, token usage, API keys, and model filters.").classes(
                    "muted text-sm leading-6"
                )
                ui.button(
                    "Open Usage Explorer",
                    icon="open_in_new",
                    on_click=lambda: ui.run_javascript(f"window.open('{XAI_USAGE_URL}', '_blank')"),
                ).props("color=primary")

        with ui.card().classes("surface w-full p-6 gap-4"):
            ui.label("API Keys").classes("text-xl font-semibold")
            with ui.grid(columns=3).classes("w-full gap-4"):
                for field in API_KEY_FIELDS:
                    inputs[field.key] = ui.input(
                        field.label,
                        value=settings.get(field.key, ""),
                        password=True,
                        password_toggle_button=True,
                    ).props("outlined").classes("w-full")

        with ui.card().classes("surface w-full p-6 gap-4"):
            ui.label("Models").classes("text-xl font-semibold")
            with ui.grid(columns=2).classes("w-full gap-4"):
                for field in MODEL_FIELDS:
                    inputs[field.key] = ui.input(
                        field.label,
                        value=settings.get(field.key, field.default),
                    ).props("outlined").classes("w-full")

        with ui.row().classes("w-full justify-end gap-3"):
            ui.button("Reload", icon="refresh", on_click=reset).props("outline color=grey-8")
            ui.button("Save Settings", icon="save", on_click=save).props("color=primary")
