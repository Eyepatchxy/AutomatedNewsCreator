from nicegui import ui
from gui.components.buttons import nav_button

def page_shell(active: str | None = None) -> None:
    ui.colors(primary="#2563eb", secondary="#0f766e", accent="#f59e0b")
    ui.add_head_html(
        """
        <style>
            body { background: #f6f8fb; color: #172033; }
            .dashboard-wrap { max-width: 1180px; margin: 0 auto; padding: 28px 22px 48px; }
            .topbar { border-bottom: 1px solid #e2e8f0; background: rgba(255,255,255,.9); backdrop-filter: blur(8px); }
            .surface { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 10px 28px rgba(15,23,42,.05); }
            .action-card { min-height: 160px; transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease; cursor: pointer; }
            .action-card:hover { transform: translateY(-2px); border-color: #93c5fd; box-shadow: 0 18px 38px rgba(37,99,235,.11); }
            .muted { color: #64748b; }
            .stage-card { min-width: 142px; }
            .log-box { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
        </style>
        """
    )
    with ui.header().classes("topbar text-slate-900"):
        with ui.row().classes("w-full items-center justify-between px-6 py-3"):
            ui.label("Automated News Creator").classes("text-lg font-semibold")
            with ui.row().classes("items-center gap-2"):
                nav_button("Home", "/", "home", active == "home")
                nav_button("YT Workflow", "/yt", "smart_display", active == "yt")
                nav_button("Custom Topic", "/custom-topic", "edit_note", active == "custom")