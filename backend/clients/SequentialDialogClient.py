from clients.SequentialClient import SequentialClient
from silero_vad import silero_vad
from diart.utils import decode_audio
import logging
import time
import asyncio
from config import STEP, TEMP_FILE_PATH, REQUIRED_AUDIO_TYPE, ClientState

class SequentialDialogClient(SequentialClient):

    def __init__(self, sid, socket, config):
        super().__init__(sid=sid, socket=socket, config=config)
        self.last_chunk_voiced = False
        self.chunks_total_silence = 0
        self.tasks = set()
    
    def send_dialogStart_msg(self):
        task = asyncio.create_task(self.socket.emit("dialogProcessingStart"))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    def handle_chunk(self, chunk):
        speech_present, speech_confidence = silero_vad(decode_audio(chunk))
        if speech_present:
            self.audio_chunks.put(chunk)
            self.last_chunk_voiced = True
            if self.chunks_total_silence > 0:
                self.chunks_total_silence = 0
        else:
            if self.last_chunk_voiced and self.chunks_total_silence == 0:
                self.last_chunk_voiced = False
                self.chunks_total_silence += 1
            elif self.chunks_total_silence > 0:
                self.chunks_total_silence += 1
                if self.chunks_total_silence == 3:
                    logging.info("It's been more than ~1.5 second of silence")
                    self.send_dialogStart_msg()
                    self.start_dialog_transcription = True
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
