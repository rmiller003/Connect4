import wave
import struct

def create_silent_wav(filename, duration=1, framerate=44100, channels=1, sampwidth=2):
    nframes = int(duration * framerate)
    wav_file = wave.open(filename, 'w')
    wav_file.setparams((channels, sampwidth, framerate, nframes, 'NONE', 'not compressed'))

    for _ in range(nframes):
        wav_file.writeframes(struct.pack('h', 0))

    wav_file.close()

if __name__ == '__main__':
    create_silent_wav('sonar-ping.wav')
    create_silent_wav('ping.wav')
    print("Silent WAV files created successfully.")
