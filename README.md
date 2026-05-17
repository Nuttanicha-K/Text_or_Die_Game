# Text or Die

A simple word-typing tower game made with Python and Pygame.
Players must type valid words based on a given category before the rising water catches the tower.

---

## Gameplay

In each round, the game randomly selects a category:

* Fruits
* Countries
* Animals

The player types a valid word from the selected category.

### Rules

* Correct words add blocks to the tower
* Longer words give higher scores
* Repeated words are not allowed
* Wrong or repeated answers cause the water to rise
* If the water reaches the top block, the game ends

The camera automatically follows the tower as it grows upward.

---

## Features

* Animated water with wave effects
* Smooth camera movement
* Score system
* Round progression difficulty
* Background music support
* Restart system
* Custom category word lists
* Transparent UI elements

---

## Requirements

Install Python packages:

```bash
pip install pygame
```

---

## Project Structure

```text
project/
│
├── main.py
├── fruits.txt
├── countries.txt
├── animals.txt
├── music.mp3
├── Bg1.png
└── README.md
```

---

## Word List Format

Each text file should contain one word per line.

Example (`fruits.txt`):

```text
apple
banana
orange
mango
```

---

## How to Run

```bash
python main.py
```

---

## Controls

| Key          | Action                  |
| ------------ | ----------------------- |
| Type letters | Enter a word            |
| Enter        | Submit word             |
| Backspace    | Delete character        |
| R            | Restart after Game Over |

---

## Game Mechanics

### Water System

The water rises dynamically depending on:

* average length of submitted words
* current round number

As rounds increase, penalties become stronger.

---

### Score Formula

```text
score += word_length × 10
```

---

### Camera System

The camera smoothly follows the tower:

* moves upward when the tower grows
* keeps gameplay centered on screen

---

## Assets

The game uses:

* `music.mp3` for background music
* `Bg1.png` as the background image

If these files are missing, the game still runs with fallback behavior.

---

## Classes

### `Block`

Represents a single letter block in the tower.

### `Water`

Handles:

* water level
* animation
* wave rendering
* rising mechanics

---

## Technologies Used

* Python
* Pygame
* Object-Oriented Programming (OOP)

---
