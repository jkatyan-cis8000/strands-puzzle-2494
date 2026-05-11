"""
Theme module for Strands puzzle game.
Handles theme word generation and grid filling.
"""

from typing import List, Tuple, Set, Optional
from board import Board
from word_finder import WordFinder
from spangram import is_spangram, get_sides_touched
import random


class ThemeManager:
    """Manages theme words and grid generation."""
    
    # Common themes with sample words
    THEMES = {
        "fruits": ["APPLE", "BANANA", "CHERRY", "GRAPE", "LEMON", "MANGO", "ORANGE", "PEACH", "PEAR", "PLUM"],
        "animals": ["LION", "TIGER", "BEAR", "ZEBRA", "GIRAFFE", "ELEPHANT", "MONKEY", "PANDA", "KOALA", "KANGAROO"],
        "colors": ["RED", "BLUE", "GREEN", "YELLOW", "ORANGE", "PURPLE", "PINK", "BLACK", "WHITE", "GRAY"],
        "countries": ["USA", "CANADA", "MEXICO", "FRANCE", "GERMANY", "SPAIN", "ITALY", "JAPAN", "CHINA", "BRAZIL"],
        "cities": ["NEW YORK", "LONDON", "PARIS", "TOKYO", "BERLIN", "ROME", "MADRID", "DUBAI", "SINGAPORE", "HONG KONG"],
        "sports": ["SOCCER", "BASKETBALL", "TENNIS", "GOLF", "BASEBALL", "CRICKET", "RUGBY", "HOCKEY", "VOLLEYBALL", "SWIMMING"],
        "music": ["NOTE", "RHYTHM", "MELODY", "SONG", "LYRIC", "GUITAR", "PIANO", "DRUM", "BASS", "VIOLIN"],
        "space": ["STAR", "PLANET", "MOON", "SUN", "GALAXY", "COMET", "ASTEROID", "NEBULA", "ORBIT", "GRAVITY"],
        "weather": ["RAIN", "SNOW", "SUN", "WIND", "STORM", "CLOUD", "FOG", "HAIL", "SLEET", "THUNDER"],
        "food": ["PIZZA", "BURGER", "PASTA", "SUSHI", "TACO", "Salad", "STEAK", "FISH", "CHICKEN", "PORK"],
    }
    
    def __init__(self, board: Board):
        """Initialize with a board reference."""
        self.board = board
        self.word_finder = WordFinder(board)
        self.current_theme: Optional[str] = None
        self.current_theme_words: List[str] = []
        self.spangram: Optional[str] = None
        self.spangram_path: List[Tuple[int, int]] = []
    
    def select_random_theme(self) -> str:
        """Select a random theme."""
        themes = list(self.THEMES.keys())
        self.current_theme = random.choice(themes)
        return self.current_theme
    
    def select_theme(self, theme: str) -> bool:
        """Select a specific theme."""
        if theme in self.THEMES:
            self.current_theme = theme
            return True
        return False
    
    def get_theme_words(self) -> List[str]:
        """Get words for the current theme."""
        if self.current_theme:
            return self.THEMES[self.current_theme].copy()
        return []
    
    def select_spangram_from_theme(self, words: List[str]) -> Optional[str]:
        """Select a spangram from theme words (must be 8 letters to span grid)."""
        # Look for a word that's long enough to be a spangram
        # In Strands, the spangram is typically the longest word
        long_words = [w for w in words if len(w) >= 6]
        if long_words:
            return random.choice(long_words)
        return random.choice(words) if words else None
    
    def find_spangram_path(self, word: str) -> Optional[List[Tuple[int, int]]]:
        """Find a spangram path for the given word."""
        rows = self.board.ROWS
        cols = self.board.COLS
        
        # Try to find paths that touch opposite sides
        for row in range(rows):
            for col in range(cols):
                if self.board.get_cell(row, col) == word[0]:
                    paths = self.word_finder.find_paths_from(row, col, len(word))
                    for path in paths:
                        if is_spangram(path, rows, cols):
                            return path
        
        return None
    
    def place_word_on_board(self, word: str, path: List[Tuple[int, int]]) -> bool:
        """Place a word on the board at the given path."""
        if len(word) != len(path):
            return False
        
        for i, (row, col) in enumerate(path):
            if self.board.get_cell(row, col) == '' or self.board.get_cell(row, col) == word[i]:
                self.board.set_cell(row, col, word[i])
            else:
                # Conflict - can't place
                return False
        
        return True
    
    def clear_word_from_board(self, path: List[Tuple[int, int]]) -> None:
        """Clear cells that were filled by a word."""
        for row, col in path:
            if not self.board.is_cell_used(row, col):
                self.board.set_cell(row, col, '')
    
    def generate_grid_from_words(self, words: List[str], spangram: str) -> bool:
        """
        Generate a grid from theme words and spangram.
        Returns True if successful.
        """
        # Clear the board
        self.board.reset()
        
        # Try to place spangram first
        spangram_path = self.find_spangram_path(spangram)
        if not spangram_path:
            return False
        
        # Place spangram
        if not self.place_word_on_board(spangram, spangram_path):
            return False
        
        # Track used cells
        used_cells = set(spangram_path)
        
        # Place other words
        for word in words:
            # Find valid paths for this word
            paths = self.word_finder.find_word_paths(word)
            valid_paths = []
            
            for path in paths:
                # Check if path only uses unused cells or cells with matching letters
                valid = True
                for i, (row, col) in enumerate(path):
                    if i < len(word):
                        cell_letter = self.board.get_cell(row, col)
                        if cell_letter != '' and cell_letter != word[i]:
                            valid = False
                            break
                if valid:
                    valid_paths.append(path)
            
            if valid_paths:
                # Pick a random valid path
                path = random.choice(valid_paths)
                self.place_word_on_board(word, path)
        
        # Fill remaining empty cells
        self.board.fill_with_random_letters()
        
        return True
    
    def create_puzzle(self, num_theme_words: int = 5) -> Tuple[List[str], str, List[List[Tuple[int, int]]]]:
        """
        Create a new puzzle with the current theme.
        Returns (theme_words, spangram, word_paths).
        """
        if not self.current_theme:
            self.select_random_theme()
        
        all_words = self.get_theme_words()
        if len(all_words) < num_theme_words:
            num_theme_words = len(all_words)
        
        # Select random theme words
        words = random.sample(all_words, num_theme_words)
        
        # Select spangram (must be 8 letters)
        spangram = self.select_spangram_from_theme(words)
        
        # Generate grid
        success = self.generate_grid_from_words(words, spangram)
        
        if not success:
            # Try again with different combination
            return self.create_puzzle(num_theme_words)
        
        # Store for later use
        self.current_theme_words = words
        self.spangram = spangram
        self.spangram_path = self.find_spangram_path(spangram) if spangram else []
        
        return (words, spangram, self.spangram_path)
    
    def fill_remaining_cells(self) -> None:
        """Fill any remaining empty cells with random letters."""
        self.board.fill_with_random_letters()
    
    def get_grid(self) -> List[List[str]]:
        """Get the current grid."""
        return self.board.get_grid_copy()
    
    def set_grid(self, grid: List[List[str]]) -> None:
        """Set the grid from an external source."""
        self.board.reset()
        for row in range(self.board.ROWS):
            for col in range(self.board.COLS):
                if row < len(grid) and col < len(grid[row]):
                    self.board.set_cell(row, col, grid[row][col])
    
    def get_word_at_position(self, row: int, col: int) -> Optional[str]:
        """Get the word that contains the given position."""
        # This would need to be implemented by tracking word positions
        return None
    
    def get_all_words_on_board(self) -> List[str]:
        """Get all words currently on the board (from theme words)."""
        return self.current_theme_words + ([self.spangram] if self.spangram else [])
