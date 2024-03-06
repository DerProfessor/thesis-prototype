from clients.SequentialClient import SequentialClient
from silero_vad import silero_vad
from diart.utils import decode_audio
import logging
import time
import asyncio
from config import STEP, TEMP_FILE_PATH, REQUIRED_AUDIO_TYPE, ClientState, LANGCHAIN_CONFIG, COQUI_ADDRESS
import requests
import soundfile as sf
import numpy as np

from langserve.client import RemoteRunnable
from httpx import ConnectError

class SequentialDialogClient(SequentialClient):

    def __init__(self, sid, socket, config):
        super().__init__(sid=sid, socket=socket, config=config)
        self.last_chunk_voiced = False
        self.chunks_total_silence = 0
        self.tasks = set()
        self.last_chunk = None
        self.langchain_client = RemoteRunnable(LANGCHAIN_CONFIG["address"])
        self.session_id = LANGCHAIN_CONFIG["session_id"]
    
    def call_dialog_assistant(self):
        # TODO: Handle multiple speakers more gracefully
        if len(self.current_transcription) > 0:
            text = self.current_transcription[0]["text"]
            try:
                result = self.langchain_client.invoke(input=text,
                                                    config={"configurable": {"session_id": self.session_id}}
                                                    )
                return result
            except ConnectError:
                logging.error("Could not connect to langchain")
                return "Tut mir leid, im Moment erfahre ich leider technische Probleme."
        else:
            logging.warning("No transcription available to send to dialog assistant")
            return "Tut mir leid, das habe nicht verstanden."

    def call_speak(self, response):
        #TODO: Handle multiple answers more gracefully
        response_json = {"text": response}
        if len(response) > 0:
            response = requests.post(
                COQUI_ADDRESS,
                json=response_json,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                asyncio.run(self.socket.emit("dialogResponseAvailable", response.content))
                logging.info("Response (audio) sent to client")
        else:
            logging.warning("Something went wrong during dialog processing")
    
    def send_dialog_data(self, response):
        if len(response) > 0:
            asyncio.run(self.socket.emit("dialogDataAvailable", response))
            logging.info("Dialog data sent")
        else:
            logging.warning("Something went wrong during dialog processing")

    def handle_dialogStart(self):
        asyncio.run(self.socket.emit("dialogProcessingStart"))
        response = self.call_dialog_assistant()
        self.send_dialog_data(response)
        self.call_speak(response)
        asyncio.run(self.socket.emit("dialogProcessingEnd"))

    def handle_chunk(self, chunk):
        speech_present, speech_confidence = silero_vad(decode_audio(chunk))
        if speech_present:
            if self.chunks_total_silence > 0:
                # Add previous chunk to better understand beginning of speech
                self.chunks_total_silence = 0
                self.audio_chunks.put(self.last_chunk)
            self.audio_chunks.put(chunk)
            self.last_chunk_voiced = True
        else:
            if self.last_chunk_voiced and self.chunks_total_silence == 0:
                self.last_chunk_voiced = False
                self.chunks_total_silence += 1
            elif self.chunks_total_silence > 0:
                self.chunks_total_silence += 1
                if self.chunks_total_silence == 3:
                    logging.info("It's been more than ~1.5 second of silence")
                    self.start_dialog_transcription = True
        self.last_chunk = chunk
        logging.debug("Chunk added")

    
    def stream_sequential_transcription(self):
        logging.info("Sequential transcription thread started")
        buffer = None
        chunk_counter = 0
        batch_size = self.transcription_timeout // STEP
        assert batch_size > 0, "batch size must be above 0"

        while True:
            if self.state == ClientState.DISCONNECTED:
                logging.info("Client disconnected, ending transcription...")
                break
            if not self.state == ClientState.ENDING_STREAM:
                if self.start_dialog_transcription:
                    buffer_float32 = self.convert_buffer_to_float32(buffer)
                    self.transcribe_buffer(buffer_float32)
                    chunk_counter = 0
                    self.start_dialog_transcription = False
                    # Is resetting the buffer a good idea?
                    buffer = None

                    self.handle_dialogStart()

                if not self.audio_chunks.empty():
                    current_chunk = self.audio_chunks.get()
                    buffer = self.modify_buffer(current_chunk, buffer)
                    chunk_counter += 1
            else:
                logging.info("Client is ending stream, preparing for a final transcription...")
                while not self.audio_chunks.empty():
                    current_chunk = self.audio_chunks.get()
                    buffer = self.modify_buffer(current_chunk, buffer)
                    chunk_counter += 1
                if chunk_counter > 0:
                    buffer_float32 = self.convert_buffer_to_float32(buffer)
                    self.transcribe_buffer(buffer_float32)
                break
