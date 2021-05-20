import tables
import os
from datetime import datetime
import configuration.conf as conf

file = None
path = ''


def get_output_dir_path():
    real_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(real_path) + '/../../' + conf.output_folder_name
    return dir_path


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
    file.create_earray(file.root, 'data', atom, enlargeable_array_shape)  # TODO use name for storing different games


def deposit(game_state):
    file.root.data.append(game_state[None, :])


def close():
    global file
    if file is not None:
        file.close()
        file = None
        os.remove(path)  # Remove invalid game record

