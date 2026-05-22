# Chess Master 

A state-of-the-art, chess.com-inspired desktop chess game built with Python, Pygame, and `python-chess`. 

Featuring a gorgeous, responsive dark UI, synthesized wooden sound effects, a fully **Adaptive AI Opponent** (powered by Stockfish), a persistent ELO rating system, a premove engine, and real-time book opening tracking.

---

## Key Features

### Dynamic Adaptive AI (Stockfish-Powered)
Say goodbye to rigid, boring difficulty levels. The AI dynamically calibrates its strength to stay just a small step above your current ELO rating:
* **Challenge Offset:** Ranges from `+175 ELO` (Beginner) down to a tight `+15 ELO` (Super-GM), ensuring games are consistently competitive but never impossibly hard.
* **Realistic Human-Like Tempo:** The engine calculates realistic thinking delay windows that dynamically adapt to the active time control (Bullet, Blitz, Rapid, Unlimited) and scale down in intense time pressure or obvious capture sequences to mimic human players.
* **Calibrated Search Depth & Skill:** Stockfish skill settings and physical minimax search depths are constrained dynamically according to ELO ranges to ensure true ratings alignment.
* *Note: Automatically falls back to an adaptive minimax search engine if `stockfish.exe` is not found.*

### Persistent ELO Rating & Player Stats
* Track your progress across sessions! Your ELO, Peak ELO, and comprehensive Win/Loss/Draw stats are persisted inside `player_data.json`.
* Uses standard chess.com K-factor scaling (`K=40` for provisional/under-1000 ELO players, scaling down to `K=10` for masters) to calculate precise ratings adjustments dynamically.

### Always-Visible Theory Detector (Book Opening)
* **Real-time Detection:** Tracks your move sequence dynamically against an extensive openings book database.
* **Always-Visible UI Indicator:** Anchored directly in the sidebar from move 0. Starts as a clean, sleek, muted `Standard Play` banner, and dynamically transforms into a brilliant gold-accented card (e.g., `⚡ BOOK OPENING: Sicilian Defense` or `Italian Game`) and updates the top navigation bar title the moment standard theory is matched.

### Professional Premove System
* Make your moves instantly! You can queue structural legal moves or obvious recaptures during the AI's turn. 
* Highlights premoves in red and executes them the millisecond the opponent completes their turn.

### Modern Chess.com-Inspired UI
* **Splash Dashboard:** Minimalist double-panel welcome screen showing player card stats (Wins/Losses/Draws, ELO, Peak ELO) alongside an AI connectivity status badge.
* **Setup Screen:** Interactive presets with custom-drawn **vector selection icons** (White Crown, Black Crown, Split-color Random Coin) that scale elegantly and eliminate broken empty rectangles (`▯`) on all operating systems.
* **Interactive Settings Overlay:** Toggle sound effects or switch instantly between 5 premium visual board themes (*Green, Blue, Lichess Brown, Purple, and Dark*) featuring centered visual 2x2 grid previews.
* **Responsive Vector Spacing:** Automatically scales, center-aligns, and recalculates coordinates on screen size maximization or manual resizing.
* **Evaluation Bar:** Side-mounted vertical visual graph illustrating engine evaluation values (`+` / `-` scores or `Mate in N` alerts) in real-time.
* **Scrollable SAN Move Log:** Clicking on past moves or using the left/right arrow keys (`←` / `→`) lets you dynamically review position history.

### Pure Synthesized Audio
Synthesizes rich wooden board thocks, bright promotion chimes, dual castling chords, and victory/defeat fanfares programmatically—yielding premium sounds without needing any extra asset files.

---

## Preset Time Controls
Choose from 10 popular chess.com presets with full increment support:
* **Bullet:** `1+0`, `2+1`
* **Blitz:** `3+0`, `3+2`, `5+0`, `5+3`
* **Rapid:** `10+0`, `15+10`, `30+0`
* **Unlimited:** `INF` (features elegant turn-highlighted infinity `"∞"` clock widgets)

---

## Setup & Installation

### Requirements
* Python `3.10` or newer
* `pygame`
* `python-chess`

### Quick Install
Install the official Pygame and Python-Chess dependencies:
```bash
pip install pygame python-chess
```

### Run the Game
Double-click `Play Chess.bat` (Windows) or launch it directly from your terminal:
```bash
python chess_game.py
```

---

## Controls & Navigation

* **Drag-and-Drop / Click-to-Move:** Click a piece to view highlighted legal dots, and click or drag-and-drop onto the destination to move.
* **Promotion:** A premium vertical pop-up overlay lets you select Queen, Rook, Bishop, or Knight when a pawn reaches the back rank.
* **Position Review:** Press the **Left Arrow key (`←`)** to step backward through moves, **Right Arrow key (`→`)** to step forward, or click directly on any move in the scrollable log.
* **Cancel/Clear:** Right-click (`Button 3`) on the board to deselect pieces or cancel premoves instantly.
