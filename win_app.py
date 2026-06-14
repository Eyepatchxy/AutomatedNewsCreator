import multiprocessing
from multiprocessing import freeze_support

from nicegui import ui

from gui.pages.home_page import home_page
from gui.pages.video_generation.video_progress_page import video_progress_page

if __name__ in {"__main__", "__mp_main__"}:

    freeze_support()
    multiprocessing.set_start_method("spawn", force=True)
    ui.run(
        title="Automated News Generator",
        native=True,
        reload=False
    )