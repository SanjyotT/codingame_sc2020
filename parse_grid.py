import sys
import time
import math
import random

def p(*args, **kwargs):
    return print(*args, **kwargs, file=sys.stderr)


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


class Game:
    def __init__(self):
        self.my_score = 0
        self.opponent_score = 0
        self.visible_pac_count = 0
        self.visible_pellet_count = 0


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
    def __init__(self, id, node, dir):
        self.id = id
        self.node1 = node
        self.dir1 = dir
        self.node2 = None
        self.dir2 = None
        self.path = list()
        self.length = 0
        self.pellets = 0


class Maze:
    def __init__(self, w, h, floor_plan):
        self.w = w
        self.h = h
        self.floor_plan = floor_plan
        self.dirs = ['l', 'd', 'r', 'u']
        self.node_count = 0
        self.edge_count = 0
        self.nodes = dict()  # (x, y) -> Node()
        self.edges = dict()  # edge_id -> Edge()
        self.pellet_dict = dict()  # (x, y) -> pellet value
        self.total_pellets = 0

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

                        # p(f"Constructing node at ({x}, {y})")

                        self.node_count += 1
                    elif self.conn_count(x, y) > 2:
                        # Create joint node
                        self.nodes[(x, y)] = Node(self.node_count, x, y, 'joint')

                        # p(f"Constructing node at ({x}, {y})")

                        self.node_count += 1

    def _create_edge(self, node, dir):
        # Creates Edge object connecting `node` to a new node found by traversing along the `dir` direction
        # Stores the Edge in self.edges

        # New Edge creation
        e = Edge(self.edge_count, node, dir)
        self.edges[self.edge_count] = e
        self.edge_count += 1

        # Attach this Edge to the current Node's `dir`
        node[dir] = e

        x, y = node.x, node.y

        # Traverse till we find the next node
        this_dir = dir
        while True:
            # Get new x and y
            new_x, new_y = self.get_coord(x, y, this_dir)

            # If new x, y have a node, update Edge, new node, and break
            if self.nodes.get((new_x, new_y)) is not None:
                other_node = self.nodes.get((new_x, new_y))

                # Update edge
                e.path.append((new_x, new_y))
                e.node2 = other_node
                e.dir2 = self.inverse_dir(this_dir)
                e.length = len(e.path)

                # Update the other node for this new Edge connection
                other_node[self.inverse_dir(this_dir)] = e
                break

            # Append new x, y to path, update x, y
            e.path.append((new_x, new_y))

            x, y = new_x, new_y

            # Choose dir
            available_dirs = self.get_available_dirs(x, y)
            if this_dir in available_dirs:
                continue
            else:
                new_dir_candidates = list(set(available_dirs) - set(self.inverse_dir(this_dir)))
                this_dir = new_dir_candidates[0]

        # p(f"Constructing edge from ({e.node1.x},{e.node1.y}) to ({e.node2.x},{e.node2.y})")

    def construct_edges(self):
        # Loop over all nodes and connect them to Edge objects
        for key in self.nodes:
            x, y = key
            node = self.nodes.get(key)
            traversible_dirs = [dir for dir in self.dirs  # l, r, u, d
                                if self.check_way(x, y, dir)  # Only directions without wall
                                and node[dir] is None]  # Only directions not assigned an Edge yet

            for dir in traversible_dirs:
                self._create_edge(node, dir)
        return

    def update_pellet_values(self):
        self.total_pellets = 0
        for edge_id in self.edges:
            e = self.edges[edge_id]
            pellets = 0
            for point in e.path:
                try:
                    pellets += self.pellet_dict[point]
                    self.total_pellets += self.pellet_dict[point]
                except KeyError:
                    # p(f"Keyerror for pellet value update for {point}")
                    pass
            e.pellets = pellets


class Pac:
    def __init__(self, id, x, y, type_id, speed_turns_left, ability_cooldown):
        self.id = id
        self.x = x
        self.y = y
        self.type_id = type_id
        self.speed_turns_left = speed_turns_left
        self.ability_cooldown = ability_cooldown
        self.current_dest = None
        self.travel_queue = list()

    def move(self, x, y):
        print(f'MOVE {self.id} {x} {y}')

    def stay(self):
        self.move(self.x, self.y)

    def default_move_to_dest(self):
        if self.current_dest is None:
            self.stay()

        if (self.x, self.y) == self.current_dest:
            self.current_dest = None
            self.stay()

        else:
            self.move(self.current_dest[0], self.current_dest[1])

    def move_on_travel_queue(self):
        if not self.travel_queue:
            self.stay()
        else:
            try:
                current_index = self.travel_queue.index((self.x, self.y))
            except ValueError:
                # This means travel queue starts from the point just next to current node, hence current index -1
                current_index = -1

            if current_index == len(self.travel_queue) - 1:
                self.travel_queue = []
                self.stay()
            else:
                self.move(*self.travel_queue[current_index + 1])


class Controller:

    def __init__(self):
        pass

    @staticmethod
    def move_pac_to_closest_node(pac, maze):
        pac_loc = (pac.x, pac.y)
        closest_node = None

        # Only go to the closest joint node, and not terminal nodes
        joint_nodes = [(maze.nodes[n].x, maze.nodes[n].y) for n in maze.nodes if maze.nodes[n].type == 'joint']

        # Check if `pac` is already on a joint node
        if pac_loc in joint_nodes:
            closest_node = maze.nodes[pac_loc]
            return

        # Otherwise check which edge the `pac` is on
        else:
            for edge_id, e in maze.edges.items():
                if pac_loc in e.path:
                    if e.node1.type == 'terminal':
                        # If one node is terminal, move towards other (which will be joint)
                        closest_node = e.node2
                    elif e.node2.type == 'terminal':
                        # If one node is terminal, move towards other (which will be joint)
                        closest_node = e.node1
                    elif e.path.index(pac_loc) < math.floor(len(e.path) / 2.0):
                        # Closest node is on the half side of the edge the pac is in
                        closest_node = e.node1
                    else:
                        # Closest node is on the half side of the edge the pac is in
                        closest_node = e.node2
                    break
        pac.current_dest = (closest_node.x, closest_node.y)
        pac.default_move_to_dest()
        p(f"Moving pac {pac.id} to closest joint node: ({closest_node.x}, {closest_node.y})")

    def greedy_edge_traverse(self, pac, maze):

        # If Pac not at a node, move to closest node
        pac_loc = (pac.x, pac.y)

        p(f'Pac at ({pac.x}, {pac.y})')

        if pac_loc not in maze.nodes:

            p(f'Pac not at a node')

            if not pac.travel_queue:

                p(f'Pac travel queue empty so moving to closest joint node')

                self.move_pac_to_closest_node(pac, maze)
            else:

                p(f'Pac continues on travel queue')

                pac.move_on_travel_queue()
        else:

            # Calculate edge with highest pellet rate for the current node
            node = maze.nodes[pac_loc]

            p(f'Pac at Node({node.x}, {node.y})')

            edges = [node[d] for d in maze.dirs if node[d] is not None]
            pellets_in_edges = [edge.pellets for edge in edges]

            # If all edges have zero pellets, get random point with a pellet and move to it
            if sum(pellets_in_edges) == 0:
                best_edge = random.choice(edges)
                p(f'All side edges have 0 pellets. Moving to random edge')

            else:
                best_edge = max(edges, key=lambda x: float(x.pellets))

            p(f'Pac best edge: ({best_edge.node1.x}, {best_edge.node1.y}) -> ({best_edge.node2.x}, {best_edge.node2.y})')

            if best_edge.node1 == node:
                travel_queue = best_edge.path
            else:
                travel_queue = list(reversed(best_edge.path))
                travel_queue.append((best_edge.node1.x, best_edge.node1.y))  # To construct queue till next node

            p(f'New travel queue: {travel_queue}')

            pac.travel_queue = travel_queue
            pac.move_on_travel_queue()


def game_loop_pac_update(visible_pac_count, my_pacs, en_pacs):
    for i in range(visible_pac_count):
        pac_id, mine, x, y, type_id, speed_turns_left, ability_cooldown = input().split()
        pac_id, mine, x, y = map(int, (pac_id, mine, x, y))
        mine = mine == 1
        if mine:
            # My pac
            if pac_id not in my_pacs:
                my_pacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown)
            else:
                # Pac in my pacs
                this_pac = my_pacs[pac_id]
                this_pac.x = x
                this_pac.y = y
                this_pac.speed_turns_left = speed_turns_left
                this_pac.ability_cooldown = ability_cooldown
        else:
            # Enemy pac
            if pac_id not in en_pacs:
                en_pacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown)
            else:
                # Pac in enemy pacs
                this_pac = en_pacs[pac_id]
                this_pac.x = x
                this_pac.y = y
                this_pac.speed_turns_left = speed_turns_left
                this_pac.ability_cooldown = ability_cooldown

    return my_pacs, en_pacs


def game_loop_pellet_update(visible_pellet_count):
    pellet_dict = dict()
    for i in range(visible_pellet_count):
        x, y, value = [int(j) for j in input().split()]
        pellet_dict[(x, y)] = value
    return pellet_dict


def game_loop_update(turn_id, game, maze, my_pacs, en_pacs):
    my_score, opponent_score = [int(i) for i in input().split()]
    visible_pac_count = int(input())  # all your pacs and enemy pacs in sight

    game.my_score = my_score
    game.opponent_score = opponent_score
    game.visible_pac_count = visible_pac_count

    my_pacs, en_pacs = game_loop_pac_update(visible_pac_count, my_pacs, en_pacs)

    visible_pellet_count = int(input())  # all pellets in sight
    game.visible_pellet_count = visible_pellet_count

    pellet_dict = game_loop_pellet_update(visible_pellet_count)
    if turn_id == 0:
        maze.pellet_dict = pellet_dict
    else:
        orig_pellet_dict = maze.pellet_dict
        missing_points = list(set(orig_pellet_dict.keys()) - set(pellet_dict.keys()))
        for point in missing_points:
            orig_pellet_dict[point] = 0
        maze.pellet_dict = orig_pellet_dict

    return game, maze, my_pacs, en_pacs


if __name__ == '__main__':
    width, height = [int(i) for i in input().split()]
    m = Map(width, height)
    m.read_map()
    m.parse()
    maze = Maze(width, height, m.floor_plan)
    maze.construct_nodes()
    maze.construct_edges()

    game = Game()
    con = Controller()
    my_pacs = dict()
    en_pacs = dict()

    initial_pellets = 0
    # game loop
    turn_id = 0
    while True:
        t0 = time.time()
        # Update all game stats
        game, maze, my_pacs, en_pacs = game_loop_update(turn_id, game, maze, my_pacs, en_pacs)
        maze.update_pellet_values()

        # TODO: Implement multi-edge greedy traverse

        for pac_id, pac in my_pacs.items():
            con.greedy_edge_traverse(pac, maze)

        # MOVE <pacId> <x> <y>
        # print("MOVE 0 15 10")

        turn_id += 1
