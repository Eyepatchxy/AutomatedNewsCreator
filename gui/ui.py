import dotenv
dotenv.load_dotenv()

import json
import time
from dataclasses import dataclass
from typing import Any
from nicegui import app, ui
from paths import PROCESSED_NEWS_FILE, PROJECT_ROOT, CHANNELS_FILE


EXTRACTION_STAGES = [
    "Videos Fetched",
    "Metadata Extracted",
    "Deduplication",
    "Clustering",
    "Verification",
    "Article Generation",
]

VIDEO_STAGES = [
    "Topic Approved",
    "Script Generated",
    "Chunks Generated",
    "Audio Generated",
    "Visuals Generated",
    "Rendering",
    "Final Encoding",
]


@dataclass
class Channel:
    name: str
    handle: str
    channel_id: str
    priority: int = 99


@dataclass
class NewsItem:
    headline: str
    category: str
    confidence: float
    source_count: int
    summary: str = ""


STATE: dict[str, Any] = {
    "selected_channels": [],
    "selected_news": None,
    "custom_topic": None,
}


def load_channels() -> list[Channel]:
    if not CHANNELS_FILE.exists():
        return []

    data = json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    channels = data.get("channels", data if isinstance(data, list) else [])
    return [
        Channel(
            name=item.get("name", "Unnamed channel"),
            handle=item.get("handle", ""),
            channel_id=item.get("id", item.get("channel_id", "")),
            priority=item.get("priority", 99),
        )
        for item in channels
    ]


def load_processed_news() -> list[NewsItem]:
    fallback = [
        NewsItem(
            headline="India's AI policy debate intensifies as startups seek clearer rules",
            category="Technology",
            confidence=0.91,
            source_count=5,
            summary="A concise policy-focused update suitable for a short explainer.",
        ),
        NewsItem(
            headline="Markets open mixed as investors wait for inflation signals",
            category="Business",
            confidence=0.86,
            source_count=4,
            summary="A market brief with clear visual hooks and quick context.",
        ),
        NewsItem(
            headline="New climate report highlights urgent urban heat risks",
            category="Environment",
            confidence=0.88,
            source_count=6,
            summary="A data-led story that works well as a full-length video.",
        ),
    ]

    if not PROCESSED_NEWS_FILE.exists():
        return fallback

    try:
        data = json.loads(PROCESSED_NEWS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback

    if not data:
        return fallback

    items: list[NewsItem] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        headline = (
            item.get("headline")
            or item.get("title")
            or item.get("topic")
            or f"Processed news item {index + 1}"
        )
        category = item.get("category") or item.get("detected_category") or "General"
        confidence = float(item.get("confidence", item.get("score", 0.82)))
        source_count = int(item.get("source_count", len(item.get("sources", [])) or 1))
        summary = item.get("summary") or item.get("description") or ""
        items.append(NewsItem(headline, category, confidence, source_count, summary))

    return items or fallback


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


def nav_button(label: str, target: str, icon: str, active: bool = False) -> None:
    color = "primary" if active else "grey-7"
    ui.button(label, icon=icon, on_click=lambda: ui.navigate.to(target)).props(
        f"flat color={color}"
    )


def content() -> ui.column:
    return ui.column().classes("dashboard-wrap w-full gap-6")


def page_title(title: str, subtitle: str | None = None) -> None:
    with ui.column().classes("gap-1"):
        ui.label(title).classes("text-3xl font-bold tracking-tight")
        if subtitle:
            ui.label(subtitle).classes("muted text-base")


def back_button(target: str) -> None:
    ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.to(target)).props(
        "flat color=grey-8"
    )


def action_card(title: str, subtitle: str, icon: str, target: str) -> None:
    with ui.card().classes("surface action-card p-6 flex-1").on(
        "click", lambda: ui.navigate.to(target)
    ):
        ui.icon(icon).classes("text-4xl text-primary")
        ui.label(title).classes("text-xl font-semibold")
        ui.label(subtitle).classes("muted text-sm leading-6")


def stat_card(label: str, value: str, icon: str) -> None:
    with ui.card().classes("surface p-5 flex-1"):
        with ui.row().classes("items-center gap-3"):
            ui.icon(icon).classes("text-2xl text-primary")
            with ui.column().classes("gap-0"):
                ui.label(value).classes("text-2xl font-bold")
                ui.label(label).classes("muted text-sm")


def stage_classes(status: str) -> str:
    return {
        "pending": "border-slate-200 bg-white text-slate-500",
        "running": "border-blue-300 bg-blue-50 text-blue-800",
        "completed": "border-emerald-300 bg-emerald-50 text-emerald-800",
        "failed": "border-red-300 bg-red-50 text-red-800",
    }[status]


def stage_icon(status: str) -> str:
    return {
        "pending": "radio_button_unchecked",
        "running": "sync",
        "completed": "check_circle",
        "failed": "error",
    }[status]


class ProgressPipeline:
    def __init__(self, stages: list[str], log_prefix: str, eta: str) -> None:
        self.stages = stages
        self.log_prefix = log_prefix
        self.current_index = 0
        self.started_at = time.monotonic()
        self.completed = False

        with ui.card().classes("surface p-6 w-full gap-5"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Pipeline").classes("text-xl font-semibold")
                self.elapsed_label = ui.label("Elapsed: 00:00").classes("muted")

            with ui.linear_progress(value=0, show_value=False, size="20px").classes("w-full") as progress:
                self.progress = progress
                self.progress_value_label = ui.label(self._format_progress(0)).classes(
                    "absolute-center text-white"
                ).style("font-size: 0.875rem")
            with ui.row().classes("w-full gap-3"):
                self.stage_cards: list[dict[str, Any]] = [
                    self._make_stage_card(stage, "running" if i == 0 else "pending")
                    for i, stage in enumerate(stages)
                ]

            with ui.row().classes("w-full gap-4"):
                with ui.card().classes("surface p-4 flex-1"):
                    ui.label("Live Logs").classes("font-semibold")
                    self.log = ui.log(max_lines=80).classes(
                        "log-box h-64 w-full rounded bg-slate-950 p-3 text-sm text-slate-100"
                    )
                with ui.card().classes("surface p-4 w-64"):
                    ui.label("ETA").classes("font-semibold")
                    self.eta_label = ui.label(eta).classes("text-2xl font-bold")
                    ui.label("Placeholder until real job telemetry is connected.").classes(
                        "muted text-sm leading-5"
                    )

        self.log.push(f"{self.log_prefix}: queued")
        self.timer = ui.timer(1.1, self.tick)

    def _make_stage_card(self, stage: str, status: str) -> dict[str, Any]:
        with ui.card().classes(f"stage-card flex-1 border p-4 {stage_classes(status)}") as card:
            icon = ui.icon(stage_icon(status)).classes("stage-icon text-2xl")
            ui.label(stage).classes("font-semibold leading-5")
            label = ui.label(status.title()).classes("stage-status text-xs uppercase tracking-wide")
        return {"card": card, "icon": icon, "label": label}

    def _set_stage(self, index: int, status: str) -> None:
        stage = self.stage_cards[index]
        card = stage["card"]
        card.classes(replace=f"stage-card flex-1 border p-4 {stage_classes(status)}")
        stage["icon"].name = stage_icon(status)
        stage["label"].text = status.title()

    @staticmethod
    def _format_progress(value: float) -> str:
        percent = max(0.00, min(value, 1.00)) * 100
        return f"{percent:.2f}".rstrip("0").rstrip(".") + "%"

    def _set_progress(self, value: float) -> None:
        self.progress.value = value
        self.progress_value_label.text = self._format_progress(value)

    def tick(self) -> None:
        elapsed = int(time.monotonic() - self.started_at)
        self.elapsed_label.text = f"Elapsed: {elapsed // 60:02d}:{elapsed % 60:02d}"

        if self.completed:
            return

        self._set_stage(self.current_index, "completed")
        self.log.push(f"{self.log_prefix}: {self.stages[self.current_index]} completed")
        self.current_index += 1
        self._set_progress(self.current_index / len(self.stages))

        if self.current_index >= len(self.stages):
            self.completed = True
            self.log.push(f"{self.log_prefix}: complete")
            self.eta_label.text = "Complete"
            self.timer.cancel()
            return

        self._set_stage(self.current_index, "running")
        self.log.push(f"{self.log_prefix}: {self.stages[self.current_index]} running")


def selected_channel_names() -> list[str]:
    ids = set(STATE["selected_channels"])
    return [channel.name for channel in load_channels() if channel.channel_id in ids]


@ui.page("/")
def home_page() -> None:
    page_shell("home")
    with content():
        with ui.column().classes("min-h-[70vh] w-full items-center justify-center gap-8"):
            ui.label("Automated News Creator").classes(
                "text-center text-5xl font-bold tracking-tight"
            )
            with ui.row().classes("w-full max-w-4xl gap-5"):
                action_card(
                    "Generate Using YT Channels",
                    "Fetch, verify, cluster, and turn channel news into videos.",
                    "smart_display",
                    "/yt",
                )
                action_card(
                    "Generate Using Custom Topic",
                    "Start with your own topic and move straight into video creation.",
                    "topic",
                    "/custom-topic",
                )


@ui.page("/yt")
def yt_workflow_page() -> None:
    page_shell("yt")
    with content():
        back_button("/")
        page_title("YT Workflow", "Choose whether to process channel news or create videos from processed stories.")
        with ui.row().classes("w-full gap-5"):
            action_card(
                "Fetch & Process News",
                "Select channels first, then confirm before extraction begins.",
                "travel_explore",
                "/yt/channels",
            )
            action_card(
                "Generate Videos From Processed News",
                "Pick a processed story and configure the video output.",
                "movie_creation",
                "/yt/processed-news",
            )


@ui.page("/yt/channels")
def channel_selection_page() -> None:
    page_shell("yt")
    channels = load_channels()
    visible_channels = channels.copy()

    with content():
        back_button("/yt")
        page_title("Select Channels", "Choose the channels to include in the next extraction run.")

        selected = set(STATE["selected_channels"])
        list_container = ui.column().classes("w-full gap-3")

        def render_list() -> None:
            list_container.clear()
            with list_container:
                if not visible_channels:
                    ui.label("No channels match your search.").classes("muted")
                    return
                for channel in visible_channels:
                    with ui.card().classes("surface w-full p-4"):
                        with ui.row().classes("w-full items-center justify-between gap-4"):
                            with ui.row().classes("items-center gap-3"):
                                checkbox = ui.checkbox(value=channel.channel_id in selected)
                                with ui.column().classes("gap-0"):
                                    ui.label(channel.name).classes("font-semibold")
                                    ui.label(f"{channel.handle} - Priority {channel.priority}").classes(
                                        "muted text-sm"
                                    )

                            def toggle(value: bool, channel_id: str = channel.channel_id) -> None:
                                if value:
                                    selected.add(channel_id)
                                else:
                                    selected.discard(channel_id)
                                STATE["selected_channels"] = list(selected)

                            checkbox.on_value_change(lambda event, fn=toggle: fn(event.value))

        def filter_channels(term: str) -> None:
            query = (term or "").strip().lower()
            visible_channels.clear()
            visible_channels.extend(
                channel
                for channel in channels
                if query in channel.name.lower() or query in channel.handle.lower()
            )
            render_list()

        def set_all(checked: bool) -> None:
            if checked:
                selected.update(channel.channel_id for channel in channels)
            else:
                selected.clear()
            STATE["selected_channels"] = list(selected)
            render_list()

        with ui.card().classes("surface w-full p-5 gap-4"):
            with ui.row().classes("w-full items-center gap-3"):
                ui.input("Search channels", on_change=lambda event: filter_channels(event.value)).props(
                    "outlined clearable"
                ).classes("flex-1")
                ui.button("Select All", icon="done_all", on_click=lambda: set_all(True)).props(
                    "outline"
                )
                ui.button("Deselect All", icon="remove_done", on_click=lambda: set_all(False)).props(
                    "outline color=grey-8"
                )
            render_list()

        with ui.row().classes("w-full justify-end"):
            ui.button(
                "Continue",
                icon="arrow_forward",
                on_click=lambda: ui.navigate.to("/yt/extraction/confirm"),
            ).props("color=primary")


@ui.page("/yt/extraction/confirm")
def extraction_confirmation_page() -> None:
    page_shell("yt")
    selected_names = selected_channel_names()
    estimated_videos = max(len(selected_names) * 12, 0)

    with content():
        back_button("/yt/channels")
        page_title("Confirm Extraction", "Review the workload before starting the channel extraction flow.")
        with ui.row().classes("w-full gap-4"):
            stat_card("Selected Channels", str(len(selected_names)), "subscriptions")
            stat_card("Estimated Videos", str(estimated_videos), "video_library")
            stat_card("Estimated Runtime", f"{max(len(selected_names) * 3, 1)} min", "timer")

        with ui.card().classes("surface w-full p-5"):
            ui.label("Selected Channels").classes("text-lg font-semibold")
            if selected_names:
                for name in selected_names:
                    ui.label(name).classes("py-1")
            else:
                ui.label("No channels selected yet.").classes("muted")

        with ui.row().classes("w-full justify-between"):
            ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.to("/yt/channels")).props(
                "outline color=grey-8"
            )
            ui.button(
                "Start Extraction",
                icon="play_arrow",
                on_click=lambda: ui.navigate.to("/yt/extraction/progress"),
            ).props("color=primary").bind_enabled_from(STATE, "selected_channels", backward=lambda value: bool(value))


@ui.page("/yt/extraction/progress")
def extraction_progress_page() -> None:
    page_shell("yt")
    with content():
        back_button("/yt/extraction/confirm")
        page_title("Extraction Progress", "Mock pipeline view for the future channel extraction job.")
        ProgressPipeline(EXTRACTION_STAGES, "Extraction", "About 5 min")


@ui.page("/yt/processed-news")
def processed_news_page() -> None:
    page_shell("yt")
    news_items = load_processed_news()
    selected_index = {"value": 0}
    STATE["selected_news"] = news_items[0]

    with content():
        back_button("/yt")
        page_title("Processed News", "Select one story to use as the basis for a generated video.")
        cards = ui.column().classes("w-full gap-3")

        def render_cards() -> None:
            cards.clear()
            with cards:
                for index, item in enumerate(news_items):
                    active = index == selected_index["value"]
                    with ui.card().classes(
                        f"surface w-full cursor-pointer p-5 border-2 {'border-primary' if active else 'border-transparent'}"
                    ).on("click", lambda _, i=index: select_item(i)):
                        with ui.row().classes("w-full items-start justify-between gap-4"):
                            with ui.column().classes("gap-2 flex-1"):
                                ui.label(item.headline).classes("text-lg font-semibold")
                                if item.summary:
                                    ui.label(item.summary).classes("muted text-sm")
                            with ui.row().classes("gap-2"):
                                ui.badge(item.category).props("outline color=primary")
                                ui.badge(f"{item.confidence:.0%} confidence").props("outline color=green")
                                ui.badge(f"{item.source_count} sources").props("outline color=grey")

        def select_item(index: int) -> None:
            selected_index["value"] = index
            STATE["selected_news"] = news_items[index]
            render_cards()

        render_cards()
        with ui.row().classes("w-full justify-end"):
            ui.button(
                "Continue To Video Configuration",
                icon="arrow_forward",
                on_click=lambda: ui.navigate.to("/video/config"),
            ).props("color=primary")


def video_options_panel() -> None:
    with ui.card().classes("surface w-full p-6 gap-5"):
        ui.label("Video Configuration").classes("text-xl font-semibold")
        with ui.grid(columns=2).classes("w-full gap-4"):
            ui.select(["Short", "Full"], value="Short", label="Video Type").props("outlined")
            ui.select(["30 seconds", "60 seconds", "3 minutes", "5 minutes"], value="60 seconds", label="Duration").props(
                "outlined"
            )
            ui.select(["Neutral Anchor", "Energetic Host", "Calm Explainer"], value="Neutral Anchor", label="Voice").props(
                "outlined"
            )
            ui.select(["Objective", "Conversational", "Urgent", "Analytical"], value="Conversational", label="Tone").props(
                "outlined"
            )
            ui.select(["9:16", "16:9", "1:1"], value="9:16", label="Aspect Ratio").props("outlined")
            ui.select(["Subtle", "None", "Cinematic", "News Bed"], value="Subtle", label="Background Music").props(
                "outlined"
            )
        ui.switch("Subtitles", value=True)


def topic_selector_panel() -> None:
    news_items = load_processed_news()
    current = STATE.get("selected_news") or news_items[0]
    STATE["selected_news"] = current
    labels = [item.headline for item in news_items]
    if isinstance(current, NewsItem) and current.headline not in labels:
        news_items = [current, *news_items]
        labels = [item.headline for item in news_items]
    current_label = current.headline if isinstance(current, NewsItem) else labels[0]

    with ui.card().classes("surface w-full p-6 gap-3"):
        ui.label("Topic").classes("text-xl font-semibold")
        ui.select(labels, value=current_label, label="Processed topic").props("outlined").classes(
            "w-full"
        ).on_value_change(
            lambda event: STATE.update(
                {
                    "selected_news": next(
                        item for item in news_items if item.headline == event.value
                    )
                }
            )
        )
        ui.label("Best available processed topic is selected by default.").classes("muted text-sm")


@ui.page("/video/config")
def video_configuration_page() -> None:
    page_shell()
    with content():
        back_button("/yt/processed-news")
        page_title("Video Configuration", "Defaults are optimized so most runs can continue immediately.")
        topic_selector_panel()
        video_options_panel()
        with ui.row().classes("w-full justify-between"):
            ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.back()).props(
                "outline color=grey-8"
            )
            ui.button(
                "Generate Video",
                icon="movie",
                on_click=lambda: ui.navigate.to("/video/progress"),
            ).props("color=primary")


@ui.page("/video/progress")
def video_progress_page() -> None:
    page_shell()
    with content():
        back_button("/video/config")
        page_title("Video Generation Progress", "Mock progress view for the future rendering pipeline.")
        ProgressPipeline(VIDEO_STAGES, "Video generation", "About 8 min")


@ui.page("/custom-topic")
def custom_topic_page() -> None:
    page_shell("custom")

    with content():
        back_button("/")
        page_title("Custom Topic", "Describe the story you want to turn into a video.")
        topic = ui.input("Topic").props("outlined").classes("w-full")
        description = ui.textarea("Small Description").props("outlined").classes("w-full")
        category = ui.select(
            ["Politics", "Business", "Technology", "Sports", "Entertainment", "World", "General"],
            value="General",
            label="Category",
        ).props("outlined").classes("w-full")
        analysis = ui.column().classes("w-full")

        def analyze_topic() -> None:
            clean_topic = (topic.value or "Untitled topic").strip()
            clean_category = category.value or "General"
            STATE["custom_topic"] = {
                "topic": clean_topic,
                "description": description.value or "",
                "category": clean_category,
            }
            STATE["selected_news"] = NewsItem(
                headline=clean_topic,
                category=clean_category,
                confidence=0.87,
                source_count=1,
                summary=description.value or "Custom topic provided by the user.",
            )
            analysis.clear()
            with analysis:
                with ui.card().classes("surface w-full p-6 gap-4"):
                    ui.label("Topic Analysis").classes("text-xl font-semibold")
                    with ui.row().classes("w-full gap-4"):
                        stat_card("Detected Topic", clean_topic, "radar")
                        stat_card("Detected Category", clean_category, "category")
                        stat_card("Confidence Score", "87%", "verified")
                    ui.label("Possible Angle").classes("font-semibold")
                    ui.label(
                        f"Frame this as a clear explainer that gives viewers the latest context, why {clean_topic.lower()} matters, and what may happen next."
                    ).classes("muted leading-6")
                    ui.label("Do you want to generate a video on this topic?").classes(
                        "text-lg font-semibold"
                    )
                    with ui.row().classes("w-full justify-between"):
                        ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.to("/")).props(
                            "outline color=grey-8"
                        )
                        ui.button(
                            "Continue To Video Configuration",
                            icon="arrow_forward",
                            on_click=lambda: ui.navigate.to("/video/config"),
                        ).props("color=primary")

        with ui.row().classes("w-full justify-end"):
            ui.button("Analyze Topic", icon="auto_awesome", on_click=analyze_topic).props(
                "color=primary"
            )
        analysis


app.add_static_files("/static", PROJECT_ROOT)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Automated News Creator", reload=False)
