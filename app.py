import multiprocessing
from multiprocessing import freeze_support
from nicegui import ui

from gui.pages.home_page import home_page
from gui.pages.channelwise.extraction.add_channel_page import add_channel_page
from gui.pages.channelwise.extraction.channel_selection_page import channel_selection_page
from gui.pages.channelwise.extraction.extraction_confirmation_page import extraction_confirmation_page
from gui.pages.channelwise.extraction.extraction_progress_page import extraction_progress_page
from gui.pages.channelwise.extraction.processed_news_page import processed_news_page
from gui.pages.channelwise.upload_videos_page import upload_videos_page
from gui.pages.channelwise.yt_workflow_page import yt_workflow_page
from gui.pages.topicwise.custom_topic_page import custom_topic_page
from gui.pages.video_generation.video_configuration_page import video_configuration_page
from gui.pages.video_generation.video_progress_page import video_progress_page


def main():
    ui.run(native=True)


if __name__ in {"__main__", "__mp_main__"}:

    # only parent should configure multiprocessing
    if __name__ == "__main__":
        multiprocessing.set_start_method("fork")
        freeze_support()

    main()