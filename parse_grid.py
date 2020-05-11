import sys
import time


def p(*args, **kwargs):
    return print(*args, **kwargs, file=sys.stderr)


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
    def __init__(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.l = None
        self.r = None
        self.u = None
        self.d = None

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __eq__(self, other):
        return self.id == other.id


class Edge:
    def __init__(self, node, dir):
        self.node1 = node
        self.dir1 = dir
        self.node2 = None
        self.dir2 = None
        self.path = list()


class Maze:
    def __init__(self, w, h, floor_plan):
        self.w = w
        self.h = h
        self.floor_plan = floor_plan
        self.dirs = ['l', 'd', 'r', 'u']
        self.node_count = 0
        self.nodes = dict()

    @staticmethod
    def inverse_dir(dir):
        inverse_dict = {
            'l': 'r',
            'r': 'l',
            'u': 'd',
            'd': 'u'
        }
        return inverse_dict[dir]

    def is_floor(self, x, y):
        return self.floor_plan[(x, y)] == ' '

    def get_coord(self, x, y, dir):

        if dir == 'l':
            if x == 0:
                return x + self.w - 1, y  # Wrap around the left edge
            else:
                return x - 1, y

        elif dir == 'r':
            if x == self.w - 1:
                return 0, y  # Wrap around the right edge
            else:
                return x + 1, y

        elif dir == 'u':
            if y == 0:
                return x, y  # If at upper edge, return current position
            else:
                return x, y - 1

        elif dir == 'd':
            if y == self.h - 1:
                return x, y  # If at bottom edge, return current position
            else:
                return x, y + 1
        else:
            p(f'Invalid direction: {dir}')

    def check_way(self, x, y, dir):
        return self.is_floor(*self.get_coord(x, y, dir))

    def conn_count(self, x, y):
        if not self.is_floor(x, y):
            return 0

        count = 0
        for dir in self.dirs:
            if self.check_way(x, y, dir):
                count += 1
        return count

    def get_available_dirs(self, x, y):
        available_dirs = list()
        for dir in self.dirs:
            if self.check_way(x, y, dir):
                available_dirs.append(dir)
        return available_dirs

    def construct_nodes(self):
        for y in range(self.h):
            for x in range(self.w):
                if self.is_floor(x, y):
                    if self.conn_count(x, y) == 1:
                        # Create terminal node
                        self.nodes[(x, y)] = Node(self.node_count, x, y, 'terminal')

                        p(f"Constructing node at ({x}, {y})")

                        self.node_count += 1
                    elif self.conn_count(x, y) > 2:
                        # Create joint node
                        self.nodes[(x, y)] = Node(self.node_count, x, y, 'joint')

                        p(f"Constructing node at ({x}, {y})")

                        self.node_count += 1

    def traverse(self, node, dir):
        # Returns Edge object connecting `node` to a new node found by traversing along the `dir` direction

        # New Edge creation
        e = Edge(node, dir)

        # Attach this Edge to the current Node's `dir`
        node[dir] = e

        x, y = node.x, node.y
        available_dirs = self.get_available_dirs(x, y)

        # Traverse till we find the next node
        this_dir = dir
        while True:
            # Get new x and y
            new_x, new_y = self.get_coord(x, y, this_dir)

            # If new x, y have a node, update Edge, new node, and break
            if self.nodes.get((new_x, new_y)) is not None:
                other_node = self.nodes.get((new_x, new_y))
                e.path.append((new_x, new_y))

                # Update edge
                e.node2 = other_node
                e.dir2 = self.inverse_dir(this_dir)

                # Update the other node for this new Edge connection
                other_node[self.inverse_dir(this_dir)] = e

                break

            # Append new x, y to path, update x, y
            e.path.append((new_x, new_y))
            # TODO: Update other edge attributes like distance and pellets

            x, y = new_x, new_y

            # Choose dir
            available_dirs = self.get_available_dirs(x, y)
            if this_dir in available_dirs:
                continue
            else:
                new_dir_candidates = list(set(available_dirs) - set(self.inverse_dir(this_dir)))
                this_dir = new_dir_candidates[0]

        p(f"Constructing edge from ({e.node1.x},{e.node1.y}) to ({e.node2.x},{e.node2.y})")

        return

    def construct_edges(self):
        # Loop over all nodes and connect them to Edge objects
        for key in self.nodes:
            x, y = key
            node = self.nodes.get(key)
            traversible_dirs = [dir for dir in self.dirs  # l, r, u, d
                                if self.check_way(x, y, dir)  # Only directions without wall
                                and node[dir] is None]  # Only directions not assigned an Edge yet

            for dir in traversible_dirs:
                self.traverse(node, dir)
        return


if __name__ == '__main__':
    width, height = [int(i) for i in input().split()]
    m = Map(width, height)
    m.read_map()
    t0 = time.time()
    m.parse()
    maze = Maze(width, height, m.floor_plan)
    maze.construct_nodes()
    maze.construct_edges()
    p(f'Time taken: {round(time.time() - t0, 5)}s')



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
