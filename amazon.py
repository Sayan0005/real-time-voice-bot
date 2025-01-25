import asyncio
import pyaudio
import boto3
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

# Define the custom event handler to process transcription results
class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(f"Transcript: {alt.transcript}")

# Function to capture audio from the microphone and send to Transcribe
async def transcribe_microphone_audio():
    client = TranscribeStreamingClient(region='us-east-2')
    
    # Start streaming transcription
    stream = await client.start_stream_transcription(
        language_code='en-US',
        media_sample_rate_hz=16000,  # Sample rate for your audio input
        media_encoding='pcm'         # Encoding type for the audio input
    )

    # Open the microphone stream for capturing audio
    p = pyaudio.PyAudio()
    stream_audio = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          input=True,
                          frames_per_buffer=1024)

    print("Listening...")

    # Send the audio chunks to Amazon Transcribe in real-time
    async def send_audio_chunks():
        while True:
            data = stream_audio.read(1024)  # Read 1024 bytes (adjust if needed)
            if not data:
                break
            await stream.input_stream.send_audio_event(audio_chunk=data)

        await stream.input_stream.end_stream()

    # Instantiate event handler and process transcription events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(send_audio_chunks(), handler.handle_events())

# Main function to run the transcription
async def main():
    await transcribe_microphone_audio()

# Run the asyncio loop
if __name__ == '__main__':
    asyncio.run(main())
