from tasks.ExtractionTools.channelwise_news_extractor import create_youtube_client, get_channel_id_from_handle



youtube = create_youtube_client()
handle = "@TheLallantop"
channel_id = get_channel_id_from_handle(youtube, handle)
print(f"Channel ID for {handle}: {channel_id}")