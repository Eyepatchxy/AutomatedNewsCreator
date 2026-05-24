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