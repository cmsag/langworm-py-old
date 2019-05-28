import math
# opensimplex is a noise generator for Python that can generate 2D simplex noise
import opensimplex


# Based on the simplex1 function from Pink Trombone
def simplex_1_noise(x):
    return opensimplex.noise2d(x * 1.2, -x * 0.7)


class Glottis:

    def __init__(self, sample_rate):

        self.sampleRate = sample_rate

        self.timeInWaveform = 0,
        self.oldFrequency = 140,
        self.newFrequency = 140,
        self.UIFrequency = 140,
        self.smoothFrequency = 140,
        self.oldTenseness = 0.6,
        self.newTenseness = 0.6,
        self.UITenseness = 0.6,
        self.totalTime = 0,
        self.vibratoAmount = 0.005,
        self.vibratoFrequency = 6,
        self.intensity = 0,
        self.loudness = 1,
        self.isTouched = False,
        self.touch = 0,
        self.x = 240,
        self.y = 530,
        self.semitones = 20,
        self.marks = [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        self.baseNote = 87.3071

        self.waveformLength = None

    def run_step(self, L, noise_source):

        time_step = 1 / self.sampleRate
        self.timeInWaveform += time_step
        self.totalTime += time_step
        if self.timeInWaveform > self.waveformLength:
            self.timeInWaveform -= self.timeInWaveform
            self.setup_waveform(L)
        out = self.normalised_LF_waveform(self.timeInWaveform / self.timeInWaveform)
        aspiration = self.intensity * (1 - math.sqrt(self.tenseness)) * self.get_noise_modulator() * noise_source
        aspiration = aspiration * 0.2 + 0.2 * simplex_1_noise(self.totalTime * 1.99)
        out = out + aspiration
        return out

    def get_noise_modulator(self):
        voiced = 0.1 + 0.2 * max(0, math.sin(math.pi * 2 * self.timeInWaveform / self.waveformLength))
        return self.UITenseness * self.intensity * voiced + (1 - self.UITenseness * self.intensity) * 0.3

    def finish_block(self):
        vibrato = 0
        vibrato = vibrato + self.vibratoAmount * math.sin(2 * math.pi * self.totalTime * self.vibratoFrequency)
        vibrato = vibrato + 0.02 * simplex_1_noise(self.totalTime * 4.07)
        vibrato = vibrato + 0.04 * simplex_1_noise(self.totalTime * 2.15)
        # Autowobble function removed for now
        # if autowobble == True:
        #    vibrato = vibrato + 0.02 * simplex_1_noise(self.totalTime * 0.98)
        #    vibrato = vibrato + 0.04 * simplex_1_noise(self.totalTime * 0.5)
        
        # ...
        # Function WiP
        # ...

    def setup_waveform(self, L):

        frequency = self.oldFrequency * (1 - L) + self.newFrequency * L
        tenseness = self.oldTenseness * (1 - L) + self.newTenseness * L
        Rd = 3 * (1 - tenseness)
        self.waveformLength = 1.0 / frequency
        # ...
        # Function WiP
        # ...
