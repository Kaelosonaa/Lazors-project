import numpy as np
import time
import random
class Lazor_class(object):
    def __init__(self, initial_pos, direction):
        self.initial_pos = initial_pos
        self.direction = direction
    def intersect_pts_remaining(self, grid, intersect_points):
        self.intersect_points = intersect_points
        lazor_moves = self.lazor_data(grid)[1]
        intersect_pts_notcrossed = []
        for k in intersect_points:
            if k not in lazor_moves:
                intersect_pts_notcrossed.append(k)
        return intersect_pts_notcrossed
    def lazor_data(self, grid):
        lazor_pos = self.initial_pos
        direction = self.direction
        block_intersect = []
        lazor_moves = []
        lazor_moves.append(self.initial_pos)
        def in_array(lazor_pos, direction):
            lazor_pos_x = lazor_pos[0] + direction[0]
            lazor_pos_y = lazor_pos[1] + direction[1]
            grid_x_len = len(grid[0])
            grid_y_len = len(grid)
            return (lazor_pos_x >= 0 and lazor_pos_x < grid_x_len and
                    lazor_pos_y >= 0 and lazor_pos_y < grid_y_len)
        def block_new(lazor_pos, direction):
            x_0, y_0 = lazor_pos
            x_1 = lazor_pos[0] + direction[0]
            y_1 = lazor_pos[1] + direction[1]
            x_1y_0 = x_1 % 2 + y_0 % 2
            x_0y_1 = x_0 % 2 + y_1 % 2
            if x_1y_0 != 0:
                block_1 = (x_1, y_0)
            elif x_0y_1 != 0:
                block_1 = (x_0, y_1)
            else:
                return False
            return block_1
        def reflect_block(lazor_pos, direction, block_next):
            reflect_x = block_next[0] - lazor_pos[0]
            reflect_y = block_next[1] - lazor_pos[1]
            reflect_x_scale = 2 * reflect_x
            reflect_y_scale = 2 * reflect_y
            direction = (direction[0] - reflect_x_scale,
                         direction[1] - reflect_y_scale)
            return direction
        def refract_block(lazor_pos, direction, block_next):
            initial_pos_new = (lazor_pos[0] + direction[0],
                               lazor_pos[1] + direction[1])
            lazor_split = Lazor_class(initial_pos_new, direction)
            lazor_moves_split = lazor_split.lazor_data(grid)
            for i in lazor_moves_split[0]:
                block_intersect.append(i)
            for i in lazor_moves_split[1]:
                lazor_moves.append(i)
            direction = reflect_block(lazor_pos, direction, block_next)
            return direction
        while in_array(lazor_pos, direction):
            block_next = block_new(lazor_pos, direction)
            block_next_type = grid[block_next[1]][block_next[0]]
            if block_next_type == 'A':
                direction = reflect_block(lazor_pos, direction, block_next)
            elif block_next_type == 'C':
                direction = refract_block(lazor_pos, direction, block_next)
            elif block_next_type == 'B':
                return block_intersect, lazor_moves
            elif block_next_type == 'o':
                block_intersect.append(block_next)
            lazor_pos = (lazor_pos[0] + direction[0],
                         lazor_pos[1] + direction[1])
            lazor_moves.append(lazor_pos)
        return block_intersect, lazor_moves
def solution_check(lazors, grid, intersect_points):
    for each_lazor in lazors:
        intersect_points = each_lazor.intersect_pts_remaining(
            grid, intersect_points)
    if len(intersect_points) == 0:
        return True
    else:
        return False
def read_input_file(board):
    block_count = {'A': 0,
                   'B': 0,
                   'C': 0}
    block_count_names = ['A', 'B', 'C']
    lazor_list_read = []
    intersect_points = []

    board_open = open(board, 'r')
    board_open = board_open.readlines()
    board_open = [line.replace('\n', '')
                  for line in board_open if line != '\n']
    for number, line in enumerate(board_open):
        if "START" in line:
           grid_start = number
        if "STOP" in line:
           grid_end = number
           grid_text = [line.replace(' ', '')
                 for line in board_open[grid_start + 1:grid_end]]
           print(grid_text)
    
  
    
    #grid_start = board_open.index('GRID START')
    #grid_end = board_open.index("GRID STOP")
    #grid_text = [line.replace(' ', '')
                 #for line in board_open[grid_start + 1:grid_end]]

    grid_x_len = len(grid_text[0])
    print(grid_x_len)
    grid_y_len = len(grid_text)
    print(grid_y_len)
    grid_x_len = grid_x_len * 2 + 1
    grid_y_len = grid_y_len * 2 + 1
    grid = [[0] * grid_x_len] * grid_y_len
    print(grid)
    o_locations = []
    grid_text_y = 1
    for line in grid_text:
        grid_text_x = 1
        grid_line = [0]
        for letter in line:
            if letter == 'o':
                o_locations.append((grid_text_x, grid_text_y))
            grid_line.append(letter)
            grid_line.append(0)
            grid_text_x = grid_text_x + 2
        grid[grid_text_y] = grid_line
        grid_text_y = grid_text_y + 2

    for line in board_open[grid_end:]:
        if not line[0] in block_count_names:
            if line[0] == 'L':
                lazor_list_read.append(
                    [tuple(map(int, line.replace('L', '').split()[s:s + 2]))
                     for s in [0, 2]])
            elif line[0] == 'P':
                intersect_points.append(
                    tuple(map(int, line.replace('P', '').split())))
        if line[0] in block_count_names:
            block_count[line[0]] = int(line[2])

    lazors = []
    for lazor_index in lazor_list_read:
        lazors.append(Lazor_class(lazor_index[0], lazor_index[1]))
  
    return (grid, block_count, intersect_points, lazors, o_locations)
def board_solver_process(board):
    t1 = time.time()
    board_name = str(board)
    board_name = board_name.replace('.bff', '')
    (grid, block_count, intersect_points, lazors,
        o_locations) = read_input_file(board)
    block_list = []
    for b in block_count:
        if b == 'A':
            for ai in range(block_count.get('A')):
                block_list.append('A')
        elif b == 'C':
            for ai in range(block_count.get('C')):
                block_list.append('C')
        elif b == 'B':
            for ai in range(block_count.get('B')):
                block_list.append('B')
    unsolved = True
    iterations = 1
    while unsolved:
        i = random.sample(o_locations, len(block_list))
        for j in range(len(block_list)):
            block_xy = i[j]
            i_x = block_xy[0]
            i_y = block_xy[1]
            grid[i_y][i_x] = block_list[j]
        solve = solution_check(lazors, grid, intersect_points)
        if solve:
            print("Grid Solution")
            print(np.matrix(grid))
            t2 = time.time()
            print('Iterations = %s' % iterations)
            time_elapsed = t2 - t1
            print('Time Elapsed = %s s' % time_elapsed)
            print("Solution saved as txt file")
            board_solution = board_name + "solution.txt"
            f = open(board_solution, 'w')
            solution_grid = []
            for y in range(1, len(grid), 2):
                for x in grid[y]:
                    if x == 0:
                        grid[y].remove(x)
                solution_grid.append(' '.join(grid[y]))
            solution_grid = '\n'.join(solution_grid)
            f.write(solution_grid)
            f.close()
            return
        for j in range(len(block_list)):
            block_xy = i[j]
            i_x = block_xy[0]
            i_y = block_xy[1]
            grid[i_y][i_x] = 'o'
        iterations = iterations + 1
if __name__ == '__main__':
    board_solver_process("mad_1.bff")
