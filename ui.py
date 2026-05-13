import gradio as gr
import subprocess


def generate_only():
    try:
        subprocess.run(
            ["python", "main.py"],
            check=True
        )

        return "Generated video successfully."

    except subprocess.CalledProcessError as e:
        return f"Error:\n{e}"


def upload_only():
    try:
        subprocess.run(
            ["python", "upload_video.py"],
            check=True
        )

        return "Uploaded existing video."

    except subprocess.CalledProcessError as e:
        return f"Error:\n{e}"


def generate_and_upload():
    try:
        subprocess.run(
            [
                "python",
                "main.py",
                "--upload",
                "--privacy",
                "public"
            ],
            check=True
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
        outputs=output
    )

    both_btn.click(
        fn=generate_and_upload,
        outputs=output
    )

app.launch()