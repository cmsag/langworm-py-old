import math
import numpy
# opensimplex is a noise generator for Python that can generate 2D simplex noise
import opensimplex


# Based on the simplex1 function from Pink Trombone
# Generate 1D simplex noise
def simplex_1_noise(x):
    return opensimplex.noise2d(x * 1.2, -x * 0.7)

def clamp(x, minval, maxval):
    return max(minval, min(x, maxval))


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

        # Defined by the setup_waveform function
        self.waveformLength = None
        self.Te = None
        self.epsilon = None
        self.shift = None
        self.delta = None
        self.E_zero = None
        self.alpha = None
        self.omega = None
        # ---------------------------------------

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
        if self.UIFrequency > self.smoothFrequency:
            self.smoothFrequency = min(self.smoothFrequency * 1.1, self.UIFrequency)
        if self.UIFrequency < self.smoothFrequency:
            self.smoothFrequency = max(self.smoothFrequency / 1.1, self.UIFrequency)
        self.oldFrequency = self.newFrequency
        self.newFrequency = self.smoothFrequency * (1 + vibrato)
        self.oldTenseness = self.newTenseness
        self.newTenseness = self.UITenseness + 0.1 * simplex_1_noise(self.totalTime * 0.46) + 0.05 * simplex_1_noise(self.totalTime * 0.36)
        # UI functionality for changing values with mouse removed for now
        # if not self.isTouched and always_voice == True:
        #    self.newTenseness = self.newTenseness + (3 - self.UITenseness) * (1 - self.intensity)
        # if self.isTouched and always_voice == False:
        #    self.intensity = self.intensity + 0.13
        # else:
        #   self.intensity = self.intensity - 0.05
        self.intensity = self.intensity - 0.05

    def setup_waveform(self, L):
        # using "L" instead of lambda to accommodate for Python
        frequency = self.oldFrequency * (1 - L) + self.newFrequency * L
        tenseness = self.oldTenseness * (1 - L) + self.newTenseness * L
        Rd = 3 * (1 - tenseness)
        self.waveformLength = 1.0 / frequency

        clamp(Rd, 0.5, 2.7)

        # Normalised to time = 1, Ee = 1
        Ra = -0.01 + 0.048 * Rd
        Rk = 0.224 + 0.118 * Rd
        Rg = (Rk / 4) * (0.5 + 1.2 * Rk) / (0.11 * Rd - Ra *(0.5 + 1.2 * Rk))

        Ta = Ra
        Tp = 1 / (2 * Rg)
        self.Te = Tp + Tp * Rk

        self.epsilon = 1 / Ta
        self.shift = numpy.exp(-self.epsilon * (1 - self.Te))
        self.delta = 1 - self.shift # Divide by this to scale RHS

        RHSintegral = (1 / self.epsilon) * (self.shift - 1) + (1 - self.Te) * self.shift
        RHSintegral = RHSintegral / self.delta

        total_lower_integral = - (self.Te - Tp) / 2 + RHSintegral
        total_upper_integral = -total_lower_integral

        self.omega = math.pi / Tp
        s = math.sin(self.omega * self.Te)

        # need E0 * e ^ (alpha * Te) * s = -1(to meet the return at - 1)
        # and E0 * e ^ (alpha * Tp / 2) * Tp * 2 / pi = totalUpperIntegral
                                                         # (our approximation of the integral up to Tp)
                                                         # writing x for e ^ alpha,
        # have E0 * x ^ Te * s = -1 and E0 * x ^ (Tp / 2) * Tp * 2 / pi = totalUpperIntegral
        # dividing the second by the first,
        # letting y = x ^ (Tp / 2 - Te),
        # y * Tp * 2 / (pi * s) = -totalUpperIntegral;

        y = -math.pi * s * total_upper_integral / (Tp * 2)
        z = math.log(y)
        self.alpha = z / (Tp / 2 - self.Te)
        self.E_zero = -1 / (s * numpy.exp(self.alpha * self.Te))

    def normalised_waveform(self, t):
        if t > self.Te:
            output = (-numpy.exp(-self.epsilon * (t - self.Te)) + self.shift)/self.delta
        else:
            output = self.E_zero * numpy.exp(self.alpha * t) * math.sin(self.omega * t)

        return output * self.intensity * self.loudness
