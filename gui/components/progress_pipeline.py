from nicegui import ui
import time
from gui.utils.helper import stage_classes, stage_icon
from typing import Any

class ProgressPipeline:
    def __init__(
        self,
        stages: list[str],
        log_prefix: str,
        eta: str,
        auto_tick: bool = True,
        tick_seconds: float = 4.0,
    ) -> None:
        self.stages = stages
        self.log_prefix = log_prefix
        self.current_index = 0
        self.started_at = time.monotonic()
        self.completed = False

        with ui.card().classes("surface p-6 w-full gap-5"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Pipeline").classes("text-xl font-semibold")
                self.elapsed_label = ui.label("Elapsed: 00:00").classes("muted")

            self.progress = ui.linear_progress(value=0).classes("w-full")
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
                    ui.label("Updates as the job moves through the pipeline.").classes(
                        "muted text-sm leading-5"
                    )

        self.log.push(f"{self.log_prefix}: queued")
        self.timer = ui.timer(tick_seconds, self.tick) if auto_tick else None

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

    def tick(self) -> None:
        elapsed = int(time.monotonic() - self.started_at)
        self.elapsed_label.text = f"Elapsed: {elapsed // 60:02d}:{elapsed % 60:02d}"

        if self.completed:
            return

        if self.current_index >= len(self.stages) - 1:
            self.progress.value = max(
                self.progress.value,
                (len(self.stages) - 1) / len(self.stages),
            )
            self.log.push(f"{self.log_prefix}: {self.stages[self.current_index]} still running")
            return

        self._set_stage(self.current_index, "completed")
        self.log.push(f"{self.log_prefix}: {self.stages[self.current_index]} completed")
        self.current_index += 1
        self.progress.value = self.current_index / len(self.stages)

        self._set_stage(self.current_index, "running")
        self.log.push(f"{self.log_prefix}: {self.stages[self.current_index]} running")

    def finish_success(self, message: str = "Complete") -> None:
        if self.completed:
            return

        for index in range(self.current_index, len(self.stages)):
            self._set_stage(index, "completed")

        self.current_index = len(self.stages)
        self.progress.value = 1
        self.completed = True
        self.log.push(f"{self.log_prefix}: {message}")
        self.eta_label.text = "Complete"
        if self.timer:
            self.timer.cancel()

    def fail(self, message: str) -> None:
        if self.completed:
            return

        self._set_stage(min(self.current_index, len(self.stages) - 1), "failed")
        self.completed = True
        self.log.push(f"{self.log_prefix}: failed - {message}")
        self.eta_label.text = "Failed"
        if self.timer:
            self.timer.cancel()
