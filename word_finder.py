"""
Word finder module for Strands puzzle game.
Provides path finding and word construction capabilities.
"""

from typing import List, Tuple, Optional, Set
from board import Board, DIRECTIONS


class WordFinder:
    """Finds words in the board using path exploration."""
    
    def __init__(self, board: Board):
        """Initialize with a board reference."""
        self.board = board
        self.rows = board.ROWS
        self.cols = board.COLS
    
    def find_paths_from(self, start_row: int, start_col: int, 
                       max_length: int = 8) -> List[List[Tuple[int, int]]]:
        """
        Find all possible paths from a starting position using DFS.
        Returns list of paths (each path is a list of coordinates).
        """
        all_paths = []
        
        def dfs(row: int, col: int, path: List[Tuple[int, int]], 
                visited: Set[Tuple[int, int]]) -> None:
            # Add current position to path
            path.append((row, col))
            visited.add((row, col))
            
            # Save path if it's long enough
            if len(path) >= 2:
                all_paths.append(path[:])
            
            # Stop if max length reached
            if len(path) >= max_length:
                path.pop()
                visited.remove((row, col))
                return
            
            # Try all directions
            for dr, dc in DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                
                # Check boundaries
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    # Check if cell is not already in this path
                    if (new_row, new_col) not in visited:
                        # Check if cell is not used by another word
                        if not self.board.is_cell_used(new_row, new_col):
                            dfs(new_row, new_col, path, visited)
            
            # Backtrack
            path.pop()
            visited.remove((row, col))
        
        dfs(start_row, start_col, [], set())
        return all_paths
    
    def find_all_paths(self, min_length: int = 2, max_length: int = 8) -> List[List[Tuple[int, int]]]:
        """Find all possible paths on the board."""
        all_paths = []
        for row in range(self.rows):
            for col in range(self.cols):
                paths = self.find_paths_from(row, col, max_length)
                all_paths.extend(paths)
        return all_paths
    
    def get_word_from_path(self, path: List[Tuple[int, int]]) -> str:
        """Get the word formed by a path."""
        return self.board.get_letter_path(path)
    
    def validate_path(self, path: List[Tuple[int, int]]) -> bool:
        """Validate that a path is a valid word path."""
        if len(path) < 2:
            return False
        
        # Check for repeated cells
        if len(set(path)) != len(path):
            return False
        
        # Check each step is adjacent
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            dr, dc = abs(r2 - r1), abs(c2 - c1)
            # Valid adjacent: max of dr, dc should be 1
            if dr > 1 or dc > 1:
                return False
        
        return True
    
    def find_word_paths(self, word: str) -> List[List[Tuple[int, int]]]:
        """Find all paths that form a specific word."""
        matching_paths = []
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board.get_cell(row, col) == word[0]:
                    paths = self.find_paths_from(row, col, len(word))
                    for path in paths:
                        path_word = self.get_word_from_path(path)
                        if path_word == word:
                            matching_paths.append(path)
        
        return matching_paths
    
    def find_words_in_dictionary(self, dictionary: Set[str]) -> List[Tuple[str, List[Tuple[int, int]]]]:
        """
        Find all words from dictionary that exist on the board.
        Returns list of (word, path) tuples.
        """
        found_words = []
        all_paths = self.find_all_paths()
        
        for path in all_paths:
            word = self.get_word_from_path(path)
            if word in dictionary:
                found_words.append((word, path))
        
        return found_words
    
    def get_valid_next_steps(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get valid next positions from current path."""
        if not path:
            return []
        
        last_row, last_col = path[-1]
        next_steps = []
        
        for dr, dc in DIRECTIONS:
            new_row, new_col = last_row + dr, last_col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                if (new_row, new_col) not in path:
                    if not self.board.is_cell_used(new_row, new_col):
                        next_steps.append((new_row, new_col))
        
        return next_steps
    
    def is_path_extendable(self, path: List[Tuple[int, int]]) -> bool:
        """Check if a path can be extended further."""
        return len(self.get_valid_next_steps(path)) > 0
    
    def find_partial_words(self) -> List[Tuple[str, List[Tuple[int, int]]]]:
        """Find all partial words (potential complete words)."""
        partial_words = []
        all_paths = self.find_all_paths()
        
        for path in all_paths:
            word = self.get_word_from_path(path)
            if len(word) >= 2:
                partial_words.append((word, path))
        
        return partial_words
    
    def is_valid_word(self, path: List[Tuple[int, int]]) -> bool:
        """Check if a path forms a valid word."""
        if not self.validate_path(path):
            return False
        
        word = self.get_word_from_path(path)
        dictionary = self.board.get_dictionary()
        
        return word in dictionary
