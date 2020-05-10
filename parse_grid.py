import sys
import time


def p(*args, **kwargs):
    return print(args, kwargs, file=sys.stderr)


# Define map object which stores x, y coordinate and if wall is present or floor
class Map:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.rows = list()
        self.floor_plan = dict()

    def read_map(self):
        # Read in the inputs and store it line-by-line
        for i in range(self.h):
            self.rows.append(input())

    def parse(self):
        for y in range(self.h):
            for x in range(self.w):
                self.floor_plan[(x, y)] = self.rows[y][x]

    def __str__(self):
        s = ''
        for r in self.rows:
            s += r + '\n'
        return s.strip('\n')


class Node:
    def __init__(self, x, y, id):
        self.id = id
        self.x = x
        self.y = y
        self.l = None
        self.r = None
        self.u = None
        self.d = None
        self.lpel = None
        self.rpel = None
        self.upel = None
        self.dpel = None


class Maze:
    def __init__(self, w, h, floor_plan):
        self.w = w
        self.h = h
        self.floor_plan = floor_plan
        self.node_plan = dict()
        self.dirs = ['left', 'down', 'right', 'up']

    def is_floor(self, x, y):
        return self.floor_plan[(x, y)] == ' '

    def check_way(self, x, y, dir):

        if dir == 'left':
            if x == 0:
                return self.is_floor(x + self.w - 1, y)
            else:
                return self.is_floor(x - 1, y)

        elif dir == 'right':
            if x == self.w - 1:
                return self.is_floor(0, y)
            else:
                return self.is_floor(x + 1, y)

        elif dir == 'up':
            if y == 0:
                return False
            else:
                return self.is_floor(x, y - 1)

        elif dir == 'down':
            if y == self.h - 1:
                return False
            else:
                return self.is_floor(x, y + 1)

        else:
            p(f'Invalid direction: {dir}')

    def conn_count(self, x, y):
        if not self.is_floor(x, y):
            return 0

        count = 0
        for dir in self.dirs:
            if self.check_way(x, y, dir):
                count += 1
        return count

    def construct(self):
        for y in range(self.h):
            for x in range(self.w):
                self.node_plan[(x, y)] = 0
                if self.is_floor(x, y):
                    if self.conn_count(x, y) > 2:
                        # Create node
                        self.node_plan[(x, y)] = 1
                        # TODO: Create terminal nodes

    # TODO: Node linking algorithm
    # TODO: Node traversal algorithm

    def print_nodes(self):
        for y in range(self.h):
            for x in range(self.w):
                print(self.node_plan[(x, y)], file=sys.stderr, end=' ')
            print('\n', file=sys.stderr, end=' ')


if __name__ == '__main__':
    width, height = [int(i) for i in input().split()]
    m = Map(width, height)
    m.read_map()
    t0 = time.time()
    m.parse()
    maze = Maze(width, height, m.floor_plan)
    maze.construct()
    print(f'Time taken: {round(time.time() - t0, 5)}s', file=sys.stderr)
    maze.print_nodes()



    #################################

    # game loop
    while True:
        my_score, opponent_score = [int(i) for i in input().split()]
        visible_pac_count = int(input())  # all your pacs and enemy pacs in sight
        for i in range(visible_pac_count):
            # pac_id: pac number (unique within a team)
            # mine: true if this pac is yours
            # x: position in the grid
            # y: position in the grid
            # type_id: unused in wood leagues
            # speed_turns_left: unused in wood leagues
            # ability_cooldown: unused in wood leagues
            pac_id, mine, x, y, type_id, speed_turns_left, ability_cooldown = input().split()
            pac_id = int(pac_id)
            mine = mine != "0"
            x = int(x)
            y = int(y)
            speed_turns_left = int(speed_turns_left)
            ability_cooldown = int(ability_cooldown)
        visible_pellet_count = int(input())  # all pellets in sight
        for i in range(visible_pellet_count):
            # value: amount of points this pellet is worth
            x, y, value = [int(j) for j in input().split()]

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # MOVE <pacId> <x> <y>
        print("MOVE 0 15 10")
