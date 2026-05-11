"""
UI module for Strands puzzle game.
Provides user interface for game interactions.
"""

from typing import List, Tuple, Optional, Callable
from board import Board
from game_state import GameState, WordInfo
from theme import ThemeManager


class StrandsUI:
    """Handles all UI interactions for the Strands puzzle."""
    
    def __init__(self, game_state: GameState, theme_manager: ThemeManager):
        """Initialize UI with game state and theme manager."""
        self.game_state = game_state
        self.theme_manager = theme_manager
        self.board = game_state.board
        self.selected_cells: List[Tuple[int, int]] = []
        self.current_word: str = ""
        self.hover_cell: Optional[Tuple[int, int]] = None
        self.on_cell_select: Optional[Callable[[int, int], None]] = None
        self.on_word_submit: Optional[Callable[[str], bool]] = None
        self.on_hint_request: Optional[Callable[[], None]] = None
        self.on_cell_hover: Optional[Callable[[int, int], None]] = None
    
    def select_cell(self, row: int, col: int) -> None:
        """Select a cell on the board."""
        if self.on_cell_select:
            self.on_cell_select(row, col)
    
    def submit_word(self) -> bool:
        """Submit the currently selected word."""
        if self.on_word_submit:
            return self.on_word_submit(self.current_word)
        return False
    
    def request_hint(self) -> None:
        """Request a hint."""
        if self.on_hint_request:
            self.on_hint_request()
    
    def get_theme_words(self) -> List[str]:
        """Get the list of theme words to find."""
        return self.theme_manager.current_theme_words
    
    def get_theme_words_status(self) -> List[Tuple[str, bool]]:
        """Get theme words with their found status."""
        words = self.theme_manager.current_theme_words
        return [(word, word in self.game_state.found_words_set) for word in words]
    
    def get_spangram_status(self) -> bool:
        """Get the spangram found status."""
        return self.game_state.has_found_spangram()
    
    def get_current_score(self) -> int:
        """Get the current score."""
        return self.game_state.score
    
    def get_completion_percentage(self) -> float:
        """Get board completion percentage."""
        return self.game_state.get_completion_percentage()
    
    def get_hints_available(self) -> int:
        """Get number of hints available."""
        return self.game_state.get_hints_available()
    
    def get_found_words(self) -> List[WordInfo]:
        """Get list of found words."""
        return self.game_state.get_found_words()
    
    def get_found_spangrams(self) -> List[WordInfo]:
        """Get list of found spangrams."""
        return self.game_state.get_spangrams()
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.game_state.is_game_complete()
    
    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.game_state.reset()
        self.selected_cells = []
        self.current_word = ""
    
    def select_path_from_cells(self, path: List[Tuple[int, int]]) -> None:
        """Select cells based on a path."""
        self.selected_cells = path.copy()
        self.current_word = self.board.get_letter_path(path)
    
    def deselect_all(self) -> None:
        """Deselect all cells."""
        self.selected_cells = []
        self.current_word = ""
    
    def add_cell_to_selection(self, row: int, col: int) -> bool:
        """Add a cell to the current selection."""
        # Check if cell is already selected
        if (row, col) in self.selected_cells:
            return False
        
        # Check if cell is already used by another word
        if self.game_state.is_cell_used(row, col):
            return False
        
        # Check if cell is adjacent to last selected cell
        if self.selected_cells:
            last_row, last_col = self.selected_cells[-1]
            dr, dc = abs(row - last_row), abs(col - last_col)
            if dr > 1 or dc > 1:
                return False
        
        self.selected_cells.append((row, col))
        self.current_word = self.board.get_letter_path(self.selected_cells)
        return True
    
    def remove_last_cell(self) -> None:
        """Remove the last cell from selection."""
        if self.selected_cells:
            self.selected_cells.pop()
            self.current_word = self.board.get_letter_path(self.selected_cells)
    
    def get_current_selection(self) -> List[Tuple[int, int]]:
        """Get the currently selected cells."""
        return self.selected_cells.copy()
    
    def get_current_word(self) -> str:
        """Get the current word being formed."""
        return self.current_word
    
    def is_valid_path(self) -> bool:
        """Check if current selection forms a valid path."""
        if len(self.selected_cells) < 2:
            return False
        return self.board.validate_path(self.selected_cells)
    
    def get_word_info(self, word: str) -> Optional[WordInfo]:
        """Get information about a found word."""
        return self.game_state.found_words.get(word)
    
    def get_cell_status(self, row: int, col: int) -> str:
        """Get the status of a cell (used, unused, selected)."""
        if (row, col) in self.selected_cells:
            return "selected"
        if self.game_state.is_cell_used(row, col):
            return "used"
        return "unused"
    
    def get_hint_for_word(self, word: str) -> Optional[Tuple[int, int]]:
        """Get a hint position for a word."""
        if word not in self.game_state.found_words_set:
            return None
        word_info = self.game_state.found_words[word]
        if word_info.path:
            return word_info.path[0]
        return None
    
    def format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
