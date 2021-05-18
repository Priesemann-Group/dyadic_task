
# Game config
ant_amount = 10
min_radius = 42
max_radius = 60
velocity = 3
time_to_occupy = .5  # TODO back to .5
occupied_animation_time = .3  # should be < time_to_occupy

competitive_reward = 1
cooperative_reward = 10

pos_updates_ps = 60
update_amount = pos_updates_ps * 20  # 20 seconds

# Appearance
font_name = 'Arial'
font_size = 20
font_color = (0, 0, 0, 255)
background_color = (255, 255, 255)
margin_color = (0, 0, 0)
player_radius = 5
ant_color = (100, 100, 200)
target_opacity = 64
popup_height = 20

player_colors = [
    (100, 100, 100),  # clients player color
    (200, 100, 100)   # opponents color
]

# Sound
player_volumes = [1., .4]


# Server configs
field_size = (1920, 1080)
server_ip = '134.76.24.227'
server_port = 8767

time_until_disconnect = 60

output_folder_name = 'game_records'
date_format = '%d-%m-%y_%H-%M-%S'

_rows = ant_amount + 4  # For the 4 headers
_cols = 4  # For x, y, rad, share values for each ant
packet_shape = (_rows, _cols)

# For sprite creation
ant_img_size = 256

# CHOOSEN SERVER PORTS
# 8766 - UDP - weltweit
# 8767 - UDP - weltweit
# 8768 - UDP - weltweit
