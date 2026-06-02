from gui.state.models import Stage

EXTRACTION_STAGES = [
    Stage(1, "Videos Fetched", 0.20),
    Stage(2, "Metadata Extracted", 0.20),
    Stage(3, "Deduplication", 0.20),
    Stage(4, "Clustering", 0.20),
    Stage(5, "News Saved", 0.20),
]

VIDEO_STAGES = [
    Stage(1, "Topic Approval", 0.01),
    Stage(2, "Script Generation", 0.03),
    Stage(3, "Audio Generation", 0.04),
    Stage(4, "Chunks Generation", 0.02),
    Stage(5, "Timeline Generation", 0.02),
    Stage(6, "Thumbnail Generation", 0.03),
    Stage(7, "Visuals Generation", 0.05),
    Stage(8, "Video Encoding", 0.75),
    Stage(9, "Uploading", 0.05),
]