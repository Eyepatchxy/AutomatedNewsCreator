from nicegui import ui

# Import pages so routes register
import gui.pages.home_page
import gui.pages.channelwise.yt_workflow_page
import gui.pages.channelwise.upload_videos_page
import gui.pages.channelwise.extraction.channel_selection_page
import gui.pages.channelwise.extraction.add_channel_page
import gui.pages.topicwise.custom_topic_page
import gui.pages.channelwise.extraction.extraction_confirmation_page
import gui.pages.channelwise.extraction.extraction_progress_page
import gui.pages.channelwise.extraction.processed_news_page
import gui.pages.video_generation.video_configuration_page
import gui.pages.video_generation.video_progress_page

ui.run(
    title="Automated News Creator",
    reload=False,
)
