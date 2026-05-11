"""
Game controller module for Strands puzzle game.
Manages game flow, word validation, and interaction between components.
"""

from typing import List, Tuple, Optional, Set
from board import Board
from game_state import GameState, WordInfo
from word_finder import WordFinder
from theme import ThemeManager
from ui import StrandsUI


class StrandsGame:
    """Main game controller managing game flow and logic."""
    
    def __init__(self):
        """Initialize the game."""
        # Initialize components
        self.board = Board(rows=6, cols=8)
        self.theme_manager = ThemeManager(self.board)
        self.game_state = GameState(self.board)
        self.word_finder = WordFinder(self.board)
        self.ui = StrandsUI(self.game_state, self.theme_manager)
        
        # Game state tracking
        self.words_found_count = 0
        self.non_theme_words_count = 0
        self.hint_word_count = 0
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup UI callbacks."""
        self.ui.on_cell_select = self._on_cell_select
        self.ui.on_word_submit = self._on_word_submit
        self.ui.on_hint_request = self._on_hint_request
    
    def start_new_game(self, theme: Optional[str] = None) -> None:
        """Start a new game with optional theme selection."""
        # Initialize components
        self.board.reset()
        self.game_state.reset()
        self.words_found_count = 0
        self.non_theme_words_count = 0
        self.hint_word_count = 0
        
        # Setup theme
        if theme:
            self.theme_manager.select_theme(theme)
        else:
            self.theme_manager.select_random_theme()
        
        # Generate puzzle
        words, spangram, spangram_path = self.theme_manager.create_puzzle(num_theme_words=5)
        
        # Update game state
        self.game_state.theme_words = set(words)
        self.game_state.game_started = True
        self.game_state.start_time = 0  # Would be set to current time in real implementation
        
        # Initialize word info for theme words
        for word in words:
            self.game_state.found_words[word] = WordInfo(
                word=word,
                path=[],
                found_at=0,
                is_theme=True,
                is_spangram=word == spangram
            )
        
        # Initialize spangram
        if spangram and spangram_path:
            self.game_state.found_words[spangram].path = spangram_path
            self.game_state.found_words[spangram].is_spangram = True
        
        self.ui.reset_game()
    
    def _on_cell_select(self, row: int, col: int) -> None:
        """Handle cell selection."""
        # If cell is already used by another word, don't allow selection
        if self.game_state.is_cell_used(row, col):
            # Clear selection if clicking on used cell
            self.ui.deselect_all()
            return
        
        self.ui.add_cell_to_selection(row, col)
    
    def _on_word_submit(self, word: str) -> bool:
        """Handle word submission."""
        # Validate word length
        if len(word) < 4:
            return False
        
        # Check if word is already found
        if word in self.game_state.found_words_set:
            return False
        
        # Validate path is correct
        path = self.ui.get_current_selection()
        if not self.board.validate_path(path):
            return False
        
        # Check if word matches the selected path
        path_word = self.board.get_letter_path(path)
        if path_word != word:
            return False
        
        # Check if path contains all required cells
        path_set = set(path)
        for row in range(self.board.ROWS):
            for col in range(self.board.COLS):
                if self.board.get_cell(row, col) == word:
                    # Word must contain all occurrences of its letters
                    if (row, col) not in path_set:
                        # Check if the cell is part of a longer word
                        cell_word = self.game_state.get_word_at_cell(row, col)
                        if cell_word != word:
                            return False
        
        # Word is valid - add to game state
        return self._add_found_word(word, path)
    
    def _add_found_word(self, word: str, path: List[Tuple[int, int]]) -> bool:
        """Add a found word to the game state."""
        # Check if word is a spangram
        is_spangram = len(path) == 8 and self._is_spangram_path(path)
        
        # Determine if theme word
        is_theme = word in self.game_state.theme_words
        
        # Update counters
        self.words_found_count += 1
        if not is_theme:
            self.non_theme_words_count += 1
        
        # Add word to game state
        success = self.game_state.add_word(
            word=word,
            path=path,
            is_theme=is_theme,
            is_spangram=is_spangram,
            word_count=self.words_found_count
        )
        
        if success:
            # Check for game completion
            if self.game_state.is_game_complete():
                self.game_state.game_over = True
                self.ui.on_hint_request = lambda: None  # Disable hints on game over
        
        return success
    
    def _is_spangram_path(self, path: List[Tuple[int, int]]) -> bool:
        """Check if path is a spangram (touches two opposite sides)."""
        if len(path) != 8:
            return False
        
        rows = set(p[0] for p in path)
        cols = set(p[1] for p in path)
        
        # Check if touches top and bottom
        if 0 in rows and 5 in rows:
            return True
        
        # Check if touches left and right
        if 0 in cols and 7 in cols:
            return True
        
        return False
    
    def _on_hint_request(self) -> None:
        """Handle hint request."""
        hints_available = self.game_state.get_hints_available()
        if hints_available > 0:
            # Find a word that hasn't been found
            for word in self.theme_manager.current_theme_words:
                if word not in self.game_state.found_words_set:
                    # Show hint for this word
                    print(f"Hint: Try finding '{word}'")
                    return
            
            # If all theme words found, find any word
            all_words = self.word_finder.get_all_words_on_board()
            for word in all_words:
                if word not in self.game_state.found_words_set:
                    print(f"Hint: Try finding '{word}'")
                    return
    
    def get_theme_words_remaining(self) -> List[str]:
        """Get list of theme words not yet found."""
        return self.game_state.get_theme_words_remaining()
    
    def get_theme_words_count(self) -> int:
        """Get count of theme words found."""
        return len(self.game_state.theme_words) - len(self.get_theme_words_remaining())
    
    def get_non_theme_words_count(self) -> int:
        """Get count of non-theme words found."""
        return self.non_theme_words_count
    
    def get_words_found(self) -> List[WordInfo]:
        """Get all found words."""
        return self.game_state.get_found_words()
    
    def is_spangram_found(self) -> bool:
        """Check if spangram has been found."""
        return self.game_state.has_found_spangram()
    
    def get_completion_percentage(self) -> float:
        """Get board completion percentage."""
        return self.game_state.get_completion_percentage()
    
    def get_theme_completion_percentage(self) -> float:
        """Get theme word completion percentage."""
        return self.game_state.get_theme_completion()
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.game_state.is_game_complete()
    
    def get_score(self) -> int:
        """Get current score."""
        return self.game_state.score
    
    def get_hint_words_remaining(self) -> int:
        """Get remaining hint words needed for next hint."""
        next_hint_threshold = 3 * (self.game_state.hints_used + 1)
        return max(0, next_hint_threshold - self.non_theme_words_count)
    
    def handle_user_action(self, action: str, data: Optional[dict] = None) -> dict:
        """Handle a user action and return response."""
        if action == "select_cell":
            row, col = data["row"], data["col"]
            self.ui.select_cell(row, col)
            return {"success": True, "current_word": self.ui.get_current_word()}
        
        elif action == "submit_word":
            word = data["word"]
            success = self.ui.submit_word()
            return {"success": success, "word": word}
        
        elif action == "clear_selection":
            self.ui.deselect_all()
            return {"success": True, "current_word": ""}
        
        elif action == "hint":
            self.ui.request_hint()
            return {"success": True, "hint_available": self.game_state.get_hints_available() > 0}
        
        elif action == "reset":
            self.start_new_game()
            return {"success": True, "game_reset": True}
        
        elif action == "get_state":
            return {
                "success": True,
                "score": self.get_score(),
                "theme_words_found": self.get_theme_words_count(),
                "theme_words_total": len(self.theme_manager.current_theme_words),
                "non_theme_words_found": self.non_theme_words_count,
                "hints_used": self.game_state.hints_used,
                "completion": self.get_completion_percentage(),
                "game_over": self.is_game_over()
            }
        
        return {"success": False, "error": f"Unknown action: {action}"}
