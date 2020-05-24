# Codingame Spring Challenge 2020 solution
Spring challenge 2020 competition hosted by [codingame](http://codingame.com).

General approach to solving the challenge is to separate the logic into two distinct parts, one Maze and the other is the Pac.


Maze is responsible for providing operations and methods for optimum path calculation by 
implementing a graph over the 2-D grid. It implements a greedy-edge traversal algorithm to
calculate the path for the best immediate edge in the graph from the current node.


Pac is responsible for following a command from Maze while averting danger from enemy Pacs.
It implements a policy for when enemy Pacs are in the vicinity and methods to traverse over
a given travel queue.
