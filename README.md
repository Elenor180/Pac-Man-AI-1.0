# Pac-Man-AI-1.0
Demonstration of A* Search for finding best path applied on Pac Man as he navigates his world 

## Pac-Man AI with Dynamic Behavior & A* Search
An AI-powered Pac-Man game built in Python (Pygame) with dynamic ghost behavior, adjustable AI priorities, and power pellet mechanics.

#### Project Overview
This project is a custom Pac-Man implementation where the main character, Pac-Man, uses a simple AI system to navigate the maze. 
The AI dynamically adjusts its behavior based on real-time game states, such as:

Proximity of ghosts (danger levels)

Collection of regular dots or power pellets

Activation of power pellets, which makes ghosts vulnerable

The core decision-making uses A Search Algorithm* to find paths in the maze based on multiple factors:

Distance to target (dots, pellets, ghosts)

Danger zones marked by nearby ghosts

Escape urgency when chased

Dot collection priority for maximizing score

#### AI Mechanics & Behavior
A Pathfinding* guides Pac-Man towards goals like dots or power pellets.

When in danger, Pac-Man prioritizes finding the safest route away from ghosts.

If a power pellet is active, Pac-Man actively chases vulnerable ghosts for bonus points.

Adjustable parameters:

Escape Urgency (↑/↓) — Changes how quickly Pac-Man tries to flee when in danger.

Dot Priority (←/→) — Adjusts the importance Pac-Man gives to collecting dots.

#### Ghost AI Behavior
Each ghost has:

A random aggression factor that determines if it chases Pac-Man.

A speed level affecting how often it moves.

Behavior change when vulnerable (tries to run away).

Ghosts respawn after being eaten.

#### Features Summary
Grid-based movement using A* pathfinding.

Real-time adjustable AI parameters via keyboard.

Vulnerable ghost state with visual flashing indicators.

Score system with multiplier for consecutive ghost captures.

Full power pellet mechanics with timers.

Victory and Game Over states.

Fully resizable to a 20x20 maze with balanced gameplay.

# Why A* Search Isn't Always Optimal Here
While A Search* is a classic algorithm for finding the shortest path, it doesn’t always yield optimal gameplay behavior in this context due to:

Dynamic Dangers: The positions of ghosts change constantly, making static pathfinding results outdated within a few frames.

No Predictive Modeling: The AI reacts to the current state only. Without prediction of ghost movement, Pac-Man may choose a seemingly optimal path that becomes unsafe immediately after.

Multi-Objective Conflicts: Balancing dot collection, ghost avoidance, and power pellet usage often leads A* to compute suboptimal paths when objectives conflict.

Real-Time Adjustments Needed: To truly optimize Pac-Man’s survival and scoring, more adaptive strategies like predictive ghost modeling, Monte Carlo Tree Search, or Reinforcement Learning would be required.

In essence, A works well for static mazes but struggles when the environment changes rapidly*, as in this game.

#### Controls
Key	Function
↑	Increase Escape Urgency
↓	Decrease Escape Urgency
←	Decrease Dot Priority
→	Increase Dot Priority
R	Restart the game after Game Over or Victory

#### How to Run
Install Python 3.x and pygame:

bash
Copy
Edit
pip install pygame
Download the project files.

Run:

bash
Copy
Edit
python pacman_ai_improved.py

#### Screenshots
<img width="722" height="681" alt="image" src="https://github.com/user-attachments/assets/66d26920-af0d-4d2b-8f81-dbbd84fb93f2" />


#### Future Improvements (Open Ideas)
Implement predictive ghost path modeling.

Use Minimax or MCTS for smarter path decisions.

Add scoring heuristics for safer dot collection.

Introduce reinforcement learning for AI training.
