import pkg_resources
#pkg_resources.require('Twisted==21.7.0')
pkg_resources.require('pyglet==1.5.16')
#pkg_resources.require('numba==0.53.1')
#pkg_resources.require('numpy==1.20.3')

# Game config
#ant_amount = 6
coop_reward = 16
coop_split = 1/8
comp_reward = 12

#from backend.ant_kind import AntKind

#ant_kinds = [AntKind.SHARED_2,
#             AntKind.SHARED_14,
#             AntKind.COMPETITIVE_5]
ant_kinds = [1, 4, 7]

ant_amount = len(ant_kinds)
ant_radius = 70
#velocity = 3
#velocity = 2
velocity = 1.5
#time_to_occupy = .5
time_to_occupy = 1
occupied_animation_time = .3  # should be < time_to_occupy
ant_movement = False

ant_disappearance = False
ant_lifetime = 5

#time_before_round = 2
time_before_round = 5

pos_updates_ps = 60
lap_time = 2 * 60
simultaneous_games = 1
laps_to_play = 1

update_amount = pos_updates_ps * lap_time

# Control
# WASD Control
#wasd_speed = 8  # for moving dots
#wasd_speed = 16
wasd_speed = 10
#wasd_diag_speed = wasd_speed/int((wasd_speed**2+wasd_speed**2)**.5)*wasd_speed
wasd_diag_speed = (wasd_speed**2/2)**.5
wasd_update_rate = 1/60
speed = wasd_speed / wasd_update_rate  # todo rename?

# Appearance
font_name = 'Arial'
font_size = 20
reward_label_size = 20
countdown_font_size = 64
popup_font_size = 42
#score_chart_max_score = 1./time_to_occupy * lap_time * 8 * 1/2  # 8 is the average reward for cooperation, 1/3 is random
#score_chart_max_score = 1./time_to_occupy * lap_time * 8 / 8 # * 1/8  # 8 is the average reward for cooperation, 1/3 is random
score_chart_max_score = -1 # disabled
#player_radius = 10
player_radius = 20
target_opacity = 255
popup_height = 64

background_color = (255, 255, 255)
margin_color = (0, 0, 0)
score_chart_bg_color = (32, 32, 32)
border_black = (32, 32, 32)
font_color = (0, 0, 0, 255)

dyadic_background_color = (0, 0, 0)
dyadic_margin_color = (255, 255, 255)
dyadic_score_chart_bg_color = (223, 223, 223)
dyadic_border_black = (223, 223, 223)
dyadic_font_color = (255, 255, 255, 255)

player_colors = [
    (87, 117, 180),  # clients player color
    (250, 114, 44)   # opponents color
]
competitive_reward_color = (100, 100, 100)
ant_base_color = (200, 200, 200)  # TODO rename

prediction_color = (255, 0, 255)

# Sound
player_volumes = [1., .4]


# Replay config
secs_jumps = 10


# Server config
#field_size = (1920, 1080)
field_size = (1820, 1080)  # TODO change this back
# 910 540
score_chart_width = 100  # field_size[0] + score_chart_width = 1920
server_ip = '134.76.24.227'
server_port = 8767

time_until_disconnect = lap_time

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
