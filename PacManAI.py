import pygame
import random
from collections import deque
import heapq
import math

pygame.init()

# Game Constants
ROWS, COLS = 20, 20
CELL_SIZE = 30
WIDTH, HEIGHT = CELL_SIZE * COLS, CELL_SIZE * ROWS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GHOST_COLORS = [RED, PINK, CYAN, ORANGE]
VULNERABLE_COLOR = (100, 100, 255)
FLASH_COLOR = (200, 200, 255)

# Directions
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Game Parameters
ESCAPE_URGENCY = 1
DANGER_THRESHOLD = 2
DOT_PRIORITY = 0.4
POWER_PELLET_DURATION = 40  # Increased duration
FLASH_START = 10  # More flashing time
PACMAN_SPEED = 1.5  # Pac-Man moves faster

# Maze Layout
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

def get_random_empty_position():
    empty_positions = [(r, c) for r in range(ROWS) for c in range(COLS) 
                      if maze[r][c] in [0, 2] and (r, c) != tuple(pacman)]
    return random.choice(empty_positions) if empty_positions else (1, 1)

# Game state
pacman = [1, 1]
dots = {(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 0}
power_pellets = {(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 2}
score = 0
power_pellet_active = False
power_pellet_timer = 0
ghosts_eaten = 0

# Ghosts - with varied speeds
ghosts = []
for i in range(4):
    pos = get_random_empty_position()
    ghosts.append({
        'pos': [pos[0], pos[1]],
        'color': GHOST_COLORS[i],
        'aggression': random.uniform(0.05, 0.8),
        'speed': random.choice([1, 1, 1, 1]),  # Normal speed
        'vulnerable_speed': 2,  # Slower when vulnerable
        'counter': 0,
        'vulnerable': False,
        'eaten': False
    })

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man with Power Pellets")
clock = pygame.time.Clock()

# Danger distance calculation
def calculate_danger_distance(current_pos):
    min_distance = float('inf')
    for ghost in ghosts:
        if ghost['eaten'] or (ghost['vulnerable'] and power_pellet_active):
            continue
            
        dist = abs(current_pos[0] - ghost['pos'][0]) + abs(current_pos[1] - ghost['pos'][1])
        if dist < min_distance:
            min_distance = dist
    
    if min_distance == float('inf'):
        return 0
        
    return min(1.0, 1.0 - (min_distance / (ROWS + COLS)))

# Manhattan distance heuristic
def heuristic(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# Optimized A* search
path_cache = {}
def a_star_search(start, goal, danger_level, danger_weight=1.0):
    cache_key = (start, goal, danger_weight)
    if cache_key in path_cache:
        return path_cache[cache_key]
    
    if start == goal:
        return [], 0

    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        current = heapq.heappop(frontier)[1]
        
        if current == goal:
            break
        
        for direction in DIRECTIONS:
            next_pos = (current[0] + direction[0], current[1] + direction[1])
            if (0 <= next_pos[0] < ROWS and 0 <= next_pos[1] < COLS and 
                maze[next_pos[0]][next_pos[1]] in [0, 2]):
                
                new_cost = cost_so_far[current] + 1
                new_cost += danger_level.get(next_pos, 0) * 2 * danger_weight
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
    
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current, None)
        if current is None:
            result = (None, float('inf'))
            path_cache[cache_key] = result
            return result
    
    path.reverse()
    result = (path, cost_so_far.get(goal, float('inf')))
    path_cache[cache_key] = result
    return result

# Improved escape path for vulnerable ghosts
def get_path_away_from(ghost_pos, pacman_pos):
    best_dir = None
    max_dist = -1
    
    for direction in DIRECTIONS:
        new_row = ghost_pos[0] + direction[0]
        new_col = ghost_pos[1] + direction[1]
        if (0 <= new_row < ROWS and 0 <= new_col < COLS and 
            maze[new_row][new_col] in [0, 2]):
            dist = math.sqrt((new_row - pacman_pos[0])**2 + (new_col - pacman_pos[1])**2)
            if dist > max_dist:
                max_dist = dist
                best_dir = (new_row, new_col)
    
    if best_dir:
        return [best_dir]
    return None

# Ghost pathfinding to Pac-Man
def get_path_for_ghost(ghost):
    start = (ghost['pos'][0], ghost['pos'][1])
    target = (pacman[0], pacman[1])
    path, _ = a_star_search(start, target, {}, 0)
    return path

# Predict ghost positions for danger zone
def predict_ghost_positions(ghost, steps=2):
    positions = {tuple(ghost['pos'])}
    for direction in DIRECTIONS:
        nr, nc = ghost['pos'][0] + direction[0], ghost['pos'][1] + direction[1]
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] in [0, 2]:
            positions.add((nr, nc))
    return positions

# Danger zone with predicted positions
def get_ghost_danger_zone_predicted():
    danger = set()
    danger_level = {}

    for ghost in ghosts:
        if ghost['eaten'] or (power_pellet_active and ghost['vulnerable']):
            continue
            
        positions = predict_ghost_positions(ghost, steps=1)
        for pos in positions:
            level = 2 if pos == tuple(ghost['pos']) else 1
            danger.add(pos)
            if pos not in danger_level or level > danger_level[pos]:
                danger_level[pos] = level
    
    return danger, danger_level

# Dead end detection
def is_dead_end(position):
    open_paths = 0
    for direction in DIRECTIONS:
        nr, nc = position[0] + direction[0], position[1] + direction[1]
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] in [0, 2]:
            open_paths += 1
    return open_paths <= 1

# Find safest immediate area
def find_safest_open_area(current_pos, danger_level):
    safest_pos = current_pos
    safest_score = -1
    
    # Only check immediate neighbors for performance
    for direction in DIRECTIONS:
        new_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
        if (0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and 
            maze[new_pos[0]][new_pos[1]] in [0, 2]):
            safety = 1 - (danger_level.get(new_pos, 0) / 2.0)
            if safety > safest_score:
                safest_score = safety
                safest_pos = new_pos
                
    return safest_pos

# Improved Pac-Man pathfinding
def get_best_path():
    global path_cache
    path_cache = {}  # Clear cache each frame
    
    danger, danger_level = get_ghost_danger_zone_predicted()
    current_pos = (pacman[0], pacman[1])
    danger_score = calculate_danger_distance(current_pos)

    # If power pellet is active, prioritize chasing vulnerable ghosts
    if power_pellet_active:
        vulnerable_ghosts = [g for g in ghosts if g['vulnerable'] and not g['eaten']]
        if vulnerable_ghosts:
            # Find the closest vulnerable ghost
            closest_ghost = min(vulnerable_ghosts, 
                               key=lambda g: heuristic(current_pos, tuple(g['pos'])))
            path, _ = a_star_search(current_pos, tuple(closest_ghost['pos']), danger_level, 0.5)
            if path:
                return path

    # If in danger, move to safest nearby area
    if danger_score > ESCAPE_URGENCY or current_pos in danger:
        safe_zone = find_safest_open_area(current_pos, danger_level)
        if safe_zone != current_pos:
            path, _ = a_star_search(current_pos, safe_zone, danger_level, 2.0)
            if path:
                return path

    # Find path to nearest dot or power pellet
    targets = list(dots.union(power_pellets))
    if not targets:
        return None
        
    # Only consider the 3 closest targets for performance
    closest_targets = sorted(targets, key=lambda t: heuristic(current_pos, t))[:3]
    
    best_path = None
    best_cost = float('inf')
    
    for target in closest_targets:
        if is_dead_end(target) and danger_score > 0.3:
            continue
            
        adjusted_weight = (1 - DOT_PRIORITY) * danger_score
        path, cost = a_star_search(current_pos, target, danger_level, adjusted_weight)
        if path and cost < best_cost:
            best_path = path
            best_cost = cost

    # Fallback if no path found - move randomly
    if best_path is None:
        possible_moves = []
        for direction in DIRECTIONS:
            new_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            if (0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and 
                maze[new_pos[0]][new_pos[1]] in [0, 2]):
                possible_moves.append(new_pos)
        if possible_moves:
            return [random.choice(possible_moves)]
    
    return best_path

# Improved ghost movement with vulnerability slowdown
def move_ghosts():
    global ghosts_eaten, score
    
    for ghost in ghosts:
        if ghost['eaten']:
            ghost['counter'] += 1
            if ghost['counter'] > 20:
                pos = get_random_empty_position()
                ghost['pos'] = [pos[0], pos[1]]
                ghost['eaten'] = False
                ghost['vulnerable'] = False
            continue
            
        ghost['counter'] += 1
        
        # Determine movement speed based on vulnerability
        if ghost['vulnerable']:
            # Ghosts are slower when vulnerable
            if ghost['counter'] % ghost['vulnerable_speed'] != 0:
                continue
        else:
            if ghost['counter'] % ghost['speed'] != 0:
                continue
            
        if power_pellet_active and ghost['vulnerable']:
            # Try to escape from Pac-Man
            escape_path = get_path_away_from(tuple(ghost['pos']), tuple(pacman))
            if escape_path:
                ghost['pos'][0], ghost['pos'][1] = escape_path[0]
            else:
                # If can't escape, move randomly
                direction = random.choice(DIRECTIONS)
                new_row = ghost['pos'][0] + direction[0]
                new_col = ghost['pos'][1] + direction[1]
                if 0 <= new_row < ROWS and 0 <= new_col < COLS and maze[new_row][new_col] in [0, 2]:
                    ghost['pos'][0], ghost['pos'][1] = new_row, new_col
        elif random.random() < ghost['aggression']:
            path = get_path_for_ghost(ghost)
            if path and len(path) > 0:
                ghost['pos'][0], ghost['pos'][1] = path[0]
        else:
            # Random movement
            direction = random.choice(DIRECTIONS)
            new_row = ghost['pos'][0] + direction[0]
            new_col = ghost['pos'][1] + direction[1]
            if 0 <= new_row < ROWS and 0 <= new_col < COLS and maze[new_row][new_col] in [0, 2]:
                ghost['pos'][0], ghost['pos'][1] = new_row, new_col

# Reset game function
def reset_game():
    global pacman, dots, power_pellets, score, power_pellet_active, power_pellet_timer, ghosts_eaten, ghosts
    
    pacman = [1, 1]
    dots = {(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 0}
    power_pellets = {(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 2}
    score = 0
    power_pellet_active = False
    power_pellet_timer = 0
    ghosts_eaten = 0
    
    ghosts = []
    for i in range(4):
        pos = get_random_empty_position()
        ghosts.append({
            'pos': [pos[0], pos[1]],
            'color': GHOST_COLORS[i],
            'aggression': random.uniform(0.05, 0.8),
            'speed': random.choice([1, 1, 1, 1]),
            'vulnerable_speed': 2,
            'counter': 0,
            'vulnerable': False,
            'eaten': False
        })

running = True
game_over = False
victory = False
frame_count = 0
pacman_move_counter = 0

while running:
    frame_count += 1
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and (game_over or victory):
            if event.key == pygame.K_r:
                reset_game()
                game_over = False
                victory = False
        if event.type == pygame.KEYDOWN and not game_over and not victory:
            if event.key == pygame.K_UP:
                ESCAPE_URGENCY = min(ESCAPE_URGENCY + 0.1, 1.0)
            elif event.key == pygame.K_DOWN:
                ESCAPE_URGENCY = max(ESCAPE_URGENCY - 0.1, 0.0)
            elif event.key == pygame.K_LEFT:
                DOT_PRIORITY = max(DOT_PRIORITY - 0.1, 0.0)
            elif event.key == pygame.K_RIGHT:
                DOT_PRIORITY = min(DOT_PRIORITY + 0.1, 1.0)
    
    if not game_over and not victory:
        if power_pellet_active:
            power_pellet_timer -= 1
            if power_pellet_timer <= 0:
                power_pellet_active = False
                for ghost in ghosts:
                    ghost['vulnerable'] = False
        
        move_ghosts()
        
        # Check for collisions
        for ghost in ghosts:
            if not ghost['eaten'] and (pacman[0], pacman[1]) == tuple(ghost['pos']):
                if power_pellet_active and ghost['vulnerable']:
                    ghost['eaten'] = True
                    ghost['counter'] = 0
                    ghosts_eaten += 1
                    score += (2 ** ghosts_eaten) * 100
                elif not (power_pellet_active and ghost['vulnerable']):
                    game_over = True
        
        if game_over:
            continue
        
        # Move Pac-Man faster
        pacman_move_counter += PACMAN_SPEED
        if pacman_move_counter >= 1:
            pacman_move_counter = 0
            path = get_best_path()
            if path and len(path) > 0:
                pacman[0], pacman[1] = path[0]
            
            # Check for dot or power pellet consumption
            pos = (pacman[0], pacman[1])
            if pos in dots:
                dots.remove(pos)
                score += 10
            elif pos in power_pellets:
                power_pellets.remove(pos)
                score += 50
                power_pellet_active = True
                power_pellet_timer = POWER_PELLET_DURATION
                ghosts_eaten = 0
                for ghost in ghosts:
                    if not ghost['eaten']:
                        ghost['vulnerable'] = True
            
            if not dots and not power_pellets:
                victory = True
    
    # Draw maze
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == 1:
                pygame.draw.rect(screen, BLUE, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif (r, c) in dots:
                pygame.draw.circle(screen, WHITE,
                                 (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2), 3)
            elif (r, c) in power_pellets:
                pygame.draw.circle(screen, WHITE,
                                 (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2), 8)
    
    # Draw Pac-Man
    pygame.draw.circle(screen, YELLOW,
                       (pacman[1] * CELL_SIZE + CELL_SIZE // 2, pacman[0] * CELL_SIZE + CELL_SIZE // 2),
                       CELL_SIZE // 3)
    
    # Draw ghosts
    for ghost in ghosts:
        if ghost['eaten']:
            continue
            
        if ghost['vulnerable']:
            if power_pellet_timer <= FLASH_START and power_pellet_timer % 2 == 0:
                color = FLASH_COLOR
            else:
                color = VULNERABLE_COLOR
        else:
            color = ghost['color']
            
        pygame.draw.circle(screen, color,
                           (ghost['pos'][1] * CELL_SIZE + CELL_SIZE // 2, 
                            ghost['pos'][0] * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 3)
    
    # Draw UI
    font = pygame.font.SysFont(None, 24)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    if power_pellet_active:
        pellet_text = font.render(f"POWER: {power_pellet_timer}", True, CYAN)
        screen.blit(pellet_text, (WIDTH - 100, 10))
    
    if game_over:
        font = pygame.font.SysFont(None, 36)
        text = font.render("GAME OVER! Press R to restart", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    elif victory:
        font = pygame.font.SysFont(None, 36)
        text = font.render("VICTORY! Press R to restart", True, YELLOW)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    
    # Draw controls
    controls_font = pygame.font.SysFont(None, 18)
    controls_text = controls_font.render("Arrow Keys: Adjust Pac-Man Behavior  R: Restart", True, WHITE)
    screen.blit(controls_text, (10, HEIGHT - 30))
    
    param_text = controls_font.render(f"Escape Urgency: {ESCAPE_URGENCY:.1f}  Dot Priority: {DOT_PRIORITY:.1f}", True, WHITE)
    screen.blit(param_text, (10, HEIGHT - 50))
    
    pygame.display.flip()
    clock.tick(8)  # Smooth gameplay

pygame.quit()