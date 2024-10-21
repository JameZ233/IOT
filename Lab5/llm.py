import asyncio
import fastapi_poe as fp


POE_API_KEY = '2-j_yibA8pbfozuVugcd8qTYAC-4Iu4XHNEOtuEV5qE'

INITIAL_PROMPT = "You are a voice assistant for a smartwatch.\
      Interpret the user's command and respond with a JSON object (no markdown) that calls specific functions for the smartwatch.\
        Available functions:\n \
    Set time: {name: \"set_time\", args: [year, month, day, weekday, hour, minute, second, microsecond]}\n \
    Turn on screen: {name: \"screen_on\", args: []}\n \
    Turn off screen: {name: \"screen_off\", args: []}\n \
    Display time: {name: \"display_time\", args: []}\n \
    Set alarm: {name: \"set_alarm\", args: [hour, minute]}\n \
    Display location: {name: \"display_location\", args: []}\n \
    Display weather: {name: \"display_weather\", args: []}\n \
    You should understand the user's request or question, try your best to parse the request into one of the functions \
    and return in the corresponding json format.\n \
    If the request does not fit into any of the above functions, answer the question based on your own knowledge, \
    and use the display_text function to display your response. \
    (return this json: {name: \"display_text\", args: [text]}).\n \
    Since the smartwatch has a tiny screen, your response should be within 48 Characters.\n \
    The user's request is as following:\n"

async def get_llm_response(prompt):
    message = fp.ProtocolMessage(role="user", content=INITIAL_PROMPT + prompt)
    full_response = ""
    async for partial in fp.get_bot_response(messages=[message], bot_name='GPT-4o-Mini',api_key=POE_API_KEY):
        full_response += partial.text
    return full_response

def interpret_command(prompt):
    # Prompt
    return asyncio.run(get_llm_response(prompt))

# def process_input(audio):
#     transcription = whisper_model.transcribe(audio)['text']
    
if __name__ == "__main__":
    prompt = INITIAL_PROMPT + ("Enter a prompt:")
    print(asyncio.run(get_llm_response(prompt)))