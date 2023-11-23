from clients.RealTimeClient import RealTimeClient
from silero_vad import silero_vad
from diart.utils import decode_audio
import logging

class RealTimeDialogClient(RealTimeClient):

    def __init__(self, sid, socket, config):
        super().__init__(sid=sid, socket=socket, config=config)
        self.last_chunk_voiced = False
        self.time_total_silence = 0

    def handle_chunk(self, chunk):
        speech_present, speech_confidence = silero_vad(decode_audio(chunk))
        if speech_present:
            self.audio_chunks.put(chunk)
            self.last_chunk_voiced = True
            if self.time_total_silence > 0:
                self.time_total_silence = 0

        else:
            if self.last_chunk_voiced and self.time_total_silence == 0:
                self.last_chunk_voiced = False
                self.time_total_silence += 1
            elif self.time_total_silence > 0:
                self.time_total_silence += 1
                if self.time_total_silence > 2:
                    logging.info("It's been more than ~1.5 second of silence")
        logging.debug("Chunk added")
