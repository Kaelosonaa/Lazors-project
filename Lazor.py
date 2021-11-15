'''
Johns Hopkins University
Department of Chemical and Biomolecular Engineering
Lazor Project Fall 2021
Software Carpentry Project
Authors: Zijian Zhong, Dake Guo, Yu Xu

Welcome to our Lazor Project!
The goal of the project is to write a python code in order to generate
a solution of the game called Lazor.
The Lazor game can be downloaded either from Android or App Store.
The objective of the Lazor game is to rearrange three different types
of blocks on a map so that the lazor beam will cross the points specified
on the map.

In order to play the Lazor game, you will need this python file and .bff
files that can be found in our repository. The .bff files will include
different setups of the Lazor game, for example:

The Mad_1.bff file looks likes this:

Nomenclature follows these rules:
    x = no block allowed
    o = blocks allowed
    A = fixed reflect block
    B = fixed opaque block
    C = fixed refract block
# Grid will start at top left being 0, 0
# Step size is by half blocks
# Thus, this leads to even numbers indicating
# the rows/columns between blocks, and odd numbers
# intersecting blocks.
[For Example]
GRID START
o   o   o   o
o   o   o   o
o   o   o   o
o   o   o   o
GRID STOP

*** Movable Blocks ***
Informations of which and how many blocks that's movable.
(Type Amount)
Types:
    A = fixed reflect block
    B = fixed opaque block
    C = fixed refract block
[For Example]
A 2
C 1

*** Lazor ***
# Now we specify that we have two lazors
#    x, y, vx, vy
# NOTE! because 0, 0 is the top left, our axis
# are as follows:
#
#      __________  +x
#      |         /
#      |
#      |
#      |
#      |/ +y
Information of each lazor is stored as:
L x y x-direction y-direction
[For Example]
(L 2 7 1 -1)
*** Target Points ***
# Here we have the points that we need the lazers to intersect
(P x y)
[For Example]
P 3 0
P 4 3
P 2 5
P 4 7

'''

from PIL import Image, ImageDraw
import random
import time

X_POS = 0
Y_POS = 1
X_DIR = 2
Y_DIR = 3
REFLECT = 0
REFRACT = 1
OPAQUE = 2
EMPTY = 3
NONE = -1
# set the constant for initial position and initial
# lazor direction.
# assign different constant to represent reflect, refract
# and opaque blocks


def debug_print(string):
    if 0:
        print(string)
    # debug function to test whether the information from file work


class Lazor():
    def __init__(self):
        '''
        This function is used to record all the data we need to solve
        the puzzle in the list. The reflect block, refract blocks and
        opaque blocks have count list to record the number from the .bff
        file. We also record the action history of the laser as a list,
        which is convenient for us to test and also easy to generate pictures.
        '''
        self.width = 0
        self.height = 0
        # set the width and height of the board
        self.reflect_block = list()
        self.refract_block = list()
        self.opaque_block = list()
        # set the list of 3 different blocks
        self.empty_block = list()
        self.available_block = list()
        # set the list of empty and available blocks
        self.reflect_block_count = 0
        self.refract_block_count = 0
        self.opaque_block_count = 0
        # get the number of 3 blocks from file
        self.original_reflect_block = list()
        self.original_refract_block = list()
        self.original_opaque_block = list()
        # set the list of 3 blocks in the original grid
        self.original_empty_block = list()
        self.original_available_block = list()
        # set the list of empty and available blocks in the original grid
        self.original_reflect_block_count = 0
        self.original_refract_block_count = 0
        self.original_opaque_block_count = 0
        # get the number of 3 blocks from the gird in file

        self.laser = list()
        self.laser_history = list()
        self.goals = list()
        # set the list of lazor initial position, move history and destination

    def generate_from_bff(self, bff_file):
        '''
        This function is used to get the data from the .bff file.
        We need the grid between Grid.Start and Grid.Stop, the block
        number of A, B, C three kinds of blocks, the lazor initial
        position and direction, and the points needed to pass.
        '''
        with open(bff_file, 'r') as f_ptr:
            raw_content = f_ptr.readlines()
            # read the .bff file from the folder
            content = list()

            for line in raw_content:
                if(line[0] == '#' or line[0] == '\n'):
                    continue
                content.append(line.replace("\n", ""))
                # remove the comment and empty line

            idx = 0
            while idx < len(content):
                if(content[idx] == "GRID START"):
                    idx += 1
                    line = content[idx].replace(' ', '')
                    self.width = len(line)*2 + 1

                    grid_y = 1
                    while(content[idx] != "GRID STOP"):
                        line = content[idx].replace(' ', '')
                        # in the range between start and stop srtings,
                        # get the grid
                        grid_x = 1
                        for char in line:
                            if(char == 'o'):
                                self.original_available_block.append((grid_x, grid_y))
                            elif(char == 'A'):
                                self.original_reflect_block.append((grid_x, grid_y))
                            elif(char == 'B'):
                                self.original_opaque_block.append((grid_x, grid_y))
                            elif(char == 'C'):
                                self.original_refract_block.append(((grid_x, grid_y)))
                            elif(char == 'x'):
                                self.original_empty_block.append(((grid_x, grid_y)))
                            # find and save the coordinate of blocks in the original grids
                            grid_x += 2
                        grid_y += 2
                        idx += 1
                    self.height = grid_y
                if(content[idx][0] == 'A'):
                    self.original_reflect_block_count = int(content[idx][-1])
                elif(content[idx][0] == 'C'):
                    self.original_refract_block_count = int(content[idx][-1])
                elif(content[idx][0] == 'B'):
                    self.original_opaque_block_count = int(content[idx][-1])
                elif(content[idx][0] == 'L'):
                    initial_laser_data = content[idx][1:].split()
                    for i in range(len(initial_laser_data)):
                        initial_laser_data[i] = int(initial_laser_data[i])
                    self.laser.append(tuple(initial_laser_data))
                elif(content[idx][0] == 'P'):
                    goals_data = content[idx][1:].split()
                    for i in range(len(goals_data)):
                        goals_data[i] = int(goals_data[i])
                    self.goals.append(tuple(goals_data))
                idx += 1
                # find and save the coordinate of A, B, C,lazor initial
                # position and direction, points needs to pass.
            self.available_block = list(self.original_available_block)
            self.opaque_block = list(self.original_opaque_block)
            self.reflect_block = list(self.original_reflect_block)
            self.refract_block = list(self.original_refract_block)
            self.empty_block = list(self.original_empty_block)
            self.reflect_block_count = 0
            self.refract_block_count = 0
            self.opaque_block_count = 0
            debug_print(self.original_reflect_block_count)
            debug_print(self.original_refract_block_count)
            debug_print(self.original_opaque_block_count)
            # debug the count number lists of 3 different blocks

    def reset(self):
            self.available_block = list(self.original_available_block)
            self.opaque_block = list(self.original_opaque_block)
            self.reflect_block = list(self.original_reflect_block)
            self.refract_block = list(self.original_refract_block)
            self.empty_block = list(self.original_empty_block)
            self.reflect_block_count = 0
            self.refract_block_count = 0
            self.opaque_block_count = 0
            self.laser_history = list()
            '''
            This function is used to reset the lists of block count
            and lazor moving history, which means for multipy tries.
            '''

    def draw(self):
        '''
        This function is used to generate the image from the lists.
        We used different color to represent the different block condition.
        The solution is saved as a image in the file where the .bff.file sets.
        '''
        img = Image.new(mode ="RGB", size = (self.width * 50, self.height * 50), color ="orange")
        img.save("solution.png")
        image = Image.open("solution.png")
        draw = ImageDraw.Draw(image)
        for block in self.available_block:
            draw.rectangle((block[0]*50, block[1]*50, block[0]*50 + 50, block[1]*50 + 50))
            # the available block has no color
        for block in self.empty_block:
            draw.rectangle((block[0]*50, block[1]*50, block[0]*50 + 50, block[1]*50 + 50),
            fill = "grey")
            # the empty block are grey
        for block in self.opaque_block:
            draw.rectangle((block[0]*50, block[1]*50, block[0]*50 + 50, block[1]*50 + 50),
            fill = "black")
            # the opaque blocks are black
        for block in self.reflect_block:
            draw.rectangle((block[0]*50, block[1]*50, block[0]*50 + 50, block[1]*50 + 50),
            fill = "blue")
            # the reflect blocks are blue
        for block in self.refract_block:
            draw.rectangle((block[0]*50, block[1]*50, block[0]*50 + 50, block[1]*50 + 50),
            fill = "white")
            # the refract blocks are white
        for goal in self.goals:
            draw.ellipse((goal[0]*50+20, goal[1]*50+20, goal[0]*50 + 30, goal[1]*50 + 30),
            fill = 'blue')
            # the point needed to pass are blue
        for laser in self.laser_history:
            draw.line((laser[0][0]*50+25,laser[0][1]*50+25) + (laser[1][0]*50+25,
            laser[1][1]*50+25), width = 5, fill = "red")
        image.save("solution.png")
        print("Solution exported in solution.png")
        # save the generated picture as solution.png

    def start_game(self):
        '''
        This function is used to return the different numbers for different blocks
        '''
        def find_block(position):
            if position in self.reflect_block:
                return 0
            elif position in self.refract_block:
                return 1
            elif position in self.opaque_block:
                return 2
            elif position in self.available_block or position in self.empty_block:
                return 3
            else:
                return -1

        def in_bound(laser):
            '''
            This function is used to ensure we only count the lazor in the range
            '''
            return (laser[X_POS] < self.width and laser[Y_POS] < self.height)

        def change_sign(num):
            '''
            This function is used to change lazor's directions.
            '''
            if num == 1:
                return -1
            else:
                return 1
        laser_queue = list()
        for laser in self.laser:
            laser_queue.append(laser)
        goals = list(self.goals)
        # list of the points needed to pass
        visted_history = list()
        # list of move history of lasor
        while len(laser_queue):
            debug_print(laser_queue)
            current_laser = laser_queue[0]
            if current_laser in visted_history:
                break
            visted_history.append(current_laser)
            # record the lazor moving history
            laser_history = [(current_laser[X_POS], current_laser[Y_POS])]
            # only count the lazor history in the range
            while in_bound(current_laser):
                debug_print(current_laser)
                if (current_laser[X_POS], current_laser[Y_POS]) in goals:
                    goals.remove((current_laser[X_POS], current_laser[Y_POS]))
                block_encounter = find_block((current_laser[X_POS] + current_laser[X_DIR],
                current_laser[Y_POS]))
                encounter_dir = 0
                if block_encounter == NONE:
                    block_encounter = find_block((current_laser[X_POS], current_laser[Y_POS] +
                    current_laser[Y_DIR]))
                    if block_encounter == NONE:
                        laser_queue.pop(0)
                        break
                    encounter_dir = 1
                if block_encounter == REFLECT:
                    if encounter_dir == 1:
                        laser_queue.append((current_laser[X_POS], current_laser[Y_POS],
                        current_laser[X_DIR], change_sign(current_laser[Y_DIR])))
                    else:
                        laser_queue.append((current_laser[X_POS], current_laser[Y_POS],
                        change_sign(current_laser[X_DIR]), current_laser[Y_DIR]))
                    laser_queue.pop(0)
                    break
                elif block_encounter == REFRACT:
                    if encounter_dir == 1:
                        laser_queue.append((current_laser[X_POS], current_laser[Y_POS],
                        current_laser[X_DIR], change_sign(current_laser[Y_DIR])))
                    else:
                        laser_queue.append((current_laser[X_POS], current_laser[Y_POS],
                        change_sign(current_laser[X_DIR]), current_laser[Y_DIR]))
                    current_laser = (current_laser[X_POS] + current_laser[X_DIR], current_laser[Y_POS] +
                    current_laser[Y_DIR], current_laser[X_DIR], current_laser[Y_DIR])
                    continue
                elif block_encounter == EMPTY:
                    current_laser = (current_laser[X_POS] + current_laser[X_DIR], current_laser[Y_POS] +
                    current_laser[Y_DIR], current_laser[X_DIR], current_laser[Y_DIR])
                elif block_encounter == OPAQUE:
                    laser_queue.pop(0)
                    break
                # assign the different condition of directions change when lazor meets different blocks

            laser_history.append((current_laser[X_POS], current_laser[Y_POS]))
            self.laser_history.append(laser_history)
        if(len(goals) == 0):
            print("Solution found!")
            lazor.draw()
            self.reset()
            return True
        self.reset()
        return False
        # print the Solution found if success, reset the lists if fail to meet the requirement.

    def set_reflect(self, position):
        '''
        This function is used to determine the position of the reflect blocks.
        '''
        if position in self.available_block and self.reflect_block_count < self.original_reflect_block_count:
            self.available_block.remove(position)
            self.reflect_block.append(position)
            self.reflect_block_count += 1
        else:
            print("Position not available! Reset")
            self.reset()

    def set_refract(self, position):
        '''
        This function is used to determine the position of the refract blocks.
        '''
        if position in self.available_block and self.refract_block_count < self.original_refract_block_count:
            self.available_block.remove(position)
            self.refract_block.append(position)
            self.refract_block_count += 1
        else:
            print("Position not available! Reset")
            self.reset()

    def set_opaque(self, position):
        '''
        This function is used to determine the position of the opaque blocks.
        '''
        if position in self.available_block and self.opaque_block_count < self.original_opaque_block_count:
            self.available_block.remove(position)
            self.opaque_block.append(position)
            self.opaque_block_count += 1
        else:
            print("Position not available! Reset")
            self.reset()

    def auto_solve(self):
        '''
        This function is used to create a function to calculate the time
        used to solve the game,
        and calculate the attemts to solve the laser path of the game.
        '''
        not_solved = True
        start = time.time()
        # calculate the time used
        counter = 0
        while not_solved:
            for i in range(self.original_reflect_block_count):
                self.set_reflect(random.choice(self.available_block))
            for i in range(self.original_refract_block_count):
                self.set_refract(random.choice(self.available_block))
            for i in range(self.original_opaque_block_count):
                self.set_opaque(random.choice(self.available_block))

            not_solved = not self.start_game()
            counter += 1
        finish = time.time()
        print("Solved in " + str(finish - start) + "s")
        print("Tried " + str(counter) + " times")

if __name__ == '__main__':
    lazor = Lazor()
    lazor.generate_from_bff("yarn_5.bff")
    lazor.auto_solve()
