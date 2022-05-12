import random
import copy

"""
1: start with the entire dungeon area (root node of the BSP tree)
2: divide the area along a horizontal or vertical line
3: select one of the two new partition cells
4: if this cell is bigger than the minimal acceptable size:
5: go to step 2 (using this cell as the area to be divided)
6: select the other partition cell, and go to step 4
7: for every partition cell:
8: create a room within the cell by randomly choosing two points (top left and bottom right) within its boundaries
9: starting from the lowest layers, draw corridors to connect rooms corresponding to children of the same parent in the BSP tree
10:repeat 9 until the children of the root node are connected
"""

def BSP(x_start, x_end, y_start, y_end):
    # Recursion base case
    if (x_end - x_start <= 0) or (y_end - y_start <= 0):
        # Left child is None, right is -1.
        # This will be useful when assigning numbers to the areas.
        leaf_node = Node(None, -1, x_start, x_end, y_start, y_end)
        return leaf_node
    # Any other case
    else:
        # Randomly pick between horizontal or vertical partition
        horiz_or_vert = random.choice([0, 1])
        # Horizontal
        if horiz_or_vert == 0:
            start = y_start
            end = y_end
        # Vertical
        else:
            start = x_start
            end = x_end
        
        # If the size after the split is smaller than the minimum size, 
        # simply divide the area in 2 equal parts.
        if end-start > 1:
            split = random.choice(range(start, end))
        else:
            split = start

        # Recursively make the partitions.
        if horiz_or_vert == 0:
            left = BSP(x_start, x_end, start, split)
            right = BSP(x_start, x_end, split+1, end)
        else:
            left = BSP(start, split, y_start, y_end)
            right = BSP(split+1, end, y_start, y_end)

        node = Node(left, right, x_start, x_end, y_start, y_end)
        return node

area_counter = 0
def write_file(node):
    global area_counter
    # At every node, iterate through the two left and right children.
    for child in node.children:
        # Check if we are at a leaf node
        # if yes...
        # left child
        if child == None:
            # Because our minimum size is of width 1, there will be one side (x or y)
            # that will have size of 1. Thus, we can't use the "range()" function, but
            # we instead keep that number constant when accessing the maze list.
            if node.x_start == node.x_end:
                for pixel_row in range(node.y_start, node.y_end+1):
                    if node.left is None:
                        maze[pixel_row][node.x_start] = str(area_counter) + " "
            elif node.y_start == node.y_end:
                for pixel_column in range(node.x_start, node.x_end+1):
                    if node.left is None:
                        maze[node.y_start][pixel_column] = str(area_counter) + " "
            else:
                for pixel_row in range(node.y_start, node.y_end+1):
                    for pixel_column in range(node.x_start, node.x_end+1):
                        if node.left is None:
                            maze[pixel_row][pixel_column] = str(area_counter) + " "
            area_counter += 1
            continue
        # right child
        elif child == -1:
            continue
        # if no... recurse on the children
        else:
            write_file(child)

            
    # Create the connection between the rooms.
    # If we are not on the leaf node...
    if not node.left is None:
        # determine whether the split was horizontal or vertical.
        connection_sign = ""
        if node.left.x_start == node.right.x_start and node.left.x_end == node.right.x_end:
            # horizontal
            # Pick a random number between start and end
            bridge_x = random.choice(range(node.left.x_start, node.left.x_end+1))
            bridge_y = node.left.y_end
            connection_sign = "|"
        else:
            # vertical
            bridge_x = node.left.x_end
            bridge_y = random.choice(range(node.left.y_start, node.left.y_end+1))
            connection_sign = "-"
        # Add the connection symbol to the chosen connection point
        old_sign = maze[bridge_y][bridge_x]
        old_sign = old_sign.split()[0]
        old_sign = old_sign + connection_sign
        maze[bridge_y][bridge_x] = old_sign


class Node(object):
    def __init__(self, left, right, x_start, x_end, y_start, y_end):
        self.left = left
        self.right = right
        self.children = [left, right]
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end

# Alternative printing function for 
# a better visualization of the maze.
def print2(maze):
    for row in maze:
        print("".join(row))


# x = (0,28,0,36)

maze = []
maze_row = []
# for x in range(29):
#     maze_row.append("X")
# for y in range(37):
#     maze.append(maze_row)
    
# root_node = BSP(0,28,0,36)

for x in range(10):
    maze_row.append("X")
for y in range(10):
    maze.append(copy.copy(maze_row))
    
root_node = BSP(0,9,0,9)

write_file(root_node)
print2(maze)