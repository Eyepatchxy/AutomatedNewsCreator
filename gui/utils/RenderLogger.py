from proglog import ProgressBarLogger
from gui.utils.CancelException import PipelineCancelled



class RenderLogger(ProgressBarLogger):

    def __init__(self, pipeline):
        super().__init__()
        self.pipeline = pipeline

    def callback(self, **changes):
        if self.pipeline.cancel_requested:
            raise PipelineCancelled()

        if "frame_index" not in self.bars:
            return


        bar = self.bars["frame_index"]

        current = bar.get("index", 0)
        total = bar.get("total", 0)

        progress = (current / total)
        progress = round(progress, 4) 

        if total:
            self.pipeline.update_stage_progress(8, progress)

        log_bool = current % 10
            
        if log_bool == 0:
            self.pipeline.log.push(
                f"{current} frames rendered out of {total}"
            )