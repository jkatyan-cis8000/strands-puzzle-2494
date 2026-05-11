/**
 * Strands Puzzle Game - JavaScript Implementation
 * Client-side game logic and UI handling
 */

// Game configuration
const CONFIG = {
    rows: 6,
    cols: 8,
    themes: {
        fruits: ["APPLE", "BANANA", "CHERRY", "GRAPE", "LEMON"],
        animals: ["LION", "TIGER", "BEAR", "ZEBRA", "GIRAFFE"],
        colors: ["RED", "BLUE", "GREEN", "YELLOW", "ORANGE"],
        countries: ["USA", "CANADA", "MEXICO", "FRANCE", "GERMANY"],
        cities: ["NEW YORK", "LONDON", "PARIS", "TOKYO", "BERLIN"],
        sports: ["SOCCER", "BASKETBALL", "TENNIS", "GOLF", "BASEBALL"],
        space: ["STAR", "PLANET", "MOON", "SUN", "GALAXY"],
        weather: ["RAIN", "SNOW", "SUN", "WIND", "STORM"]
    }
};

// Game state
let gameState = {
    grid: [],
    foundWords: new Set(),
    currentSelection: [],
    currentWord: "",
    score: 0,
    themeWords: [],
    themeWordsFound: 0,
    hintsUsed: 0,
    hintsAvailable: 0,
    hintWordsFound: 0,
    gameStarted: false,
    gameWon: false
};

// DOM elements
let boardElement = document.getElementById('board');
let currentWordElement = document.getElementById('current-word');
let themeDisplayElement = document.getElementById('theme-display');
let foundWordsListElement = document.getElementById('found-words-list');
let themeCountElement = document.getElementById('theme-count');
let completionElement = document.getElementById('completion');
let scoreElement = document.getElementById('score-display');
let hintCountElement = document.getElementById('hint-count');
let resetButton = document.getElementById('reset-btn');
let hintButton = document.getElementById('hint-btn');
let modal = document.getElementById('message-modal');
let modalTitle = document.getElementById('modal-title');
let modalMessage = document.getElementById('modal-message');
let modalClose = document.getElementById('modal-close');

// Initialize game
function initGame(theme) {
    if (!theme) {
        const themeNames = Object.keys(CONFIG.themes);
        theme = themeNames[Math.floor(Math.random() * themeNames.length)];
    }
    
    gameState.themeWords = CONFIG.themes[theme];
    gameState.themeWordsFound = 0;
    gameState.foundWords = new Set();
    gameState.currentSelection = [];
    gameState.currentWord = "";
    gameState.score = 0;
    gameState.hintsUsed = 0;
    gameState.hintWordsFound = 0;
    gameState.gameStarted = true;
    gameState.gameWon = false;
    
    generateGrid();
    renderBoard();
    updateUI();
    showTheme(theme);
}

// Generate grid with theme words
function generateGrid() {
    gameState.grid = [];
    
    // Initialize empty grid
    for (let row = 0; row < CONFIG.rows; row++) {
        gameState.grid[row] = [];
        for (let col = 0; col < CONFIG.cols; col++) {
            gameState.grid[row][col] = '';
        }
    }
    
    // Place theme words (simplified placement logic)
    let placedWords = [];
    let attempts = 0;
    
    while (placedWords.length < gameState.themeWords.length && attempts < 100) {
        const word = gameState.themeWords[placedWords.length];
        if (placeWord(word)) {
            placedWords.push(word);
        }
        attempts++;
    }
    
    // Fill remaining cells with random letters
    fillRemaining();
}

// Try to place a word on the grid
function placeWord(word) {
    const directions = [
        { dr: 0, dc: 1 },   // horizontal
        { dr: 1, dc: 0 },   // vertical
        { dr: 1, dc: 1 },   // diagonal down-right
        { dr: 1, dc: -1 }   // diagonal down-left
    ];
    
    const maxAttempts = 50;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        const direction = directions[Math.floor(Math.random() * directions.length)];
        const startRow = Math.floor(Math.random() * CONFIG.rows);
        const startCol = Math.floor(Math.random() * CONFIG.cols);
        
        // Check if word fits
        let canPlace = true;
        for (let i = 0; i < word.length; i++) {
            const row = startRow + i * direction.dr;
            const col = startCol + i * direction.dc;
            
            if (row >= CONFIG.rows || col >= CONFIG.cols || col < 0) {
                canPlace = false;
                break;
            }
            
            // Check if cell is empty or same letter
            if (gameState.grid[row][col] !== '' && gameState.grid[row][col] !== word[i]) {
                canPlace = false;
                break;
            }
        }
        
        if (canPlace) {
            // Place the word
            for (let i = 0; i < word.length; i++) {
                const row = startRow + i * direction.dr;
                const col = startCol + i * direction.dc;
                gameState.grid[row][col] = word[i];
            }
            return true;
        }
    }
    
    return false;
}

// Fill remaining cells with random letters
function fillRemaining() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
    for (let row = 0; row < CONFIG.rows; row++) {
        for (let col = 0; col < CONFIG.cols; col++) {
            if (gameState.grid[row][col] === '') {
                gameState.grid[row][col] = letters[Math.floor(Math.random() * letters.length)];
            }
        }
    }
}

// Render the board
function renderBoard() {
    boardElement.innerHTML = '';
    
    for (let row = 0; row < CONFIG.rows; row++) {
        for (let col = 0; col < CONFIG.cols; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.textContent = gameState.grid[row][col];
            cell.dataset.row = row;
            cell.dataset.col = col;
            
            // Check if cell is selected
            if (isCellSelected(row, col)) {
                cell.classList.add('selected');
            }
            
            // Check if cell is used by a found word
            if (isCellUsed(row, col)) {
                cell.classList.add('used');
            }
            
            // Check if cell is part of a theme word
            if (isCellTheme(row, col)) {
                cell.classList.add('theme');
            }
            
            cell.addEventListener('click', () => handleCellClick(row, col));
            cell.addEventListener('mouseover', () => handleCellHover(row, col));
            cell.addEventListener('mouseout', handleCellOut);
            
            boardElement.appendChild(cell);
        }
    }
}

// Check if a cell is selected
function isCellSelected(row, col) {
    return gameState.currentSelection.some(
        pos => pos.row === row && pos.col === col
    );
}

// Check if a cell is used by a found word
function isCellUsed(row, col) {
    for (const word of gameState.foundWords) {
        const path = getWordPath(word);
        if (path.some(pos => pos.row === row && pos.col === col)) {
            return true;
        }
    }
    return false;
}

// Check if a cell is part of a theme word
function isCellTheme(row, col) {
    for (const word of gameState.themeWords) {
        if (gameState.foundWords.has(word)) {
            const path = getWordPath(word);
            if (path.some(pos => pos.row === row && pos.col === col)) {
                return true;
            }
        }
    }
    return false;
}

// Get word path (simplified - in real implementation, would store paths)
function getWordPath(word) {
    // This would be implemented to track actual paths
    return [];
}

// Handle cell click
function handleCellClick(row, col) {
    if (!gameState.gameStarted || gameState.gameWon) return;
    
    // If cell is used by another word, clear selection
    if (isCellUsed(row, col) && !isCellSelected(row, col)) {
        clearSelection();
        return;
    }
    
    // Toggle selection
    const index = gameState.currentSelection.findIndex(
        pos => pos.row === row && pos.col === col
    );
    
    if (index >= 0) {
        // Remove cell from selection
        gameState.currentSelection.splice(index, 1);
    } else {
        // Add cell to selection
        // Check if it's adjacent to the last selected cell
        if (gameState.currentSelection.length > 0) {
            const last = gameState.currentSelection[gameState.currentSelection.length - 1];
            const dr = Math.abs(row - last.row);
            const dc = Math.abs(col - last.col);
            
            // Must be adjacent (including diagonally)
            if (dr > 1 || dc > 1 || (dr === 0 && dc === 0)) {
                return; // Not adjacent
            }
        }
        
        gameState.currentSelection.push({ row, col });
    }
    
    updateCurrentWord();
    renderBoard();
}

// Handle cell hover
function handleCellHover(row, col) {
    // Could implement hover effects here
}

// Handle cell mouse out
function handleCellOut() {
    // Could implement hover effects here
}

// Update current word display
function updateCurrentWord() {
    gameState.currentWord = gameState.currentSelection
        .map(pos => gameState.grid[pos.row][pos.col])
        .join('');
    
    currentWordElement.textContent = gameState.currentWord || 'Select cells to form words';
}

// Clear current selection
function clearSelection() {
    gameState.currentSelection = [];
    gameState.currentWord = '';
    updateCurrentWord();
    renderBoard();
}

// Handle word submission
function submitWord() {
    const word = gameState.currentWord;
    
    if (word.length < 4) {
        showMessage('Words must be at least 4 letters long');
        return;
    }
    
    if (gameState.foundWords.has(word)) {
        showMessage('You already found this word!');
        return;
    }
    
    // Check if word is in the theme
    if (gameState.themeWords.includes(word)) {
        // Valid theme word
        gameState.foundWords.add(word);
        gameState.themeWordsFound++;
        gameState.score += word.length;
        updateHints();
        showMessage(`Found theme word: ${word}!`);
    } else {
        // Check if it's a valid English word (simplified)
        showMessage('Not a valid word in this puzzle');
        return;
    }
    
    clearSelection();
    renderBoard();
    updateUI();
    
    // Check if game is won
    if (gameState.themeWordsFound === gameState.themeWords.length) {
        gameState.gameWon = true;
        showMessage('Congratulations! You found all theme words!', true);
    }
}

// Update hints system
function updateHints() {
    gameState.hintWordsFound++;
    if (gameState.hintWordsFound % 3 === 0) {
        gameState.hintsAvailable++;
        hintCountElement.textContent = gameState.hintsAvailable;
    }
}

// Request hint
function requestHint() {
    if (gameState.hintsAvailable > 0) {
        gameState.hintsAvailable--;
        hintCountElement.textContent = gameState.hintsAvailable;
        
        // Find a theme word not yet found
        const remaining = gameState.themeWords.filter(
            word => !gameState.foundWords.has(word)
        );
        
        if (remaining.length > 0) {
            showMessage(`Hint: Find ${remaining[0]}!`);
        } else {
            showMessage('No hints available - you found all theme words!');
        }
    } else {
        showMessage('No hints available yet. Find more non-theme words!');
    }
}

// Update UI elements
function updateUI() {
    scoreElement.textContent = gameState.score;
    themeCountElement.textContent = `${gameState.themeWordsFound}/${gameState.themeWords.length}`;
    
    // Update completion percentage
    const totalCells = CONFIG.rows * CONFIG.cols;
    const usedCells = gameState.foundWords.size * 5; // Approximate
    const completion = Math.min(100, Math.round((usedCells / totalCells) * 100));
    completionElement.textContent = `${completion}%`;
    
    // Update found words list
    updateFoundWordsList();
}

// Update found words list
function updateFoundWordsList() {
    foundWordsListElement.innerHTML = '';
    
    for (const word of gameState.foundWords) {
        const item = document.createElement('div');
        item.className = 'word-item';
        
        if (gameState.themeWords.includes(word)) {
            item.classList.add('theme-word');
        }
        
        const wordSpan = document.createElement('span');
        wordSpan.className = 'word';
        wordSpan.textContent = word;
        
        const countSpan = document.createElement('span');
        countSpan.className = 'count';
        countSpan.textContent = word.length;
        
        item.appendChild(wordSpan);
        item.appendChild(countSpan);
        foundWordsListElement.appendChild(item);
    }
}

// Show theme name
function showTheme(theme) {
    themeDisplayElement.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
}

// Show message modal
function showMessage(message, isWin = false) {
    modalTitle.textContent = isWin ? '🎉 You Won!' : 'Message';
    modalMessage.textContent = message;
    modal.classList.remove('hidden');
}

// Hide message modal
function hideModal() {
    modal.classList.add('hidden');
}

// Reset game
function resetGame() {
    initGame();
}

// Event listeners
resetButton.addEventListener('click', resetGame);
hintButton.addEventListener('click', requestHint);
modalClose.addEventListener('click', hideModal);

// Handle Enter key for submitting word
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && gameState.currentWord.length > 0) {
        submitWord();
    } else if (e.key === 'Backspace' && gameState.currentWord.length > 0) {
        if (gameState.currentSelection.length > 0) {
            gameState.currentSelection.pop();
            updateCurrentWord();
            renderBoard();
        }
    }
});

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initGame();
});
