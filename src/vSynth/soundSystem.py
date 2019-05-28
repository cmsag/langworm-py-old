
block_length = 512
block_time = 1
started = False
sound_on = False

class soundSystem():

    def __init__(self, sample_rate):
        # Defined elsewhere, sample_rate should be passed to the class upon instantiation
        self.sample_rate = sample_rate

        self.block_time = block_length / self.sample_rate

    def start_sound(self):
        # Create 2 seconds of noise
        duration = 2
        white_noise = self.create_white_noise_node(duration * self.sample_rate)

    # ...
    # Function WiP
    # ...

    def create_white_noise_node(self):
        pass

    # ...
    # Function WiP
    # ...
