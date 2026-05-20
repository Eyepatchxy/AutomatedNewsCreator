import gradio as gr
import subprocess
import sys

from tasks.paths import PROJECT_ROOT
from tasks.yt_posting import list_unuploaded_videos


def generate_only():
    try:
        subprocess.run(
            [sys.executable, "main.py"],
            check=True,
            cwd=PROJECT_ROOT,
        )

        return "Generated video successfully."

    except subprocess.CalledProcessError as e:
        return f"Error:\n{e}"


def upload_only(file_name=None):
    choices = list_unuploaded_videos()
    file_name = (file_name or "").strip() if file_name else ""
    if not file_name:
        selected = choices[0] if choices else None
        message = (
            "Select an unuploaded video, then click Upload Only again."
            if choices
            else "No unuploaded videos found."
        )
        return message, gr.update(
            choices=choices,
            value=selected,
            visible=True,
        )

    try:
        subprocess.run(
            [sys.executable, "-m", "tasks.yt_posting", file_name],
            check=True,
            cwd=PROJECT_ROOT,
        )

        updated_choices = list_unuploaded_videos()
        return "Uploaded existing video.", gr.update(
            choices=updated_choices,
            value=updated_choices[0] if updated_choices else None,
            visible=True,
        )

    except subprocess.CalledProcessError as e:
        return f"Error:\n{e}", gr.update(
            choices=choices,
            value=file_name if file_name in choices else None,
            visible=True,
        )


def generate_and_upload():
    try:
        subprocess.run(
            [
                sys.executable,
                "main.py",
                "--upload",
                "--privacy",
                "public"
            ],
            check=True,
            cwd=PROJECT_ROOT,
        )

        return "Generated and uploaded video."

    except subprocess.CalledProcessError as e:
        return f"Error:\n{e}"


with gr.Blocks(theme=gr.themes.Soft()) as app:

    gr.Markdown(
        """
        # Automated News Creator
        Generate news videos and upload them to YouTube.
        """
    )

    output = gr.Textbox(
        label="Status",
        interactive=False
    )

    upload_file_name = gr.Dropdown(
        label="Unuploaded videos",
        choices=[],
        visible=False,
        interactive=True,
    )

    with gr.Row():

        generate_btn = gr.Button("Generate Only")
        upload_btn = gr.Button("Upload Only")
        both_btn = gr.Button("Generate & Upload")

    generate_btn.click(
        fn=generate_only,
        outputs=output
    )

    upload_btn.click(
        fn=upload_only,
        inputs=upload_file_name,
        outputs=[output, upload_file_name]
    )

    both_btn.click(
        fn=generate_and_upload,
        outputs=output
    )

app.launch()
