#!/usr/bin/env python

import sys
import argparse
import os
import serial
import pyaudio
import numpy as np

ascii_to_morse = {
        'A': '.-',              'a': '.-',
        'B': '-...',            'b': '-...',
        'C': '-.-.',            'c': '-.-.',
        'D': '-..',             'd': '-..',
        'E': '.',               'e': '.',
        'F': '..-.',            'f': '..-.',
        'G': '--.',             'g': '--.',
        'H': '....',            'h': '....',
        'I': '..',              'i': '..',
        'J': '.---',            'j': '.---',
        'K': '-.-',             'k': '-.-',
        'L': '.-..',            'l': '.-..',
        'M': '--',              'm': '--',
        'N': '-.',              'n': '-.',
        'O': '---',             'o': '---',
        'P': '.--.',            'p': '.--.',
        'Q': '--.-',            'q': '--.-',
        'R': '.-.',             'r': '.-.',
        'S': '...',             's': '...',
        'T': '-',               't': '-',
        'U': '..-',             'u': '..-',
        'V': '...-',            'v': '...-',
        'W': '.--',             'w': '.--',
        'X': '-..-',            'x': '-..-',
        'Y': '-.--',            'y': '-.--',
        'Z': '--..',            'z': '--..',
        '0': '-----',           ',': '--..--',
        '1': '.----',           '.': '.-.-.-',
        '2': '..---',           '?': '..--..',
        '3': '...--',           ';': '-.-.-.',
        '4': '....-',           ':': '---...',
        '5': '.....',           "'": '.----.',
        '6': '-....',           '-': '-....-',
        '7': '--...',           '/': '-..-.',
        '8': '---..',           '(': '-.--.-',
        '9': '----.',           ')': '-.--.-',
        ' ': ' ',               '_': '..--.-',
        '\n': '.-.-',           'del': '........',
}

morse_to_ascii = {v: k.lower() for k, v in ascii_to_morse.items()}

specialcommands = {
    '\n': 'xte "key Return"',
    'del': 'xte "key BackSpace"'
}

class AudioFifo(object):
    def __init__(self):
        self.buf = np.zeros(0, dtype=np.int8)

    def write(self, buffer):
        self.buf = np.concatenate((self.buf, buffer))

    def read(self, size):
        zerolen = max(0, size - self.buf.size)
        datalen = min(size, self.buf.size)

        data = np.concatenate((self.buf[0:datalen], np.zeros(zerolen, dtype=np.int8)))
        self.buf = self.buf[datalen:]

        return data


audio_data = AudioFifo()

def callback(in_data, frame_count, time_info, status):
    data = audio_data.read(frame_count) + 127
    return (data, pyaudio.paContinue)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--baudrate', type=int, help='Baudrate of morse key', default=115200)
    parser.add_argument('-d', '--device', type=str, help='Serial port', default='/dev/ttyUSB0')
    parser.add_argument('-w', '--wpm', type=int, help='Words per minute', default=20)
    parser.add_argument('--samplerate', type=int, help='Audio sample rate', default=48000)
    parser.add_argument('-f', '--frequency', type=int, help='Tone frequency', default=700)

    args = parser.parse_args()

    p = serial.Serial(port=args.device, baudrate=args.baudrate, timeout=1.2/args.wpm)
    p.write(bytes([args.wpm]))

    audio = pyaudio.PyAudio()

    stream = audio.open(format = audio.get_format_from_width(1),
                        channels = 1,
                        rate = args.samplerate,
                        output = True,
                        stream_callback=callback)
    
    dit_samples = args.samplerate * 1.2 / args.wpm
    dah_samples = args.samplerate * 1.2 / args.wpm * 3

    dit = np.array(np.sin(2*np.pi*args.frequency * np.arange(dit_samples) / args.samplerate) * 127, dtype=np.int8)
    dit = np.concatenate((dit, np.zeros(dit_samples, dtype=np.int8) * 127))

    dah = np.array(np.sin(2*np.pi*args.frequency * np.arange(dah_samples) / args.samplerate) * 127, dtype=np.int8)
    dah = np.concatenate((dah, np.zeros(dit_samples, dtype=np.int8)))

    try:
        code = ''
        while True:
            c = p.read().decode()

            if c == '.':
                audio_data.write(dit)
                code += '.'
            elif c == '-':
                audio_data.write(dah)
                code += '-'
            elif c == '\n':
                char = morse_to_ascii.get(code, None)

                if char is not None:
                    cmd = specialcommands.get(char, 'xte "str {}"'.format(char))
                    os.system(cmd)
                    print(char, end='')

                code = ''

            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    
    p.close()

    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == '__main__':
    sys.exit(main() or 0)
