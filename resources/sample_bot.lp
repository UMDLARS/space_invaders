#There are several variables provided for your convenience. These are all the possible things that are in a square. Note that the player and mothership are both three classes wide, so they have a left, center, and right location. For the barriers and invaders, the different numbers correspond to different classes of barrier/invader. 
#Here is the list: MOTHERSHIP_L, MOTHERSHIP_C, MOTHERSHIP_R, INVADER0, INVADER1, INVADER2, ARRIER_1, BARRIER_2, BARRIER_3, BARRIER_4, MISSILE, BULLET, PLAYER_L, PLAYER_C, PLAYER_R, EMPTY, MAP_WIDTH, MAP_HEIGHT, OUT_OF_BOUNDS

#Your bot is also provided some basic variables. 
#player_left_minus_one, player_left, player_center, player_right, and player_right_plus_one will tell you what is above the player, as well as what is directly above the player one space to either direction.
#bonus_ship_x will contain the x position of the center of the bonus ship (aka the mothership) if it exists, otherwise this variable will contain the value -1
#player_x provides the player's x position (the center of the player)
#map_array contains the entire map as a two dimensional array (example of this being used at the bottom of the sample bot)

#this is a basic bot which will move randomly, trying to create a hole in barriers which it can shoot through. 

a = rand % 3

if a is 0 {
    move = west
}

if a is 1 {
    move = east
}

if a is 2 {
    move = fire
}

if player_center is BARRIER_4 or player_center is BARRIER_3 or player_center is BARRIER_2 or player_center is BARRIER_1 {
    move = fire
}

#example of accessing the map
#player_height = MAP_HEIGHT - 1
#if map_array[player_x][player_height] is PLAYER_C {
#    move = fire
#}
