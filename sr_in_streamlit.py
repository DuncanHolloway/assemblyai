import streamlit as st
import websockets
import asyncio
import base64
import re
import dictionary
import json
from urllib.parse import urlencode
from configure import auth_key
import pyaudio


dict = {
"Zero":"0",
"One":"1",
"Two":"2",
"Three":"3",
"Four":"4",
"Five":"5",
"Six":"6",
"Seven":"7",
"Eight":"8",
"Nine":"9",
"Niner":"9",
"zero":"0",
"one":"1",
"two":"2",
"three":"3",
"four":"4",
"five":"5",
"six":"6",
"seven":"7",
"eight":"8",
"nine":"9",
"niner":"9",
"Alpha":"A",
"Alba":"A",
"Bravo":"B",
"Barbow":"B",
"barbo":"B",
"Charlie":"C",
"Delta":"D",
"Echo":"E",
"Foxtrot":"F",
"Box trot":"F",
"box trop":"F",
"Box Drop":"F",
"Box dop":"F",
"Box shot":"F",
"Box chart":"F",
"Box cut":"F",
"Box, drop":"F",
"Golf":"G",
"Gulf":"G",
"Hotel":"H",
"India":"I",
"Juliett":"J",
"Juliet":"J",
"Kilo":"K",
"Lima":"L",
"Mike":"M",
"November":"N",
"Oscar":"O",
"Papa":"P",
"Pappa":"P",
"Quebec":"Q",
"Romeo":"R",
"Sierra":"S",
"Tango":"T",
"trolley":"T",
"Uniform":"U",
"Victor":"V",
"Whiskey":"W",
"X-ray":"X",
"X Ray":"X",
"Yankee":"Y",
"Zulu":"Z",
"alpha":"A",
"bravo":"B",
"barbow":"B",
"charlie":"C",
"delta":"D",
"echo":"E",
"foxtrot":"F",
"golf":"G",
"gulf":"G",
"hotel":"H",
"india":"I",
"juliett":"J",
"juliet":"J",
"kilo":"K",
"lima":"L",
"mike":"M",
"november":"N",
"oscar":"O",
"papa":"P",
"pappa":"P",
"quebec":"Q",
"romeo":"R",
"sierra":"S",
"tango":"T",
"trolley":"T",
"uniform":"U",
"victor":"V",
"whiskey":"W",
"x-ray":"X",
"yankee":"Y",
"zulu":"Z",
"Q and H":"QNH",
"Q, and H":"QNH",
"Qnh":"QNH",
"health tree":"Elstree",
"Tree":"Elstree",
"Lstree":"Elstree"
}

if 'text' not in st.session_state:
    st.session_state['text'] = 'Listening...'
    st.session_state['run'] = False

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

word_boost = ["Elstree", "Duxford", "Cessna", "152", "feet", "Farnborough","Luton", "Radar", 'QNH', "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"]
params = {"sample_rate": RATE, "word_boost": json.dumps(word_boost), "boost_param": "high"}

# starts recording
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)


def start_listening():
    st.session_state['run'] = True


def stop_listening():
    st.session_state['run'] = False


st.title('Real-time Radiotelephony transcription')

start, stop = st.columns(2)
start.button('Start listening', on_click=start_listening)

stop.button('Stop listening', on_click=stop_listening)

URL = f"wss://api.assemblyai.com/v2/realtime/ws?{urlencode(params)}"


async def send_receive():
    print(f'Connecting websocket to url ${URL}')

    async with websockets.connect(
            URL,
            extra_headers=(("Authorization", auth_key),),
            ping_interval=5,
            ping_timeout=20
   ) as _ws:

        r = await asyncio.sleep(0.3)
        print("Receiving SessionBegins ...")

        session_begins = await _ws.recv()
        print(session_begins)
        print("Sending messages ...")

        async def send():
            while st.session_state['run']:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data": str(data)})
                    r = await _ws.send(json_data)

                except websockets.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break

                except Exception as e:
                    print(e)
                    assert False, "Not a websocket 4008 error"

                r = await asyncio.sleep(0.01)

        async def receive():
            while st.session_state['run']:
                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)['text']
                    result = result
                    for key, value in dict.items():
                        result = (re.sub( key, value, result ))
                    print(result)

                    if json.loads(result_str)['message_type'] == 'FinalTranscript':
                        print(result)
                        st.session_state['text'] = result
                        st.markdown(st.session_state['text'])

                except websockets.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break

                except Exception as e:
                    print(e)
                    assert False, "Not a websocket 4008 error"

        send_result, receive_result = await asyncio.gather(send(), receive())


asyncio.run(send_receive())
