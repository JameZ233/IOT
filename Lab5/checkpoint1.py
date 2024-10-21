import gradio as gr
import whisper
import json
from llm import interpret_command
from client import send_command

#Load whisper model
whisper_model = whisper.load_model('tiny.en')

def process_input(audio):
    transcription = whisper_model.transcribe(audio)['text']
    llm_response = interpret_command(transcription)
    command = json.loads(llm_response)
    send_command(command)
    smartwatch_response = f'Placeholder for smartwatch response'
    return transcription, llm_response, smartwatch_response

ui = gr.Interface(
    inputs=[
        gr.Audio(sources=["microphone"],type='filepath',label='Voice Input'),
    ],
    fn = process_input,
    outputs=[
        gr.Textbox(label='Transcription/Input'),
        gr.Textbox(label='LLM Response'),
        gr.Textbox(label='Smartwatch Response')
    ],
    title='Voice Assistant',
    description='My capabilities: XXX',
    allow_flagging='never'
)


if __name__ == "__main__":
    # llm_response = interpret_command('set time')
    # command = json.loads(llm_response)
    # send_command(command)
    ui.launch(debug=False, share=True)