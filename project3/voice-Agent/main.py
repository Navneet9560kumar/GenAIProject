import asyncio
import base64
import json
import sys
from numpy import median
import websockets
import ssl
import os

from dotenv import load_dotenv

load_dotenv()

def sts_connect():
      api_key = os.getenv("DEEPGRAM_API_KEY")
      if not api_key:
            raise Exception("DEEPGRAM_API_KEY not set in environment variables")

            sts_ws = websockets.connect(
                  "wss://agent.deepgram.com/v1/agent/converse",
                  subprotocols=["token", api_key]
            )

            return sts_ws
      

def load_config():
      with open("config.json", "r") as f:
            return  json.load(f)
      

async def handle_barge_in(decode, twilio_ws,streamsid):
      if decode["type"]== "UserStartedSpeaking":
             clear_message = {
                   "event": "clear",
                   "streamSid": streamsid
             }
             await twilio_ws.send(json.dumps(clear_message))


async def handle_text_message(decode, twilio_ws, sts_ws, streamsid):
          await  handle_barge_in(decode, twilio_ws, streamsid)

          #todo handle functions calling
          



async def sts_sender(sts_ws,audio_queue):
       print("Starting STS sender")
       while True:
               chunk = await audio_queue.get()
               await sts_ws.send(chunk)


async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
       print("sts_recever started")
       streamsid = await streamsid_queue.get()

       async for message in sts_ws:
              if type(message) is str:
                     print(message)
                     decoded = json.loads(message)
                     await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
                     continue
              
              raw_mulaw = message

              media_message = {
                     "event": "media",
                     "media":{"payload": base64.b64encode(raw_mulaw).decode("ascii"),}
              }
        



async def twilio_receiver(twilio_ws,audio_queue, streamsid_queue):
       BUFFER_SIZE = 20* 160 
       inbuffer = bytearray(b"")


       async for message in twilio_ws:
              try:
                     data = json.loads(message)
                     event = data["event"]

                     if event == "start":
                            print("get our streamsid")
                            start = data["start"]
                            streamsid = start["streamSid"]
                            streamsid_queue.put_nowait(streamsid)
                     elif event == "connected":
                            continue
                     elif event == "media":
                            chunks = base64.b64decode(data["media"]["payload"])
                            # Fix: Use data["media"]["track"] instead of median["track"]
                            if data["media"]["track"] == "inbound":
                                   inbuffer.extend(chunks)
                                   while len(inbuffer) >= BUFFER_SIZE:
                                          chunk = inbuffer[:BUFFER_SIZE]
                                          audio_queue.put_nowait(chunk)
                                          inbuffer = inbuffer[BUFFER_SIZE:]
                     elif event == "stop":
                            break
              except Exception as e:
                     break


                              

async def twilio_handler(twilio_ws):
       audio_queue = asyncio.Queue()
       streamsid_queue = asyncio.Queue()

       async with sts_connect() as sts_ws:
               config_message = load_config()
               await sts_ws.send(json.dumps(config_message))


               await asyncio.wait(
                      [
                      asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                      asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
                      asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue)),
               ])


               await twilio_ws.close()

async def main():
       await websockets.serve(twilio_handler, "localhost", 5000)
       print("Server started on ws://localhost:5000")
       await asyncio.Future()  # Run forever    


if __name__ == "__main__":
       asyncio.run(main())