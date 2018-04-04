from __future__ import print_function, division
import math
from enum import Enum

import os
import sys  # for printing to stderr

from CYLGame import GameLanguage
from CYLGame import GridGame
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder
from CYLGame.Player import DefaultGridPlayer
from resources.Invader import Invader


class Direction(Enum):
    RIGHT = 1
    LEFT = 2


class SpaceInvaders(GridGame):
    MAP_WIDTH = 60
    MAP_HEIGHT = 25
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Space Invaders"
    CHAR_SET = "resources/terminal16x16_gs_ro.png"

    NUM_OF_INVADERS = 10
    TOTAL_INVADERS = 10
    MAX_TURNS = 900

    score = 0

    # we use these for moving the mothership easily
    LEFT = -1
    RIGHT = 1
    mothership_direction = RIGHT

    MOTHERSHIP_SPEED = 3
    mothership_exists = False

    MOTHERSHIP_L = chr(241)
    MOTHERSHIP_C = chr(242)
    MOTHERSHIP_R = chr(243)

    MOTHERSHIP_POINTS = 300
    INVADER0_POINTS = 50
    INVADER1_POINTS = 40
    INVADER2_POINTS = 30

    INVADER0 = chr(244)  # worth 50 points
    INVADER1 = chr(245)  # worth 40 points
    INVADER2 = chr(246)  # worth 30 points

    # create a list of sprite to blit by type on redraw
    INVADER_SPRITE = [INVADER0, INVADER1, INVADER2]
    BARRIER_1 = chr(247)
    BARRIER_2 = chr(248)
    BARRIER_3 = chr(249)
    BARRIER_4 = chr(250)
    MISSILE = chr(251)
    BULLET = chr(252)
    PLAYER_L = chr(253)
    PLAYER_C = chr(254)
    PLAYER_R = chr(255)
    EMPTY = ' '
    OUT_OF_BOUNDS = chr(240)

    fire_rate = 2  # the fire rate of invaders

    def __init__(self, random):
        self.random = random
        self.running = True
        self.centerx = self.MAP_WIDTH // 2
        self.centery = self.MAP_HEIGHT // 2
        self.player_pos = [self.centerx, (int)(self.MAP_HEIGHT * .99)]
        self.player_right = [self.centerx + 1, (int)(self.MAP_HEIGHT * .99)]
        self.player_left = [self.centerx - 1, (int)(self.MAP_HEIGHT * .99)]
        self.invaders = []
        self.drops_eaten = 0
        self.invaders_left = 0
        self.missiles_left = 0
        self.apple_pos = []
        self.objects = []
        self.turns = 0
        self.bullets_fired = 0
        self.level = 0
        self.gravity_power = 1
        self.bullet_speed = 3
        self.invader_speed = 1
        self.placed_invaders = 0
        self.movement_direction = Direction.RIGHT
        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT + 1, self.SCREEN_WIDTH - self.MSG_START, 5)
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT + 1, self.MSG_START, 5)
        self.panels = [self.msg_panel, self.status_panel]
        self.msg_panel.add("Welcome to " + self.GAME_TITLE + "!!!")
        self.lives = 3
        self.life_lost = False

        self.debug = False

    def init_board(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT, self.EMPTY,
                            border=PanelBorder.create(bottom="-"))
        self.panels += [self.map]

        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER_C
        self.map[(self.player_right[0], self.player_right[1])] = self.PLAYER_R
        self.map[(self.player_left[0], self.player_left[1])] = self.PLAYER_L

        self.draw_level()

    def start_game(self):
        pass

    def create_new_player(self, prog):
        self.player = DefaultGridPlayer(prog, self.get_move_consts())
        return self.player

    def draw_level(self):
        start_barrier = 5  # we want to offset the first barrier
        barrier_height = 3
        barrier_width = 5
        set_sb = False
        for w in range(0, 60):
            for h in range(0, 25):
                # generating the invaders -- 5 rows of 11, alternating columns and rows
                if h < 10 and w >= 20 and w <= 40:
                    if (w % 2 == 0) and (h % 2 == 0):
                        if h == 8 or h == 6:
                            self.invaders.append(Invader((w, h), 2))
                            self.map[(w, h)] = self.INVADER2
                        elif h == 4 or h == 2:
                            self.invaders.append(Invader((w, h), 1))
                            self.map[(w, h)] = self.INVADER1
                        else:
                            self.invaders.append(Invader((w, h), 0))
                            self.map[(w, h)] = self.INVADER0

                # generate the barriers
                if h >= self.MAP_HEIGHT - 1 - barrier_height and h < self.MAP_HEIGHT - 1:
                    # it's a barrier row
                    if w >= start_barrier and w <= start_barrier + barrier_width:  # we draw the barrier
                        self.map[(w, h)] = self.BARRIER_4
                        if w == start_barrier + barrier_width:
                            set_sb = True
            if set_sb:
                start_barrier += 12  # to achieve spacing between barriers...hopefully
                set_sb = False
        self.set_bottom_invaders()

    def set_bottom_invaders(self):
        # all_invaders = [ x for x in self.invaders ]
        cols = {}
        # sort all the invaders into columns
        for invader in self.invaders:
            pos = invader.get_pos()
            if pos[0] in cols:
                cols[pos[0]].append(invader)
            else:
                empty = []
                empty.append(invader)
                cols[pos[0]] = empty
        # sort each column on y value descending (high y values are "lower")
        for i in range(0, self.MAP_WIDTH):
            if i in cols:
                cols[i] = sorted(cols[i], key=lambda x: x.get_pos()[1], reverse=True)
                cols[i][0].set_bottom(True)

    def handle_mothership(self):
        # if there is a bullet in center_positon, center_position + direction * 1, * 2, or * 3 or * 4 (the right/left requires the *4, because the offset from center position is 1), or any of those positions are out of bounds, remove the entire mothership
        # move the center location over by 3.
        if not self.mothership_exists:
            return
        old_center = self.map.get_all_pos(self.MOTHERSHIP_C).pop()[0]
        redraw = True
        for i in range(0, 5):
            test_x = old_center + i * self.mothership_direction
            if test_x < 0 or test_x >= self.MAP_WIDTH:  # we fell off the map
                # remove mothership
                redraw = False
                self.mothership_exists = False

        clear_l = self.map.get_all_pos(self.MOTHERSHIP_L).pop()
        clear_c = self.map.get_all_pos(self.MOTHERSHIP_C).pop()
        clear_r = self.map.get_all_pos(self.MOTHERSHIP_R).pop()
        self.map[clear_l] = self.EMPTY
        self.map[clear_c] = self.EMPTY
        self.map[clear_r] = self.EMPTY

        if redraw:
            new_l = (clear_l[0] + 3 * self.mothership_direction, 0)
            new_c = (clear_c[0] + 3 * self.mothership_direction, 0)
            new_r = (clear_r[0] + 3 * self.mothership_direction, 0)

            self.map[new_l] = self.MOTHERSHIP_L
            self.map[new_c] = self.MOTHERSHIP_C
            self.map[new_r] = self.MOTHERSHIP_R

        return

    def launch_mothership(self):
        if self.turns % 45 == 0:  # launch mothership every 45 turns
            self.mothership_exists = True
            # launch the ship
            # if the turns are even, we launch from right and vice versa
            center_x = 1  # when launching from left we have to leave space for the left element
            if self.turns % 2 == 0:
                center_x = (int)(self.MAP_WIDTH * .99) - 1
                self.mothership_direction = self.LEFT
                # launch from right
                # the top row is 0
            else:
                self.mothership_direction = self.RIGHT

            position_l = (center_x - 1, 0)
            position_c = (center_x, 0)
            position_r = (center_x + 1, 0)
            self.map[position_l] = self.MOTHERSHIP_L
            self.map[position_c] = self.MOTHERSHIP_C
            self.map[position_r] = self.MOTHERSHIP_R

    def fire_missiles(self):
        for invader in self.invaders:
            if invader.get_bottom() and not invader.get_missile():  # it can fire
                invader_pos = invader.get_pos()
                # first we determine if the invader can fire...are there any invaders below it?
                # second we determine (randomly) if the invader will fire
                fire = self.random.randint(0, 30 - self.fire_rate)  # hacky way of increasing fire percentage
                if fire == 2:  # hacky way to set it to fire at a low percentage only
                    missile_pos = (invader_pos[0], invader_pos[1] + self.gravity_power)
                    if missile_pos[1] < self.MAP_HEIGHT:
                        invader.set_missile(missile_pos)

    def fire_turret(self):
        # place the bullet one over the position
        # can only have on bullet on the screen at once
        if len(self.map.get_all_pos(self.BULLET)) == 0:
            bullet_pos = (self.player_pos[0], self.player_pos[1] - 1)
            if self.is_barrier(self.map[bullet_pos]):
                self.map[bullet_pos] = self.decrement_barrier(self.map[bullet_pos])
            elif self.map[bullet_pos] == self.MISSILE:
                self.map[bullet_pos] = self.EMPTY
            else:
                self.map[bullet_pos] = self.BULLET
            self.bullets_fired += 1

    def is_barrier(self, c):
        if c == self.BARRIER_1 or c == self.BARRIER_2 or c == self.BARRIER_3 or c == self.BARRIER_4:
            return True
        return False

    def decrement_barrier(self, c):
        if c == self.BARRIER_1:
            return self.EMPTY
        elif c == self.BARRIER_2:
            return self.BARRIER_1
        elif c == self.BARRIER_3:
            return self.BARRIER_2
        elif c == self.BARRIER_4:
            return self.BARRIER_3
        else:
            return self.EMPTY

    def move_invaders(self):

        # determine if we can continue moving in the same direction (nothing will fall off the edge)
        move_down = False
        positions = None
        if self.movement_direction == Direction.RIGHT:
            # sort descending by x value
            positions = sorted([x.get_pos() for x in self.invaders], key=lambda x: x[0], reverse=True)
            # TODO: will this ever occur when we are not testing? Like when someone wins?
            if len(positions) == 0:
                return
            if self.debug:
                print(positions[0])
            if positions[0][0] + 1 >= self.MAP_WIDTH:
                move_down = True
                self.movement_direction = Direction.LEFT

        elif self.movement_direction == Direction.LEFT:
            positions = sorted([x.get_pos() for x in self.invaders], key=lambda x: x[0], reverse=False)
            if positions[0][0] - 1 < 0:
                move_down = True
                self.fire_rate += 1  # every time they move down, they fire a little bit faster
                self.movement_direction = Direction.RIGHT
            # sort ascending by x value
        if move_down:
            self.move_invaders_down()
            self.move_invaders()  # to move one in the new direction after going down
        elif not move_down:
            movement = self.invader_speed
            if self.movement_direction == Direction.LEFT:
                movement *= -1  # go the other direction
            for invader in self.invaders:
                pos = invader.get_pos()
                new_pos = (pos[0] + movement, pos[1])
                # if not self.map[new_pos] == self.BULLET: 
                invader.set_pos(new_pos)
                # else:
                #    #if its a barrier, we need to decrement it
                #    #if its a bullet, we need to remove it
                #    if self.map[new_pos] == self.BULLET:
                #      self.map[new_pos] == self.EMPTY
                #      print("collision with a bullet!")
                #    elif is_barrier(self.map[new_pos]):
                #      self.map[new_pos] = decrement_barrier(self.map[new_pos])
                #    self.invaders.remove(invader)

    def move_invaders_down(self):
        for invader in self.invaders:
            pos = invader.get_pos()
            new_pos = (pos[0], pos[1] + 1)
            if new_pos[1] < self.MAP_HEIGHT:
                # if self.map[new_pos] != self.BULLET: #it wasn't a hit
                invader.set_pos(new_pos)
                # else: #it was hit
                #    self.map[new_pos] = self.EMPTY

                #    self.invaders.remove(invader)

    def move_bullets(self):
        # there should only be one tbh
        # we need to get the list of all invader positions
        invader_positions = [x.get_pos() for x in self.invaders]
        missile_positions = [x.get_missile() for x in self.invaders]

        # we generate a list of all the mothership positions that we will encounter
        mothership_locations = []
        if self.mothership_exists:
            mothership_locations.append(self.map.get_all_pos(self.MOTHERSHIP_L).pop())
            mothership_locations.append(self.map.get_all_pos(self.MOTHERSHIP_C).pop())
            mothership_locations.append(self.map.get_all_pos(self.MOTHERSHIP_R).pop())
            # we add 2 because we need to detect a collision with the left/right, as well as the center.

        for pos in sorted(self.map.get_all_pos(self.BULLET), key=lambda x: x[1], reverse=False):
            still_exists = True
            # we iterate over all the positions that the bullet "warped" through to detect any collisions
            for i in range(0, self.bullet_speed):  # 0 - 1 so we clear the initial position
                clear = (pos[0], pos[1] - i)
                if clear[1] >= 0 and still_exists:
                    if clear in invader_positions:
                        # we need to find which invader it was and delete it
                        for invader in self.invaders:
                            if invader.get_pos() == clear:

                                # increment the score for the aliens
                                if invader.sprite == 0:
                                    self.score += self.INVADER0_POINTS
                                if invader.sprite == 1:
                                    self.score += self.INVADER1_POINTS
                                if invader.sprite == 2:
                                    self.score += self.INVADER2_POINTS

                                self.invaders.remove(invader)
                        still_exists = False
                        self.map[clear] = self.EMPTY
                        self.map[pos] = self.EMPTY
                    elif clear in mothership_locations:
                        still_exists = False
                        # remove the mothership from map
                        self.map[self.map.get_all_pos(self.MOTHERSHIP_L).pop()] = self.EMPTY
                        self.map[self.map.get_all_pos(self.MOTHERSHIP_R).pop()] = self.EMPTY
                        self.map[self.map.get_all_pos(self.MOTHERSHIP_C).pop()] = self.EMPTY
                        self.mothership_exists = False
                        self.score += self.MOTHERSHIP_POINTS

                    elif self.map[clear] == self.MISSILE:
                        # we need to track downt he invader which owns this missile
                        for invader in self.invaders:
                            if invader.get_missile() == clear:
                                invader.set_missile(False)
                        self.map[pos] = self.EMPTY
                        self.map[clear] = self.EMPTY
                        still_exists = False
                    elif self.is_barrier(self.map[clear]):
                        self.map[clear] = self.decrement_barrier(self.map[clear])
                        self.map[pos] = self.EMPTY
                        still_exists = False
                    else:
                        self.map[clear] = self.EMPTY
                        self.map[pos] = self.EMPTY

            new_pos = (pos[0], pos[1] - self.bullet_speed)
            if new_pos[1] >= 0 and still_exists:
                if new_pos in invader_positions:
                    for invader in self.invaders:
                        if invader.get_pos() == new_pos:
                            self.invaders.remove(invader)
                    still_exists = False
                    self.map[clear] = self.EMPTY
                elif new_pos in missile_positions:
                    for invader in self.invaders:
                        if invader.get_missile() == new_pos:
                            invader.set_missile(False)
                    still_exists = False
                    self.map[new_pos] = self.EMPTY
                elif self.is_barrier(self.map[new_pos]):
                    self.map[new_pos] = self.decrement_barrier(self.map[new_pos])
                    still_exists = False
                if still_exists:
                    self.map[new_pos] = self.BULLET
                    self.map[clear] = self.EMPTY
            # if not still_exists:
            #    self.map[new_pos] = self.EMPTY

    def do_turn(self):
        self.handle_key(self.player.move)
        self.player.bot_vars = self.get_vars_for_bot()
        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        if self.lives == 0:
            self.running = False
            self.msg_panel.add("You lost all your lives")
        if self.life_lost:
            self.life_lost = False
            self.msg_panel.add("You lost a life")

    def handle_key(self, key):
        self.turns += 1

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY
        self.map[(self.player_right[0], self.player_right[1])] = self.EMPTY
        self.map[(self.player_left[0], self.player_left[1])] = self.EMPTY
        # if key == "w":
        # self.player_pos[1] -= 1
        # if key == "s":
        # self.player_pos[1] += 1
        if key == "a":
            if self.player_left[0] - 1 >= 0:
                self.player_pos[0] -= 1
                self.player_right[0] -= 1
                self.player_left[0] -= 1
        if key == "d":
            if self.player_right[0] + 1 < self.MAP_WIDTH:
                self.player_pos[0] += 1
                self.player_right[0] += 1
                self.player_left[0] += 1
        if key == " ":
            self.fire_turret()
        if key == "Q":
            self.running = False
            return

        # move the invaders
        self.move_bullets()  # we do hits detection first
        self.move_invaders()
        self.move_missiles(self.gravity_power)  # move all drops down 1
        self.handle_mothership()

        # collision detection
        position = self.map[(self.player_pos[0], self.player_pos[1])]
        position_left = self.map[(self.player_left[0], self.player_left[1])]
        position_right = self.map[(self.player_right[0], self.player_right[1])]
        collision = False
        if position == self.MISSILE or position == self.INVADER2 or position == self.INVADER1 or position == self.INVADER0:
            collision = True
        if position_left == self.MISSILE or position == self.INVADER2 or position == self.INVADER1 or position == self.INVADER0:
            collision = True
        if position_right == self.MISSILE or position == self.INVADER2 or position == self.INVADER1 or position == self.INVADER0:
            collision = True

        # self.msg_panel.remove("You lost a life!")
        if collision:
            if self.debug:
                print("You lost a life!")
            self.msg_panel.add(["You lost a life!"])
            position = self.EMPTY  # clear the position
            self.lives -= 1
            # reset to center
            self.player_pos = [self.centerx, (int)(self.MAP_HEIGHT * .99)]
            self.player_right = [self.centerx + 1, (int)(self.MAP_HEIGHT * .99)]
            self.player_left = [self.centerx - 1, (int)(self.MAP_HEIGHT * .99)]
            # remove all missiles
            for invader in self.invaders:
                invader.set_missile(False)
            self.lost_life = True
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER_C
        self.map[(self.player_left[0], self.player_left[1])] = self.PLAYER_L
        self.map[(self.player_right[0], self.player_right[1])] = self.PLAYER_R

        # Fire the missiles
        self.fire_missiles()

        self.launch_mothership()

        if len(self.invaders) == 0:
            self.level += 1
        # first we clear all the prevoius invaders
        for old_invader in self.map.get_all_pos(self.INVADER2):
            self.map[old_invader] = self.EMPTY
        for old_invader in self.map.get_all_pos(self.INVADER1):
            self.map[old_invader] = self.EMPTY
        for old_invader in self.map.get_all_pos(self.INVADER0):
            self.map[old_invader] = self.EMPTY
        for old_missile in self.map.get_all_pos(self.MISSILE):
            self.map[old_missile] = self.EMPTY

        for invader in self.invaders:
            self.map[invader.get_pos()] = self.INVADER_SPRITE[invader.sprite]
            if invader.get_missile():
                self.map[invader.get_missile()] = self.MISSILE

    def move_missiles(self, gravity_power):  # gravity power is the number of positions a drop will fall per turn
        for invader in self.invaders:
            pos = invader.get_missile()
            if pos:
                # drop each by gravity_power
                new_pos = (pos[0], pos[1] + gravity_power)
                invader.set_missile(False)
                if new_pos[1] < self.MAP_HEIGHT:
                    if self.map[new_pos] == self.BULLET:
                        self.map[new_pos] = self.EMPTY
                    elif self.map[new_pos] == self.PLAYER_L or self.map[new_pos] == self.PLAYER_C or self.map[
                        new_pos] == self.PLAYER_R:
                        self.life_lost()
                    elif self.is_barrier(self.map[new_pos]):
                        self.map[new_pos] = self.decrement_barrier(self.map[new_pos])
                    else:
                        invader.set_missile(new_pos)
                        self.map[new_pos] = self.MISSILE
                else:  # it fell off the map
                    self.missiles_left -= 1

    def is_running(self):
        return self.running

    def get_char_consts(self):

        return {
            "MOTHERSHIP_L": ord(self.MOTHERSHIP_L),
            "MOTHERSHIP_C": ord(self.MOTHERSHIP_C),
            "MOTHERSHIP_R": ord(self.MOTHERSHIP_R),
            "INVADER0": ord(self.INVADER1),
            "INVADER1": ord(self.INVADER1),
            "INVADER2": ord(self.INVADER2),
            "BARRIER_1": ord(self.BARRIER_1),
            "BARRIER_2": ord(self.BARRIER_2),
            "BARRIER_3": ord(self.BARRIER_3),
            "BARRIER_4": ord(self.BARRIER_4),
            "MISSILE": ord(self.MISSILE),
            "BULLET": ord(self.BULLET),
            "PLAYER_L": ord(self.PLAYER_L),
            "PLAYER_C": ord(self.PLAYER_C),
            "PLAYER_R": ord(self.PLAYER_R),
            "EMPTY": ord(' '),
            "OUT_OF_BOUNDS": ord(self.OUT_OF_BOUNDS),
            "MAP_HEIGHT": self.MAP_HEIGHT,
            "MAP_WIDTH": self.MAP_WIDTH
        }

    def get_vars_for_bot(self):
        bot_vars = self.get_char_consts()
        # player x location (center)
        # mothership x location(center)
        bonus_ship_x = -1
        if self.mothership_exists:
            bonus_ship_x = self.map.get_all_pos(self.MOTHERSHIP_C).pop()[0]

        # for these, we send an array where 0 = y and 1 = the character (or self.EMPTY if nothing)
        # we send -1 if the location is out of bounds (for the left-1 and right+1)
        player_x = self.player_pos[0]

        player_left_minus_one = self.EMPTY
        for h in range(self.MAP_HEIGHT - 2, 0, -1):
            if player_x - 2 < 0:
                player_left_minus_one = self.OUT_OF_BOUNDS
            elif not self.map[(player_x - 2, h)] == self.EMPTY:
                player_left_minus_one = self.map[(player_x - 2, h)]
                break

        player_left = self.EMPTY
        for h in range(self.MAP_HEIGHT - 2, 0, -1):
            if not self.map[(player_x - 1, h)] == self.EMPTY:
                player_left = self.map[(player_x - 1, h)]
                break

        player_center = self.EMPTY
        for h in range(self.MAP_HEIGHT - 2, 0, -1):
            if not self.map[(player_x, h)] == self.EMPTY:
                player_center = self.map[(player_x, h)]
                break

        player_right = self.EMPTY
        for h in range(self.MAP_HEIGHT - 2, 0, -1):
            if not self.map[(player_x + 1, h)] == self.EMPTY:
                player_right = self.map[(player_x + 1, h)]
                break

        player_right_plus_one = self.EMPTY
        for h in range(self.MAP_HEIGHT - 2, 0, -1):
            if player_x + 2 >= self.MAP_WIDTH:
                player_right_plus_one = self.OUT_OF_BOUNDS
            elif not self.map[(player_x + 2, h)] == self.EMPTY:
                player_right_plus_one = self.map[(player_x + 2, h)]
                break

        bot_vars["bonus_ship_x"] = bonus_ship_x
        bot_vars["player_x"] = player_x
        bot_vars["player_left_minus_one"] = ord(player_left_minus_one)
        bot_vars["player_left"] = ord(player_left)
        bot_vars["player_center"] = ord(player_center)
        bot_vars["player_right"] = ord(player_right)
        bot_vars["player_right_plus_one"] = ord(player_right_plus_one)

        map_arr = []
        for w in range(0, self.MAP_WIDTH):
            w_arr = []
            for h in range(0, self.MAP_HEIGHT):
                w_arr.append(ord(self.map.p_to_char[(w, h)]))
            map_arr.append(tuple(w_arr))

        bot_vars["map_array"] = tuple(map_arr)

        # TODO: pass in the map to the bot

        if self.debug:
            print("returning bot_vars", bot_vars)
        return bot_vars

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open(os.path.join(os.path.dirname(__file__), "resources/sample_bot.lp"), "r").read()

    @staticmethod
    def get_intro():
        return open(os.path.join(os.path.dirname(__file__), "resources/intro.md"), "r").read()
        # return "Welcome to Space Invaders"

    def get_score(self):
        return self.score

    def draw_screen(self, frame_buffer):
        # if not self.running:
        # self.msg_panel += [""+str(self.drops_eaten)+" drops. Good job!"]

        # Update Status
        self.status_panel["Invaders"] = len(self.invaders)
        self.status_panel["Lives"] = str(self.lives)
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)
        self.status_panel["Score"] = str(self.score)

        for panel in self.panels:
            panel.redraw(frame_buffer)

    @staticmethod
    def get_move_consts():
        return {"west": ord("a"), "east": ord("d"), "fire": ord(" "), "stay": ord(".")}

    @staticmethod
    def get_move_names():
        return {ord("a"): "West", ord("d"): "East", ord(" "): "Fire", ord("."): "Stay"}


if __name__ == '__main__':
    from CYLGame import run

    run(SpaceInvaders)
