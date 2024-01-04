// AudioPlayer.js
import React, { useEffect, useRef, useState } from 'react';

function createAudioUrl(binaryWavData) {
    if (binaryWavData.length === 0) {
        return URL.createObjectURL(new Blob([], { type: "audio/wav" }));
    }
    return URL.createObjectURL(new Blob([binaryWavData], { type: "audio/wav" }));
}

const AudioPlayer = ({ binaryWavData }) => {
  const audioContextRef = useRef(new (window.AudioContext || window.webkitAudioContext)());
  const sourceNodeRef = useRef(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    // Convert binary data to Blob and set the new audio URL
    if (binaryWavData) {
      const newAudioUrl = createAudioUrl(binaryWavData);
      setAudioUrl(newAudioUrl);
    }

    const audioContext = audioContextRef.current;

    if (!audioContext) {
      console.error('Web Audio API is not supported in this browser.');
      return;
    }

    // When new binary data is received, decode it and play the audio
    if (binaryWavData) {
      audioContext.decodeAudioData(binaryWavData, (buffer) => {
        if (sourceNodeRef.current) {
          sourceNodeRef.current.stop();
          sourceNodeRef.current.disconnect();
        }

        sourceNodeRef.current = audioContext.createBufferSource();
        sourceNodeRef.current.buffer = buffer;
        sourceNodeRef.current.connect(audioContext.destination);
        sourceNodeRef.current.onended = () => setIsPlaying(false);
        sourceNodeRef.current.start();
        setIsPlaying(true);
      });
    }

    // Cleanup the old audio URL when the component unmounts
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      if (sourceNodeRef.current) {
        sourceNodeRef.current.stop();
        sourceNodeRef.current.disconnect();
      }
    };
  }, [binaryWavData]); // Update the audio URL whenever binaryWavData changes

  return (
    <div>
      {audioUrl ? (
        <audio key={audioUrl} controls>
          <source src={audioUrl} type="audio/wav" />
          Your browser does not support the audio element.
        </audio>
      ) : (
        <p>Waiting for initial response</p>
      )}
    </div>
  );
};

export default AudioPlayer;