# Game config
ant_amount = 6
ant_radius = 50
velocity = 3
time_to_occupy = .5
occupied_animation_time = .3  # should be < time_to_occupy
ant_movement = True

time_before_round = 2
competitive_reward = 1
cooperative_reward = 10

pos_updates_ps = 60
#lap_time = 20  # for mouse control
lap_time = 60
update_amount = pos_updates_ps * lap_time

# Control
# WASD Control
#wasd_speed = 8  # for moving dots
wasd_speed = 16
wasd_diag_speed = wasd_speed/int((wasd_speed**2+wasd_speed**2)**.5)*wasd_speed
wasd_update_rate = 1/60

# Appearance
font_name = 'Arial'
font_size = 20
countdown_font_size = 64
popup_font_size = 42
score_chart_max_score = 1./time_to_occupy * lap_time * 8 * 1/3  # 8 is the average reward for cooperation, 1/3 is random
player_radius = 10
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

# Sound
player_volumes = [1., .4]


# Server configs
#field_size = (1920, 1080)
field_size = (1820, 1080)
score_chart_width = 100  # field_size[0] + score_chart_width = 1920
server_ip = '134.76.24.227'
server_port = 8767

time_until_disconnect = lap_time

output_folder_name = 'game_records'
date_format = '%d-%m-%y_%H-%M-%S'

_rows = ant_amount + 4  # For the 4 headers
_cols = 4  # For x, y, rad, share values for each ant
packet_shape = (_rows, _cols)

simultaneous_games = 2

# For sprite creation
ant_img_size = 256

# CHOOSEN SERVER PORTS
# 8766 - UDP - weltweit
# 8767 - UDP - weltweit
# 8768 - UDP - weltweit
