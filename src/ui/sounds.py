from pyglet.media import load, Player
from os.path import realpath, dirname

dir_path = dirname(realpath(__file__)) + '/../../res/sound/'

occupying_sound = load(dir_path + 'occupying.ogg', streaming=False)
scored_sound = load(dir_path + 'scored.ogg', streaming=False)
slipped_off_sound = load(dir_path + 'slipped_off.ogg', streaming=False)


class OccupationSoundPlayer(Player):
    def __init__(self, volume):
        super().__init__()
        self._reward_player = Player()
        self._reward_player.volume = volume
        self.volume = volume

    def _force_play(self, sound):
        self.delete()
        self.next_source()
        self.queue(sound)
        self.play()

    def occupying(self):
        self._force_play(occupying_sound)

    def slipped_off(self):
        self._force_play(slipped_off_sound)

    def scored(self):
        self._reward_player.queue(scored_sound)
        self._reward_player.play()

