import gradio as gr

def hello_world(name):
    return f"Hallo, {name}! Hier sind die Infos die Sie suchen: "

demo = gr.Interface(
    fn=hello_world,
    inputs=gr.Textbox(label="Suchbegriff", lines=10),
    outputs=gr.Textbox(label="Infos", lines=30),
    title="Uni Mannheim - IT-Anleitungen",
    description="Hier können Sie die IT-Anleitungen der Universität Mannheim durchsuchen. Bitte geben Sie einen Suchbegriff ein:",
)

demo.launch()
