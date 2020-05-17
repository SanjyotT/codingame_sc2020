import sys
import time
import math
import random


def p(*args, **kwargs):
    return print(*args, **kwargs, file=sys.stderr)


class Commander:
    def __init__(self):
        self.command_queue = list()

    def add_command(self, command):
        self.command_queue.append(command)  # Command is MOVE string for one pac

    def publish(self):
        publish_str = ' | '.join([x.strip() for x in self.command_queue])
        print(publish_str)
        self.command_queue = list()


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
    def __init__(self,):
        self.w, self.h = [int(i) for i in input().split()]
        self.floor_plan = self.parse_map()
        self.dirs = ['l', 'd', 'r', 'u']
        self.node_count = 0
        self.edge_count = 0
        self.nodes = dict()  # (x, y) -> Node()
        self.edges = dict()  # edge_id -> Edge()
        self.pellet_dict = dict()  # (x, y) -> pellet value
        self.total_pellets = 0

    def parse_map(self):
        # Read in the inputs and store it line-by-line
        rows = list()
        for i in range(self.h):
            rows.append(input())

        floor_plan = dict()
        for y in range(self.h):
            for x in range(self.w):
                floor_plan[(x, y)] = rows[y][x]

        return floor_plan

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
                        self.node_count += 1
                    elif self.conn_count(x, y) > 2:
                        # Create joint node
                        self.nodes[(x, y)] = Node(self.node_count, x, y, 'joint')
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

        # Attach the (x, y) of current node as first point in the edge path
        x, y = node.x, node.y
        e.path.append((x, y))

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

    def get_visible_cells(self, x, y):
        # Get visible cells from (x, y) in maze
        visible_cells = list()
        visible_cells.append((x, y))

        for dir in self.get_available_dirs(x, y):
            x0, y0 = x, y
            while self.check_way(x0, y0, dir):
                x0, y0 = self.get_coord(x0, y0, dir)
                visible_cells.append((x0, y0))
        return visible_cells

    def get_diagonal_cells(self, x, y):
        p1 = self.get_coord(*self.get_coord(x, y, 'r'), 'u')  # Right Up
        p2 = self.get_coord(*self.get_coord(x, y, 'l'), 'u')  # Left Up
        p3 = self.get_coord(*self.get_coord(x, y, 'r'), 'd')  # Right Down
        p4 = self.get_coord(*self.get_coord(x, y, 'l'), 'd')  # Left Down
        points = [p for p in [p1, p2, p3, p4] if self.is_floor(*p)]
        return points

    def update_pellet_map(self, turn_id, visible_pellet_dict, my_pacs):

        if turn_id == 0:
            # Assume all floor cells have pellets
            pellet_dict = {cell: 1 for cell, value in self.floor_plan.items() if value == ' '}  # Cell is (x, y) tuple

            # Update superpellets from `visible_pellet_dict`
            super_pellets = {cell: value for cell, value in visible_pellet_dict.items() if value > 1}
            pellet_dict.update(super_pellets)
            self.pellet_dict = pellet_dict

        else:
            # Get set of all cells visible to all pacs and subtract the cells in which you saw a pellet
            # Resulting set of points don't have any pellets. Update these points in the pellet map

            all_visible_cells = set()
            for _, pac in my_pacs.items():
                all_visible_cells = all_visible_cells.union(set(maze.get_visible_cells(pac.x, pac.y)))

            visible_pellet_cells = set([cell for cell, value in visible_pellet_dict.items()])

            no_pellet_cells = all_visible_cells - visible_pellet_cells
            no_pellet_dict = {cell: 0 for cell in no_pellet_cells}

            curr_pellet_dict = self.pellet_dict
            curr_pellet_dict.update(no_pellet_dict)
            self.pellet_dict = curr_pellet_dict


class Pac:
    def __init__(self, id, x, y, type_id, speed_turns_left, ability_cooldown, maze):
        self.id = id
        self.x = x
        self.y = y
        self.type_id = type_id
        self.speed_turns_left = speed_turns_left
        self.ability_cooldown = ability_cooldown
        self.maze = maze
        self.my_pacs = None
        self.en_pacs = None

        self.current_dest = None
        self.travel_queue = list()
        self.decision_recursion_limit = 3
        self.decision_counter = 0
        self.stronger_type = {'ROCK': 'PAPER', 'PAPER': 'SCISSORS', 'SCISSORS': 'ROCK'}
        self.accepting_commands = True  # This is turned False when Pac is on kill mode in a terminal edge

    def _move(self, x, y):
        return f'MOVE {self.id} {x} {y}'

    def _speed(self):
        return f'SPEED {self.id}'

    def _switch(self, type):
        return f'SWITCH {self.id} {type.upper()}'

    def stay(self):
        self._move(self.x, self.y)

    def distance(self, x, y):
        return abs(self.x - x) + abs(self.y - y)

    def get_next_cell(self):
        current_index = self.travel_queue.index((self.x, self.y))

        # If already at destination, stay at same location (also become receptive to commands)
        if current_index == len(self.travel_queue) - 1:
            self.accepting_commands = True
            return self.travel_queue[current_index]

        # Move forward
        else:
            return self.travel_queue[current_index + 1]

    def set_travel_queue(self, queue):
        if self.accepting_commands:
            self.travel_queue = queue

    def reverse_travel_queue(self):
        self.travel_queue = list(reversed(self.travel_queue))

    def follow_travel_queue(self):

        if not self.travel_queue:
            self.stay()
        else:
            self._move(self.get_next_cell())

    def enemy_routine(self, en_pacs):
        """ Decide what to do if an enemy is in 2 distance vicinity """

        # If surrounded by more than 2 enemy pacs, stay
        # WIP: Write a better approach
        if len(en_pacs) > 1:
            self.stay()

        en_pac, en_dist = list(en_pacs.keys())[0], list(en_pacs.values())[0]

        # Calculate some decision variables used in logic
        joint_node_cells = [cell for cell, node in self.maze.nodes.items() if node.type == 'joint']

        on_edge = True if (self.x, self.y) not in self.maze.nodes else False


        current_edge = None
        on_terminal_edge = None
        on_joint_node = None

        if on_edge:
            for _, e in self.maze.edges:
                if (self.x, self.y) in e.path:
                    current_edge = e
                    break

            n1, n2 = current_edge.node1, current_edge.node2
            if 'terminal' in [n1.type, n2.type]:
                on_terminal_edge = True
            else:
                on_terminal_edge = False

        # Self on a node
        else:

            # Self on joint node
            if (self.x, self.y) in joint_node_cells:
                on_joint_node = True

            # Self on terminal node
            else:
                on_joint_node = False

        # At this point we have, `on_edge`, `on_terminal_edge`, `on_joint`, `current_edge`, `current_node`

        # If enemy is stronger
        if en_pac.type_id == self.stronger_type[self.type_id]:

            # If self in terminal edge or on terminal node
            if on_terminal_edge or (not on_edge and not on_joint_node):

                # If enemy pac on travel queue
                if (en_pac.x, en_pac.y) in self.travel_queue:

                    # If at terminal node
                    if not on_edge and not on_joint_node:

                        # If you can change to stronger type, change
                        if self.ability_cooldown == 0:
                            self._switch(self.stronger_type[en_pac.type_id])

                        # You are trapped and can do nothing. Wait for your doom.
                        else:
                            self.stay()

                    # If not at terminal node, reverse
                    else:
                        self.reverse_travel_queue()
                        self.follow_travel_queue()

                # else if enemy pac not on travel queue, follow travel queue
                else:
                    self.follow_travel_queue()

            # If on edge
            elif on_edge:

                # If enemy pac on travel queue, reverse
                if (en_pac.x, en_pac.y) in self.travel_queue:
                    self.reverse_travel_queue()
                    self.follow_travel_queue()

                # else if enemy pac not on travel queue, follow travel queue
                else:
                    self.follow_travel_queue()

            elif on_joint_node:
                # TODO: Handle in optimization, should not need to construct this case here
                pass

            else:
                p(f'Unknown scenario for Pac({self.x}, {self.y}) in enemy routine')
                self.stay()

        # If enemy is weaker
        else:

            # If enemy on edge
            if (en_pac.x, en_pac.y) not in self.maze.nodes:
                for _, e in self.maze.edges:
                    if (en_pac.x, en_pac.y) in e.path:
                        current_edge = e
                        break

                n1, n2 = current_edge.node1, current_edge.node2

                # If enemy on terminal edge
                if 'terminal' in [n1.type, n2.type]:

                    terminal_node = n1 if n1.type == 'terminal' else n2

                    # If enemy closer to terminal node, chase and kill
                    if self.distance(terminal_node.x, terminal_node.y) > en_pac.distance(terminal_node.x, terminal_node.y):
                        self.accepting_commands = False
                        self.travel_queue = current_edge.path if n2.type == 'terminal' else list(reversed(current_edge.path))
                        self.follow_travel_queue()

                    # If enemy not closer to terminal node
                    else:
                        self.follow_travel_queue()

                # If enemy not on terminal edge
                else:
                    self.follow_travel_queue()

            # If enemy on node
            else:
                self.follow_travel_queue()

    def play(self):
        """ Follows a mostly defensive strategy returning the next command """
        en_pac_close = dict()

        if self.en_pacs:
            en_pac_close = {
                pac: self.distance(pac.x, pac.y)
                for _, pac in self.en_pacs.items()
                if self.distance(pac.x, pac.y) <= 2
            }  # Get enemy Pacs and their distances from self if they are close

        diag_cells = self.maze.get_diagonal_cells(self.x, self.y)
        my_pacs_on_diags = [pac for _, pac in self.my_pacs.items() if (pac.x, pac.y) in diag_cells]

        # Enemy pac 1 or 2 distance away
        if en_pac_close:
            if min(en_pac_close.values()) == 2:
                if self.ability_cooldown == 0:
                    self._speed()
                else:
                    self.enemy_routine(en_pac_close)
            else:
                self.enemy_routine(en_pac_close)

        # Friendly pac on diagonal cell
        elif my_pacs_on_diags:
            if self.ability_cooldown == 0:
                self._speed()
            else:
                next_cells_diag_pacs = [pac.get_next_cell() for pac in my_pacs_on_diags]

                # If collision about to happen
                if self.get_next_cell() in next_cells_diag_pacs:

                    # If self id greater than all diag pacs, take right of way
                    if self.id > max([pac.id for pac in my_pacs_on_diags]):
                        self.follow_travel_queue()

                    # Otherwise let higher id pac pass and you stay
                    else:
                        self.stay()

                # If collision is not happening according to all pac travel queues
                else:
                    self.follow_travel_queue()

        # Normal operation, no pacs in vicinity
        else:
            if self.ability_cooldown == 0:
                self._speed()
            else:
                self.follow_travel_queue()


class Controller:

    def __init__(self):
        pass

    def move_pac_to_closest_node(self, pac, maze):
        pac_loc = (pac.x, pac.y)
        closest_node = None

        # Only go to the closest joint node, and not terminal nodes
        joint_nodes = [(maze.nodes[n].x, maze.nodes[n].y) for n in maze.nodes if maze.nodes[n].type == 'joint']

        # Check if `pac` is already on a joint node
        if pac_loc in joint_nodes:
            self.greedy_edge_traverse(pac, maze)

        # Otherwise check which edge the `pac` is on
        else:
            for edge_id, e in maze.edges.items():
                if pac_loc in e.path:
                    if e.node1.type == 'terminal':
                        # If one node is terminal, move towards other (which will be joint)
                        travel_queue = e.path
                    elif e.node2.type == 'terminal':
                        # If one node is terminal, move towards other (which will be joint)
                        travel_queue = list(reversed(e.path))
                    elif e.path.index(pac_loc) < math.floor(len(e.path) / 2.0):
                        # Closest node is on the half side of the edge the pac is in
                        travel_queue = list(reversed(e.path))
                    else:
                        # Closest node is on the half side of the edge the pac is in
                        travel_queue = e.path
                    break
        p(f'Pac({pac.x}, {pac.y}) travel queue: {travel_queue}')
        pac.travel_queue = travel_queue
        pac.follow_travel_queue()

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

                pac.follow_travel_queue()
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

            p(f'New travel queue: {travel_queue}')

            pac.travel_queue = travel_queue
            pac.follow_travel_queue()


def update(turn_id, maze):

    def pac_update(visible_pac_count, maze):
        my_pacs, en_pacs = dict(), dict()

        for i in range(visible_pac_count):
            pac_id, mine, x, y, type_id, speed_turns_left, ability_cooldown = input().split()
            pac_id, mine, x, y, speed_turns_left, ability_cooldown = \
                map(int, (pac_id, mine, x, y, speed_turns_left, ability_cooldown))

            mine = mine == 1
            if mine:
                # My pac
                my_pacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown, maze)
            else:
                # Enemy pac
                en_pacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown, maze)

        # Store all pac data inside each of my pac (Woah! A pac will have itself in an attribute)
        for _, my_pac in my_pacs.items():
            my_pac.my_pacs = my_pacs
            my_pac.en_pacs = en_pacs

        return my_pacs, en_pacs

    visible_pac_count = int(input())
    my_pacs, en_pacs = pac_update(visible_pac_count)  # all your pacs and enemy pacs in sight

    visible_pellet_count = int(input())
    visible_pellet_dict = dict()

    for i in range(visible_pellet_count):
        x, y, value = [int(j) for j in input().split()]
        visible_pellet_dict[(x, y)] = value

    maze.update_pellet_map(turn_id, visible_pellet_dict, my_pacs)

    return my_pacs, en_pacs


if __name__ == '__main__':
    maze = Maze()
    maze.construct_nodes()
    maze.construct_edges()

    c = Commander()  # For tracking and publishing final commands to stdout
    con = Controller()  # Game strategy maker

    # game loop
    turn_id = 0
    while True:
        # Update score
        my_score, opponent_score = [int(i) for i in input().split()]

        # Update all game stats
        my_pacs, en_pacs = update(turn_id, maze)  # Updates state for this turn and updates pellet map in `maze`


        # maze.update_pellet_values()
        #
        # for pac_id, pac in my_pacs.items():
        #     con.greedy_edge_traverse(pac, maze)
        #
        # c.publish()


        print('MOVE 0 17 5')


        turn_id += 1
