"""
Game state module for Strands puzzle game.
Manages the current game state including found words, score, and hints.
"""

from typing import List, Tuple, Set, Dict, Optional
from dataclasses import dataclass, field
from board import Board


@dataclass
class WordInfo:
    """Information about a found word."""
    word: str
    path: List[Tuple[int, int]]
    found_at: int = 0
    is_theme: bool = False
    is_spangram: bool = False
    
    def __hash__(self):
        return hash(self.word)
    
    def __eq__(self, other):
        if isinstance(other, WordInfo):
            return self.word == other.word
        return False


@dataclass
class GameState:
    """Manages the complete game state."""
    
    board: Board
    found_words: Dict[str, WordInfo] = field(default_factory=dict)
    theme_words: Set[str] = field(default_factory=set)
    score: int = 0
    hints_used: int = 0
    hint_words_found_count: int = 0
    game_started: bool = False
    game_over: bool = False
    start_time: Optional[int] = None
    
    # Track which words are found
    found_words_set: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize found_words_set from found_words."""
        self.found_words_set = set(self.found_words.keys())
    
    def add_word(self, word: str, path: List[Tuple[int, int]], 
                 is_theme: bool = False, is_spangram: bool = False,
                 word_count: int = 0) -> bool:
        """
        Add a found word to the game state.
        Returns True if the word was added, False if already found.
        """
        if word in self.found_words_set:
            return False
        
        # Mark cells as used
        self.board.mark_cells_used(path, word)
        
        # Create word info
        word_info = WordInfo(
            word=word,
            path=path,
            found_at=word_count,
            is_theme=is_theme,
            is_spangram=is_spangram
        )
        
        # Update state
        self.found_words[word] = word_info
        self.found_words_set.add(word)
        
        # Update score
        self._update_score(word_info)
        
        # Track hint progress
        if not is_theme:
            self.hint_words_found_count += 1
        
        return True
    
    def _update_score(self, word_info: WordInfo) -> None:
        """Update score based on word properties."""
        base_score = len(word_info.word)
        
        # Theme words score more
        if word_info.is_theme:
            base_score *= 2
        
        # Spangrams score even more
        if word_info.is_spangram:
            base_score *= 3
        
        # Bonus for longer words
        if len(word_info.word) >= 8:
            base_score += 10
        
        self.score += base_score
    
    def get_theme_words_remaining(self) -> List[str]:
        """Get list of theme words not yet found."""
        return [word for word in self.theme_words if word not in self.found_words_set]
    
    def get_found_words(self, include_theme: bool = True) -> List[WordInfo]:
        """Get list of found words, optionally excluding theme words."""
        words = []
        for word_info in self.found_words.values():
            if include_theme or not word_info.is_theme:
                words.append(word_info)
        return words
    
    def get_found_words_count(self, include_theme: bool = True) -> int:
        """Get count of found words."""
        return len(self.get_found_words(include_theme))
    
    def get_spangrams(self) -> List[WordInfo]:
        """Get list of found spangrams."""
        return [w for w in self.found_words.values() if w.is_spangram]
    
    def has_found_spangram(self) -> bool:
        """Check if a spangram has been found."""
        return any(w.is_spangram for w in self.found_words.values())
    
    def is_board_fully_filled(self) -> bool:
        """Check if all cells are used."""
        return len(self.board.used_cells) == (self.board.ROWS * self.board.COLS)
    
    def is_game_complete(self) -> bool:
        """Check if the game is complete."""
        if self.game_over:
            return True
        
        # Check if all theme words are found and board is full
        remaining = self.get_theme_words_remaining()
        if not remaining and self.is_board_fully_filled():
            self.game_over = True
            return True
        
        return False
    
    def use_hint(self) -> bool:
        """Use a hint if available (every 3 non-theme words)."""
        if self.hint_words_found_count >= 3 * (self.hints_used + 1):
            self.hints_used += 1
            return True
        return False
    
    def get_hints_available(self) -> int:
        """Get number of hints available."""
        return self.hint_words_found_count // 3
    
    def reset(self) -> None:
        """Reset the game state to initial values."""
        self.board.reset()
        self.found_words = {}
        self.found_words_set = set()
        self.score = 0
        self.hints_used = 0
        self.hint_words_found_count = 0
        self.game_started = False
        self.game_over = False
        self.start_time = None
    
    def get_completion_percentage(self) -> float:
        """Get the percentage of the board filled."""
        total_cells = self.board.ROWS * self.board.COLS
        return (len(self.board.used_cells) / total_cells) * 100
    
    def get_theme_completion(self) -> float:
        """Get percentage of theme words found."""
        if not self.theme_words:
            return 0.0
        found = len([w for w in self.theme_words if w in self.found_words_set])
        return (found / len(self.theme_words)) * 100
    
    def is_word_found(self, word: str) -> bool:
        """Check if a word has been found."""
        return word in self.found_words_set
    
    def is_cell_used(self, row: int, col: int) -> bool:
        """Check if a cell is used by any found word."""
        return self.board.is_cell_used(row, col)
    
    def get_word_at_cell(self, row: int, col: int) -> Optional[str]:
        """Get the word that uses a cell, if any."""
        if (row, col) in self.board.cell_used_by:
            return self.board.cell_used_by[(row, col)]
        return None
