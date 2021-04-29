import time
import conf as c
import random as r
import numpy as np
from numba import njit

pos = np.full((c.ant_amount, 2), np.nan, dtype='float64')
vel = np.full((c.ant_amount, 2), np.nan, dtype='float64')
rad = np.full(c.ant_amount, np.nan, dtype='float64')

score = [0, 0]


@njit
def euclid_dist(vec):
    return (vec[0] ** 2 + vec[1] ** 2) ** .5


@njit
def collision_calc(ants, radians):
    coll_count = 0
    colls = np.array([[-1, -1]] * len(ants))
    already_calculated = [False] * len(ants)  # TODO resize?

    for i in range(len(ants)):
        for k in range(i + 1, len(ants)):
            if not already_calculated[k]:
                dist = euclid_dist(ants[k] - ants[i])
                if dist < radians[i] + radians[k]:
                    already_calculated[k] = True
                    colls[coll_count] = np.array([i, k])
                    coll_count += 1
    return list(colls)


def load():
    global pos, vel, rad
    collision_calc(pos, rad)
    euclid_dist(np.array([0, 0]))

    for _ in range(c.ant_amount):  # TODO
        add_rand_ant()


def add_ant(x, y, angle, radius=None):
    if not radius:  # TODO del this
        radius = r.uniform(c.min_radius, c.max_radius)
    global pos, vel
    i = np.where(np.isnan(pos[:, 0]))[0][0]  # Assumption: There is always at least one nan!
    pos[i] = np.array([x, y], dtype='float64')
    vel[i] = np.array([np.cos(angle), np.sin(angle)]) * c.start_velocity
    rad[i] = radius


def add_rand_ant():
    x, y = r.randrange(c.field_size[0]), r.randrange(c.field_size[1])
    radius = r.uniform(c.min_radius, c.max_radius)
    proposed_pos = np.array([x, y])
    is_valid = True
    while is_valid:  # randomize until no collision to other points.
        is_valid = False
        for i in range(len(pos)):
            if not np.isnan(pos[i][0]):
                dist = euclid_dist(pos[i] - proposed_pos)
                if dist < rad[i] + radius:
                    x, y = r.randrange(c.field_size[0]), r.randrange(c.field_size[1])
                    radius = r.uniform(c.min_radius, c.max_radius)
                    proposed_pos = np.array([x, y])
                    is_valid = True
                    break
    angle = r.uniform(0., np.pi * 2)
    add_ant(x, y, angle)


def rad_to_area(i):
    return np.pi * rad[i] ** 2


def collision_next_iter(i, k):
    global pos, vel
    return euclid_dist((pos[i] - vel[i]) - (pos[k] - vel[k])) < rad[i] + rad[k]


collided_last_iter = []


def collisions():
    global pos, vel
    colls = collision_calc(pos, rad)
    for i, k in colls:
        if i == -1:
            break
        if tuple(sorted((i, k))) in collided_last_iter:
            if collision_next_iter(i, k):
                continue
            else:
                collided_last_iter.remove(tuple(sorted((i, k))))
        area_i = rad_to_area(i)
        area_k = rad_to_area(k)
        joint_vel = (vel[i] * area_i + vel[k] * area_k) / (area_i + area_k)
        vel[i] = 2 * joint_vel - vel[i]
        vel[k] = 2 * joint_vel - vel[k]
        if collision_next_iter(i, k):
            collided_last_iter.append(tuple(sorted((i, k))))


def correct_to_boundaries():
    for i in range(len(pos)):
        if not np.isnan(pos[i][0]):
            if pos[i][0] < 0 + rad[i]:
                pos[i][0] = 1 + rad[i]
                vel[i][0] *= -1
            elif pos[i][0] > c.field_size[0] - rad[i]:
                pos[i][0] = c.field_size[0] - 1 - rad[i]
                vel[i][0] *= -1
            if pos[i][1] < 0 + rad[i]:
                pos[i][1] = 1 + rad[i]
                vel[i][1] *= -1
            elif pos[i][1] > c.field_size[1] - rad[i]:
                pos[i][1] = c.field_size[1] - 1 - rad[i]
                vel[i][1] *= -1


def update(dt):
    global pos, vel
    pos += vel
    collisions()
    correct_to_boundaries()


target_idx = [-1, -1]
target_occupation_date = [0., 0.]


def get_target_state(mouse_positions):
    out = [-1, -1]
    for i, mouse_pos in enumerate(mouse_positions):
        global target_idx, target_occupation_date
        mouse_pos = np.array(mouse_pos)

        if target_idx[i] != -1:  # mouse was on a target
            dist = euclid_dist(pos[target_idx[i]] - mouse_pos)
            if dist < rad[target_idx[i]]:  # mouse is still on the target
                t = time.time()
                if t > target_occupation_date[i]:  # occupied the target
                    pos[target_idx[i]] = np.array([np.nan, np.nan])  # TODO
                    add_rand_ant()
                    target_idx[i] = -1
                    target_occupation_date[i] = 0.
                    out[i] = -1
                    score[i] += 1
                else:  # not occupied jet
                    time_left = target_occupation_date[i] - t
                    out[i] = target_idx[i] + time_left / c.time_to_occupy
            else:  # mouse was on a target but lost it
                target_idx[i] = -1
                target_occupation_date[i] = 0.
                out[i]
        else:  # mouse was on no target, check if it is now
            for k, p in enumerate(pos):
                dist = euclid_dist(p - mouse_pos)
                if dist < rad[k]:
                    target_idx[i] = k
                    target_occupation_date[i] = time.time() + c.time_to_occupy
    return out
