from nicegui import ui
from gui.components.buttons import nav_button

def page_shell(active: str | None = None) -> None:
    ui.colors(primary="#2563eb", secondary="#0f766e", accent="#f59e0b")
    ui.add_head_html(
        """
        <script>
            (() => {
            const applyAncTheme = () => {
                document.body?.classList.toggle(
                    'anc-dark',
                    localStorage.getItem('anc-theme') === 'dark'
                );
            };
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', applyAncTheme);
            } else {
                applyAncTheme();
            }
            })();
        </script>
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
            body.anc-dark { background: #101828; color: #eef2f6; }
            body.anc-dark .q-layout,
            body.anc-dark .q-page-container,
            body.anc-dark .nicegui-content { background: #101828; color: #eef2f6; }
            body.anc-dark .topbar { border-bottom-color: #243247; background: rgba(16,24,40,.92); color: #eef2f6; }
            body.anc-dark .surface { background: #182230; border-color: #314158; color: #eef2f6; box-shadow: 0 10px 28px rgba(0,0,0,.18); }
            body.anc-dark .surface .q-card__section,
            body.anc-dark .surface .q-item,
            body.anc-dark .surface .q-toggle__label,
            body.anc-dark .surface .q-checkbox__label,
            body.anc-dark .surface .q-radio__label { color: #eef2f6; }
            body.anc-dark .muted { color: #a8b3c4; }
            body.anc-dark .text-slate-900 { color: #eef2f6; }
            body.anc-dark .log-box { background: #0b1220; color: #dce4f0; }
            body.anc-dark .q-field__control { color: #eef2f6; }
            body.anc-dark .q-field--outlined .q-field__control::before { border-color: #4b5d75; }
            body.anc-dark .q-field--outlined.q-field--focused .q-field__control::before,
            body.anc-dark .q-field--outlined.q-field--focused .q-field__control::after { border-color: #7dd3fc; }
            body.anc-dark .q-field__native,
            body.anc-dark .q-field__input,
            body.anc-dark .q-field__prefix,
            body.anc-dark .q-field__suffix,
            body.anc-dark .q-field__label,
            body.anc-dark .q-field__append,
            body.anc-dark .q-field__prepend { color: #e5edf7; }
            body.anc-dark .q-field__native::placeholder,
            body.anc-dark .q-field__input::placeholder { color: #9aa8ba; opacity: 1; }
            body.anc-dark .q-menu,
            body.anc-dark .q-dialog__inner > div { background: #182230; color: #eef2f6; }
            body.anc-dark .q-item.q-manual-focusable--focused,
            body.anc-dark .q-item--active,
            body.anc-dark .q-item:hover { background: #253247; color: #f8fafc; }
            body.anc-dark .stage-card {
                background: #111827 !important;
                border-color: #334155 !important;
                color: #dbeafe !important;
            }
            body.anc-dark .stage-icon,
            body.anc-dark .stage-status { color: inherit; }
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
                nav_button("Settings", "/settings", "settings", active == "/settings")
