#Instead of adding silence at start and end of recording (values=0) I add the original audio . This makes audio sound more natural as volume is >0. See trim()
#I also fixed issue with the previous code - accumulated silence counter needs to be cleared once recording is resumed.

from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave
import os
rows, columns = os.popen('stty size', 'r').read().split()
from datetime import date

THRESHOLD = 1500  # audio levels not normalised.
CHUNK_SIZE = 1024 * 2
RATE = 44100
SILENT_CHUNKS = 2 * RATE / 1024  # about 3sec
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
CHANNELS = 2
TRIM_APPEND = RATE / 4

class CliChart(object):
    DONE_ONE = False
    def print10(self, sel):
        if self.DONE_ONE:
            print '\033[F' * 13
        else:
            self.DONE_ONE = True

        height = 10
        MAX = 4000
        scaling_factor = MAX / height
        output = ""
        for i in range(height):
            for j in sel:
                if height - float(j)/float(scaling_factor) <= i:
                    output += "*"
                else:
                    output += " "
            output += "\n"
        # for j in sel:
            # output += str(int(float(j)/float(scaling_factor)))
        output += "\n"
        print output

data_chunk_maxes = []
clichart = CliChart()

def is_silent(data_chunk):
    """Returns 'True' if below the 'silent' threshold"""
    data_chunk_maxes.append(max(data_chunk))
    clichart.print10(data_chunk_maxes[-10:])
    return max(data_chunk) < THRESHOLD

def normalize(data_all):
    """Amplify the volume out to max -1dB"""
    # MAXIMUM = 16384
    normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))

    r = array('h')
    for i in data_all:
        r.append(int(i * normalize_factor))
    return r

def trim(data_all):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
        if abs(b) > THRESHOLD:
            _from = max(0, i - TRIM_APPEND)
            break

    for i, b in enumerate(reversed(data_all)):
        if abs(b) > THRESHOLD:
            _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
            break

    return copy.deepcopy(data_all[_from:(_to + 1)])

def record():
    """Record a word or words from the microphone and
    return the data as an array of signed shorts."""

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

    silent_chunks = 0
    audio_started = False
    data_all = array('h')

    while True:
        # little endian, signed short
        data_chunk = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        data_all.extend(data_chunk)

        silent = is_silent(data_chunk)

        if audio_started:
            if silent:
                silent_chunks += 1
                if silent_chunks > SILENT_CHUNKS:
                    break
            else:
                silent_chunks = 0
        elif not silent:
            audio_started = True

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
    data_all = normalize(data_all)
    return sample_width, data_all

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)

    wave_file = wave.open(path, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(RATE)
    wave_file.writeframes(data)
    wave_file.close()

if __name__ == '__main__':
    lines = {}
    with open('cmu_arctic.txt', 'r') as handle:
        for line in handle:
            id = line[2:14]
            sentent = line[16:-4]
            lines[id] = sentent

    data_dir = str(date.today().isoformat())
    try:
        os.makedirs(data_dir)
    except OSError:
        pass

    for idx, id in enumerate(sorted(lines)):
        outfile = os.path.join(data_dir, id + '.wav')
        if not os.path.exists(outfile):
            promptLine = '[%s %s/%s]> %s' % (id, idx, len(lines), lines[id])
            print promptLine, ' ' * (int(columns) - len(promptLine) - 1)
            record_to_file(outfile)
            print '\033[F' * 14
            clichart.DONE_ONE = False
