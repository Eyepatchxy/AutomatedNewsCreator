from importlib import import_module


ROUTES = [
    {
        "label": "Home",
        "path": "/",
        "module": "gui.pages.home_page",
        "icon": "home",
        "group": "main",
    },

    {
        "label": "Channel-wise Workflow",
        "path": "/yt",
        "module": "gui.pages.channelwise.yt_workflow_page",
        "icon": "smart_display",
        "group": "channelwise",
    },

    {
        "label": "Channel Selection",
        "path": "/yt/channels",
        "module": "gui.pages.channelwise.extraction.channel_selection_page",
        "icon": "subscriptions",
        "group": "channelwise",
    },

    {
        "label": "Add Channel",
        "path": "/yt/channels/add",
        "module": "gui.pages.channelwise.extraction.add_channel_page",
        "icon": "add_circle",
        "group": "channelwise",
    },

    {
        "label": "Processed News",
        "path": "/yt/processed-news",
        "module": "gui.pages.channelwise.extraction.processed_news_page",
        "icon": "feed",
        "group": "channelwise",
    },

    {
        "label": "Upload Generated Videos",
        "path": "/yt/upload-videos",
        "module": "gui.pages.channelwise.upload_videos_page",
        "icon": "cloud_upload",
        "group": "channelwise",
    },

    {
        "label": "Extraction Confirmation",
        "path": "/yt/extraction/confirm",
        "module": "gui.pages.channelwise.extraction.extraction_confirmation_page",
        "icon": "check_circle",
        "group": "channelwise",
    },

    {
        "label": "Extraction Progress",
        "path": "/yt/extraction/progress",
        "module": "gui.pages.channelwise.extraction.extraction_progress_page",
        "icon": "sync",
        "group": "channelwise",
    },

    {
        "label": "Topic-wise Workflow",
        "path": "/custom-topic",
        "module": "gui.pages.topicwise.custom_topic_page",
        "icon": "edit_note",
        "group": "topicwise",
    },

    {
        "label": "Video Configuration",
        "path": "/video/config",
        "module": "gui.pages.video_generation.video_configuration_page",
        "icon": "movie",
        "group": "video",
    },

    {
        "label": "Video Generation Progress",
        "path": "/video/progress",
        "module": "gui.pages.video_generation.video_progress_page",
        "icon": "video_settings",
        "group": "video",
    },
]


def register_routes() -> None:
    for route in ROUTES:
        import_module(route["module"])


def get_route(path: str) -> dict | None:
    return next(
        (
            route
            for route in ROUTES
            if route["path"] == path
        ),
        None,
    )


def get_current_route() -> dict | None:
    from nicegui import ui

    current_path = ui.context.client.path

    return get_route(current_path)

def get_path(label: str) -> str:
    route = next(
        (
            route
            for route in ROUTES
            if route["label"] == label
        ),
        None,
    )

    if route is None:
        raise ValueError(f"Route not found: {label}")

    return route["path"]
