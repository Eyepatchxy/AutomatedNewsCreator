from nicegui import ui
import time
from gui.state.models import Stage
from gui.utils.helper import stage_classes, stage_icon
from typing import Any
from gui.utils.CancelException import PipelineCancelled

class ProgressPipeline:
    def __init__(
        self,
        stages: list[Stage],
    ) -> None:
        self.current_stage = None
        self.stages = [
            Stage(stage.sr_no, stage.name, stage.weight)
            for stage in stages
        ]
        self.started_at = time.monotonic()
        self.completed = False
        self.cancel_requested = False

        for stage in self.stages:
            stage.progress = 0.00
            stage.status = "pending"

        with ui.card().classes("surface p-6 w-full gap-5"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.button(
                    "Cancel",
                    icon="cancel",
                    on_click=self.cancel,
                ).props("color=negative")

                ui.label("Pipeline").classes("text-xl font-semibold")
                self.elapsed_label = ui.label("Elapsed: 00:00").classes("muted text-right")

                self.elapsed_timer = ui.timer(
                    1.0,
                    self._update_elapsed,
                )

            with ui.linear_progress(value=0, show_value=False, size="20px").classes("w-full") as progress:
                self.progress = progress
                self.progress_value_label = ui.label(self._format_progress(0)).classes(
                    "absolute-center text-white"
                ).style("font-size: 0.875rem")
            with ui.row().classes("w-full gap-3"):
                self.stage_cards: list[dict[str, Any]] = [
                    self._make_stage_card(stage)
                    for stage in self.stages
                ]

            with ui.row().classes("w-full gap-4"):
                with ui.card().classes("surface p-4 flex-1"):
                    ui.label("Logs").classes("font-semibold")
                    self.log = ui.log(max_lines=80).classes(
                        "log-box h-64 w-full rounded bg-slate-950 p-3 text-sm text-slate-100"
                    )
                # with ui.card().classes("surface p-4 w-64"):
                #     ui.label("ETA").classes("font-semibold")
                #     self.eta_label = ui.label(eta).classes("text-2xl font-bold")
                #     ui.label("Updates as the job moves through the pipeline.").classes(
                #         "muted text-sm leading-5"
                #     )

        self.log.push("Pipeline Queued")

    def _find_stage(self, num: int | None) -> Stage | None:
        return next(
            (
                stage
                for stage in self.stages
                if stage.sr_no == num
            ),
            None,
        )

    def _make_stage_card(self, stage: Stage) -> dict[str, Any]:
        with ui.card().classes(f"stage-card flex-1 border p-4 {stage_classes(stage.status)}") as card:
            icon = ui.icon(stage_icon(stage.status)).classes("stage-icon text-2xl")
            ui.label(stage.name).classes("font-semibold leading-5")
            label = ui.label(stage.status.title()).classes("stage-status text-xs uppercase tracking-wide")

            stage.card = card
            stage.icon = icon
            stage.label = label
        return {"card": card, "icon": icon, "label": label}
    
    @staticmethod
    def _format_progress(value: float) -> str:
        percent = max(0.00, min(value, 1.00)) * 100
        return f"{percent:.2f}".rstrip("0").rstrip(".") + "%"

    def _set_progress(self, value: float) -> None:
        self.progress.value = value
        self.progress_value_label.text = self._format_progress(value)

    def _refresh_stage_ui(self, stage: Stage):
        stage.card.classes(
            replace=f"stage-card flex-1 border p-4 {stage_classes(stage.status)}"
        )
        stage.icon.name = stage_icon(stage.status)
        stage.label.text = stage.status.title()
        self._set_progress(self.calculate_progress())

    def start_stage(self, num: int):
        self.check_cancelled()
        stage = self._find_stage(num)
        if stage is None:
            raise ValueError(f"Unknown pipeline stage: {num}")

        self.current_stage = stage.sr_no
        stage.progress = 0.00
        stage.status = "running"
        self._refresh_stage_ui(stage)
        self.log.push(
            f"{stage.name}: started"
        )


    def update_stage_progress(self, num: int, progress: float):
        self.check_cancelled()
        stage = self._find_stage(num)
        if stage is None:
            raise ValueError(f"Unknown pipeline stage: {num}")

        print(
            f"Updating stage {num}: {progress}"
        )
        stage.progress = max(0.00, min(progress, 1.00))
        self._refresh_stage_ui(stage)

    def complete_stage(self, num: int):
        self.check_cancelled()

        stage = self._find_stage(num)
        if stage is None:
            raise ValueError(f"Unknown pipeline stage: {num}")

        self.current_stage = None
        stage.progress = 1.00
        stage.status = "completed"
        self._refresh_stage_ui(stage)
        self.log.push(
            f"{stage.name}: completed"
        )

    def calculate_progress(self):

        return sum(
            stage.progress * stage.weight
            for stage in self.stages
        )
    
    def complete_pipeline(self) -> None:
        incomplete = [
            stage.name
            for stage in self.stages
            if stage.progress < 1.0
        ]

        if incomplete:
            raise RuntimeError(
                f"Cannot complete pipeline. Incomplete stages: {', '.join(incomplete)}"
            )

        self.completed = True
        self._set_progress(1.0)

        self.log.push("Process completed")
        self.elapsed_timer.cancel()

    def fail_stage(self, num: int | None, reason: str) -> None:
        if self.completed:
            return

        stage = self._find_stage(num)
        if stage is None:
            stage = self._find_stage(self.current_stage)

        if stage is None:
            self.log.push(f"Pipeline failed - {reason}")
        else:
            stage.status = "failed"
            self._refresh_stage_ui(stage)
            self.log.push(
                f"{stage.name}: failed - {reason}"
            )

        self.completed = True
        self.elapsed_timer.cancel()

    def fail(self, reason: str) -> None:
        self.fail_stage(self.current_stage, reason)

    def finish_success(self, message: str = "Process completed") -> None:
        for stage in self.stages:
            if stage.status != "completed":
                stage.progress = 1.00
                stage.status = "completed"
                self._refresh_stage_ui(stage)

        self.complete_pipeline()
        self.log.push(message)
    
    def _update_elapsed(self):
        elapsed = int(
            time.monotonic()
            - self.started_at
        )

        self.elapsed_label.text = (
            f"Elapsed: "
            f"{elapsed // 60:02d}:"
            f"{elapsed % 60:02d}"
        )

    def cancel(self):
        if self.completed:
            return

        self.cancel_requested = True

        self.log.push(
            "Cancellation requested..."
        )

    def check_cancelled(self):
        if self.cancel_requested:

            self.log.push(
                "Pipeline cancelled"
            )

            raise PipelineCancelled()
