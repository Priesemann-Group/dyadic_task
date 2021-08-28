import tables
import os
from datetime import datetime
import configuration.conf as conf

file = None
path = ''


class Depositor:
    def __init__(self, output_folder, identifier):
        self._file = None
        self._path = ''
        self._new_file(output_folder, identifier)

    def deposit(self, game_state):
        self._file.root.data.append(game_state[None, :])

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
            os.remove(self._path)  # Remove invalid game record

    def _new_file(self, output_path, identifier):
        self._path = f'{output_path}/{identifier}.h5'
        os.mknod(self._path)
        self._file = tables.open_file(self._path, mode='w')
        atom = tables.Float64Atom()
        enlargeable_array_shape = (0, *conf.packet_shape)
        self._file.create_earray(self._file.root, 'data', atom, enlargeable_array_shape)


def get_output_dir_path():
    real_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(real_path) + '/../../' + conf.output_folder_name
    return dir_path


def create_parallel_game_folder():
    dir_path = get_output_dir_path()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    parallel_record_folder = f'{dir_path}/gs_{datetime.now().strftime(conf.date_format)}'
    os.makedirs(parallel_record_folder)
    return parallel_record_folder


def new_file():
    dir_path = get_output_dir_path()
    now = datetime.now()
    global file, path

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    path = f'{dir_path}/gs_{now.strftime(conf.date_format)}.h5'

    os.mknod(path)
    file = tables.open_file(path, mode='w')
    atom = tables.Float64Atom()

    enlargeable_array_shape = (0, *conf.packet_shape)
    print(enlargeable_array_shape)
    file.create_earray(file.root, 'data', atom, enlargeable_array_shape)


def deposit(game_state):
    file.root.data.append(game_state[None, :])


def close():
    global file
    if file is not None:
        file.close()
        file = None
        os.remove(path)  # Remove invalid game record


