# Strands Puzzle Architecture

## Overview
A web-based implementation of the NYT Strands puzzle featuring:
- 6x8 grid of letters
- Theme-based word discovery
- Spangram detection (touches two opposite sides)
- Hint system (3 non-theme words = 1 hint)
- Full board completion requirement

## Module Structure

### 1. Board Module (`board.py`)
- Grid representation (6 rows x 8 columns)
- Cell management and state tracking
- Methods for letter placement and retrieval
- Direction utilities for word formation

### 2. Word Finder Module (`word_finder.py`)
- Path finding algorithm for valid word paths
- Adjacent cell detection (8 directions)
- Path validation and word construction
- Non-overlapping path tracking

### 3. Spangram Module (`spangram.py`)
- Spangram detection (must touch two opposite sides)
- Side detection logic (top-bottom, left-right)
- Validation of spangram requirements

### 4. Game State Module (`game_state.py`)
- Overall game state management
- Themed words tracking
- Non-theme words tracking
- Hint counting and unlock logic
- Board coverage tracking

### 5. Theme Generator Module (`theme.py`)
- Theme word generation
- Grid filling algorithm
- Ensures full board coverage
- Spangram placement

### 6. UI Module (`ui.py`)
- HTML/CSS structure
- Interactive grid display
- Selected path visualization
- Solution highlighting
- Hint system display

### 7. Game Controller Module (`game.py`)
- Main game loop and logic
- Input handling (selection, deselection)
- Word validation
- Win condition checking
- Hint unlocking

## File Dependencies
```
game.py (main controller, imports all modules)
├── board.py
├── word_finder.py
├── spangram.py
├── game_state.py
├── theme.py
└── ui.py (frontend only)
```

## Key Algorithms

### Path Finding
- DFS with backtracking to find all valid paths
- Each cell can only be used once per word
- 8-directional movement (horizontal, vertical, diagonal)

### Spangram Detection
- Track start and end coordinates
- Check if start is on one side and end on opposite
- Sides: top (row=0), bottom (row=5), left (col=0), right (col=7)

### Hint System
- Count non-theme words found
- Unlock hint every 3 words
- Hint shows one remaining theme word
