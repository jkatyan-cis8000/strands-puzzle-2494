"""
Spangram module for Strands puzzle game.
Provides spangram detection and validation.
"""

from typing import List, Tuple, Set

# Side definitions
TOP = "top"       # row 0
BOTTOM = "bottom" # row 5
LEFT = "left"     # col 0
RIGHT = "right"   # col 7

# Opposite side pairs
OPPOSITE_PAIRS = [
    (TOP, BOTTOM),
    (LEFT, RIGHT),
]


def get_sides_touched(path: List[Tuple[int, int]], 
                      rows: int = 6, cols: int = 8) -> Set[str]:
    """
    Get which sides of the board a path touches.
    A path touches a side if it includes a cell on that side.
    """
    sides = set()
    
    if not path:
        return sides
    
    for row, col in path:
        if row == 0:
            sides.add(TOP)
        if row == rows - 1:
            sides.add(BOTTOM)
        if col == 0:
            sides.add(LEFT)
        if col == cols - 1:
            sides.add(RIGHT)
    
    return sides


def is_spangram(path: List[Tuple[int, int]], 
                rows: int = 6, cols: int = 8) -> bool:
    """
    Check if a path is a valid spangram.
    A spangram must touch two opposite sides of the board.
    """
    if not path:
        return False
    
    sides = get_sides_touched(path, rows, cols)
    
    # Check if we have at least 2 sides
    if len(sides) < 2:
        return False
    
    # Check if the sides are opposite
    for side1, side2 in OPPOSITE_PAIRS:
        if side1 in sides and side2 in sides:
            return True
    
    return False


def get_spangram_sides(path: List[Tuple[int, int]], 
                       rows: int = 6, cols: int = 8) -> Tuple[str, str]:
    """
    Get the two opposite sides that a spangram touches.
    Returns (side1, side2) where side1 comes first in the pairs.
    """
    if not is_spangram(path, rows, cols):
        raise ValueError("Path is not a valid spangram")
    
    sides = get_sides_touched(path, rows, cols)
    
    for side1, side2 in OPPOSITE_PAIRS:
        if side1 in sides and side2 in sides:
            return (side1, side2)
    
    raise ValueError("Could not determine spangram sides")


def validate_spangram(path: List[Tuple[int, int]], 
                      rows: int = 6, cols: int = 8) -> bool:
    """
    Validate that a path meets all spangram requirements:
    1. Must touch two opposite sides
    2. Must be at least 2 cells long
    """
    if not path:
        return False
    
    if len(path) < 2:
        return False
    
    return is_spangram(path, rows, cols)


def find_spangrams(paths: List[List[Tuple[int, int]]], 
                   rows: int = 6, cols: int = 8) -> List[List[Tuple[int, int]]]:
    """Find all spangrams from a list of paths."""
    return [path for path in paths if is_spangram(path, rows, cols)]


def get_spangram_start_end(path: List[Tuple[int, int]], 
                           rows: int = 6, cols: int = 8) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Get the start and end cells of a spangram.
    These are the cells that touch the opposite sides.
    """
    sides = get_sides_touched(path, rows, cols)
    
    start = None
    end = None
    
    # Find first cell on one side and last cell on opposite side
    for i, (row, col) in enumerate(path):
        cell_sides = set()
        if row == 0:
            cell_sides.add(TOP)
        if row == rows - 1:
            cell_sides.add(BOTTOM)
        if col == 0:
            cell_sides.add(LEFT)
        if col == cols - 1:
            cell_sides.add(RIGHT)
        
        # Check if this cell is on a side
        for side in cell_sides:
            opposite = None
            if side == TOP:
                opposite = BOTTOM
            elif side == BOTTOM:
                opposite = TOP
            elif side == LEFT:
                opposite = RIGHT
            elif side == RIGHT:
                opposite = LEFT
            
            if opposite in sides:
                if start is None:
                    start = (row, col)
                end = (row, col)
    
    return (start, end)
