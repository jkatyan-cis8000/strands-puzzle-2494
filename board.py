"""
Board module for Strands puzzle game.
Provides the 6x8 grid representation and management.
"""

from typing import List, Tuple, Optional, Set
from enum import Enum

# Direction constants for 8 directions (horizontal, vertical, diagonal)
DIRECTIONS = [
    (0, 1),   # Right
    (1, 0),   # Down
    (0, -1),  # Left
    (-1, 0),  # Up
    (1, 1),   # Down-Right
    (1, -1),  # Down-Left
    (-1, 1),  # Up-Right
    (-1, -1), # Up-Left
]

class Board:
    """Represents the 6x8 grid for the Strands puzzle."""
    
    ROWS = 6
    COLS = 8
    
    def __init__(self):
        """Initialize an empty board."""
        self.grid: List[List[str]] = [['' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.used_cells: set[Tuple[int, int]] = set()
        self.cell_used_by: dict[Tuple[int, int], str] = {}
        self.dictionary: Set[str] = set()
    
    def set_cell(self, row: int, col: int, letter: str) -> bool:
        """Set a letter at the given position."""
        if self._is_valid_position(row, col):
            self.grid[row][col] = letter
            return True
        return False
    
    def get_cell(self, row: int, col: int) -> Optional[str]:
        """Get the letter at the given position."""
        if self._is_valid_position(row, col):
            return self.grid[row][col]
        return None
    
    def get_letter(self, row: int, col: int) -> str:
        """Get letter at position, returns empty string if invalid."""
        if self._is_valid_position(row, col):
            return self.grid[row][col]
        return ''
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board boundaries."""
        return 0 <= row < self.ROWS and 0 <= col < self.COLS
    
    def mark_cell_used(self, row: int, col: int, word_name: str = "") -> None:
        """Mark a cell as used by a word."""
        self.used_cells.add((row, col))
        if word_name:
            self.cell_used_by[(row, col)] = word_name
    
    def mark_cells_used(self, path: List[Tuple[int, int]], word_name: str = "") -> None:
        """Mark multiple cells as used by a word."""
        for row, col in path:
            self.mark_cell_used(row, col, word_name)
    
    def is_cell_used(self, row: int, col: int) -> bool:
        """Check if a cell is already used."""
        return (row, col) in self.used_cells
    
    def clear_cell_usage(self, row: int, col: int) -> None:
        """Clear usage of a cell."""
        if (row, col) in self.used_cells:
            self.used_cells.remove((row, col))
        if (row, col) in self.cell_used_by:
            del self.cell_used_by[(row, col)]
    
    def clear_word_usage(self, path: List[Tuple[int, int]]) -> None:
        """Clear usage of all cells in a path."""
        for row, col in path:
            self.clear_cell_usage(row, col)
    
    def get_cell_path(self, path: List[Tuple[int, int]]) -> List[str]:
        """Get the letters along a path."""
        return [self.grid[r][c] for r, c in path]
    
    def get_letter_path(self, path: List[Tuple[int, int]]) -> str:
        """Get a word from a path."""
        return ''.join(self.get_cell_path(path))
    
    def fill_with_random_letters(self) -> None:
        """Fill empty cells with random uppercase letters."""
        import random
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if not self.grid[row][col]:
                    self.grid[row][col] = random.choice(letters)
    
    def fill_from_words(self, words: List[Tuple[str, List[Tuple[int, int]]]]) -> None:
        """
        Fill the board from a list of words and their paths.
        Fills remaining empty cells with random letters.
        """
        import random
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        # Clear existing grid
        for row in range(self.ROWS):
            for col in range(self.COLS):
                self.grid[row][col] = ''
        
        # Place words
        for word, path in words:
            for i, (row, col) in enumerate(path):
                if i < len(word):
                    self.grid[row][col] = word[i]
        
        # Fill remaining with random letters
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if not self.grid[row][col]:
                    self.grid[row][col] = random.choice(letters)
    
    def is_fully_filled(self) -> bool:
        """Check if all cells are filled with letters."""
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if not self.grid[row][col] or self.grid[row][col] == '':
                    return False
        return True
    
    def get_grid_copy(self) -> List[List[str]]:
        """Get a copy of the grid."""
        return [row[:] for row in self.grid]
    
    def reset(self) -> None:
        """Reset the board to initial state."""
        self.grid = [['' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.used_cells = set()
        self.cell_used_by = {}
        self.dictionary = set()
    
    def set_dictionary(self, words: Set[str]) -> None:
        """Set the dictionary of valid words."""
        self.dictionary = words
    
    def get_dictionary(self) -> Set[str]:
        """Get the dictionary of valid words."""
        return self.dictionary
    
    def display(self, highlight_cells: List[Tuple[int, int]] = None) -> str:
        """Return a string representation of the board."""
        lines = []
        for row in range(self.ROWS):
            line = ' '.join(self.grid[row])
            lines.append(line)
        return '\n'.join(lines)


def get_direction_from_path(path: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Get the primary direction of a path."""
    if len(path) < 2:
        return (0, 0)
    
    dr = path[1][0] - path[0][0]
    dc = path[1][1] - path[0][1]
    
    # Normalize to -1, 0, or 1
    if dr != 0:
        dr = 1 if dr > 0 else -1
    if dc != 0:
        dc = 1 if dc > 0 else -1
    
    return (dr, dc)
