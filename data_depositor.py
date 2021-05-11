import tables
import os
import conf

file = tables.File(conf.game_state_data_file_name)


def get_output_path():
    real_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(real_path)
    return f'{dir_path}/{conf.game_state_data_file_name}'


def init():
    global file
    path = get_output_path()
    if os.path.exists(path):
        os.remove(path)
    os.mknod(path)
    file = tables.open_file(path, mode='w')
    atom = tables.Float64Atom()

    enlargeable_array_shape = (0, *conf.packet_shape)
    file.create_earray(file.root, 'data', atom, enlargeable_array_shape)


def deposit(game_state):
    file.root.data.append(game_state[None, :])


def close():
    file.close()

