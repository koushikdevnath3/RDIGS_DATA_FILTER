import sounddevice as sd
import soundfile as sf
import openai
import os
import tempfile
import requests
from colorama import Fore, Style, init
import re
import io

init()

# Set API keys
openai.api_key = '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'
elevenlab_api_key = '3843f0821baf8cbb06e750460eef346f'

voice_id1 = 'MRTlgyi0P321rEoNUaQb'  # Replace with your actual voice ID

def chatgpt(api_key, conversation, user_input, temperature=0.7, frequency_penalty=0.0, presence_penalty=0.0):
    try:
        conversation.append({"role": "user", "content": user_input})
        messages_input = conversation.copy()
        
        # Define system message and prompt
        system_message = {
            "role": "system",
            "content": "Your Name is Rachel. You are working in RD Info Global Solutions, a B2B lead generation company. after intro tell the reason to call then go for conforming other information Don't ask this question - 'How can I assist you today?' You are making a call to confirm details and send a white paper. The white paper is about renewable energy and how they can save money on server maintenance cost. Explain in one line on mail. For that, you need to confirm name, company name, job title, email. Remember this is not a sales call; you just want to send a white paper on mail. Once all information is there, then take concern to send mail and also tell the user will receive a call from our partner. If the user has any questions, they can ask our representative. You have all the information you need, and you called to confirm the following details: 'Name is Koushik, job title is DevOps, company name is RD Info Global Solutions, email is koushik@rdigs.com'. Start the conversation by introducing yourself, ask if you are speaking to Koushik, and continue. Great! I'm calling from RD Info Global Solutions. I hope you're doing well today. And most importantly, try to make the response as small as possible (keep it to max 2 sentences at a time) and always break the questions into multiple questions "
        }
        
        prompt = [system_message]

        messages_input.insert(0, prompt[0])
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=messages_input
        )
        chat_response = completion['choices'][0]['message']['content']
        conversation.append({"role": "assistant", "content": chat_response})
        return chat_response
    except Exception as e:
        print(f"Error in chatgpt: {e}")
        return "I'm sorry, but something went wrong."

def text_to_speech_streaming(text, voice_id, api_key):
    try:
        if not text:
            print("Nothing to say.")
            return

        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream'

        headers = {
            'Accept': 'audio/wav',
            'xi-api-key': api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'text': text,
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {
                'stability': 0.6,
                'similarity_boost': 0.85
            }
        }

        response = requests.post(url, headers=headers, json=data, stream=True)
        
        if response.status_code == 200:
            # Stream the audio directly to sounddevice
            audio_stream = io.BytesIO(response.content)
            audio, _ = sf.read(audio_stream, dtype='int16')
            sd.play(audio, samplerate=44100)
            sd.wait()
        else:
            print('Error:', response.text)
    except Exception as e:
        print(f"Error in text_to_speech_streaming: {e}")

def print_colored(agent, text):
    try:
        agent_colors = {
            "Julie:": Fore.YELLOW,
        }
        color = agent_colors.get(agent, "")
        print(color + f"{agent}: {text}" + Style.RESET_ALL, end="")
    except Exception as e:
        print(f"Error in print_colored: {e}")

def record_and_transcribe(duration=8, fs=84100):
    try:
        print('Recording...')
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        print('Recording complete.')
        filename = 'myrecording.wav'
        sf.write(filename, myrecording, fs)
        with open(filename, "rb") as file:
            result = openai.Audio.transcribe("whisper-1", file)
        transcription = result['text']
        return transcription
    except Exception as e:
        print(f"Error in record_and_transcribe: {e}")
        return "I'm sorry, but I couldn't process your request."

def end_conversation():
    print("Goodbye! Have a great day.")
    # Additional clean-up or final actions can be added here
    exit()

conversation1 = []

while True:
    try:
        user_message = record_and_transcribe(duration=2)
        if user_message.strip():
            response = chatgpt(openai.api_key, conversation1, user_message)
            print_colored("Rachel:", f"{response}\n\n")
            user_message_without_generate_image = re.sub(r'(Response:|Narration:|Image: generate_image:.*|)', '', response).strip()
            text_to_speech_streaming(user_message_without_generate_image, voice_id1, elevenlab_api_key)
            
            # Check if the user wants to end the conversation
            if "have a good day" in response.lower():
                end_conversation()
        else:
            print("No user message recorded.")
    except KeyboardInterrupt:
        end_conversation()
    except Exception as e:
        print(f"Unexpected error: {e}")
