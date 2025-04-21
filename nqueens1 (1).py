import pygame
import numpy as np
import random
import math
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
BOARD_SIZE = 8
CELL_SIZE = WIDTH // BOARD_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (255, 215, 0)  # Gold color for highlighting moves
RED = (255, 0, 0)  # For conflicts
GREEN = (0, 255, 0)  # For successful placements
FONT_SIZE = 24
DELAY = 0.5  # Seconds between moves for visualization

# Initialize font
pygame.font.init()
font = pygame.font.SysFont('Arial', FONT_SIZE)

# Try to load Queen Image, use fallback if image not found
try:
    QUEEN_IMAGE = pygame.image.load("queen.png")
    QUEEN_IMAGE = pygame.transform.scale(QUEEN_IMAGE, (CELL_SIZE, CELL_SIZE))
    use_image = True
except:
    use_image = False
    print("Queen image not found. Using 'Q' as fallback.")

# Initialize Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Queens Problem")

# Function to count conflicts (lower is better)
def count_conflicts(board):
    conflicts = 0
    for i in range(BOARD_SIZE):
        for j in range(i + 1, BOARD_SIZE):
            # Check for same column
            if board[i] == board[j]:
                conflicts += 1
            # Check for diagonal conflicts
            if abs(board[i] - board[j]) == abs(i - j):
                conflicts += 1
    return conflicts

# Function to draw the board
def draw_board(board, highlighted_row=None, conflict_count=None, algorithm_name=""):
    screen.fill(WHITE)
    
    # Draw the chess board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Highlight the row being modified if specified
    if highlighted_row is not None:
        pygame.draw.rect(screen, HIGHLIGHT, (0, highlighted_row * CELL_SIZE, WIDTH, CELL_SIZE), 3)
    
    # Draw queens
    for row in range(BOARD_SIZE):
        col = board[row]
        if use_image:
            screen.blit(QUEEN_IMAGE, (col * CELL_SIZE, row * CELL_SIZE))
        else:
            # Fallback: Draw a circle with 'Q' text
            cell_center = (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
            pygame.draw.circle(screen, RED if highlighted_row == row else WHITE, cell_center, CELL_SIZE // 2 - 5)
            text = font.render('Q', True, BLACK)
            text_rect = text.get_rect(center=cell_center)
            screen.blit(text, text_rect)
    
    # Display conflict count and algorithm name
    if conflict_count is not None:
        conflict_text = font.render(f"Conflicts: {conflict_count}", True, BLACK)
        screen.blit(conflict_text, (10, HEIGHT - 60))
    
    if algorithm_name:
        algo_text = font.render(algorithm_name, True, BLACK)
        screen.blit(algo_text, (10, HEIGHT - 30))
    
    pygame.display.update()
    handle_events()
    time.sleep(DELAY)  # Add delay for visualization

# Function to handle pygame events
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# Generate a random initial board
def generate_initial_board():
    return np.random.randint(0, BOARD_SIZE, BOARD_SIZE)

# Get all neighbors by moving one queen
def get_neighbors(board):
    neighbors = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if col != board[row]:
                neighbor = board.copy()
                neighbor[row] = col
                neighbors.append(neighbor)
    return neighbors

# Get random neighbor by moving one queen
def get_random_neighbor(board):
    row = random.randint(0, BOARD_SIZE - 1)
    col = random.randint(0, BOARD_SIZE - 1)
    while col == board[row]:  # Ensure we're actually moving
        col = random.randint(0, BOARD_SIZE - 1)
    
    neighbor = board.copy()
    neighbor[row] = col
    return neighbor, row  # Return the row that was changed for highlighting

# 1. Hill Climbing
def hill_climbing():
    board = generate_initial_board()
    current_conflicts = count_conflicts(board)
    
    draw_board(board, None, current_conflicts, "Hill Climbing")
    
    iterations = 0
    max_iterations = 100  # Prevent infinite loops
    
    while iterations < max_iterations:
        iterations += 1
        best_neighbor = None
        best_conflicts = current_conflicts
        best_row = None
        
        neighbors = get_neighbors(board)
        for neighbor in neighbors:
            conflicts = count_conflicts(neighbor)
            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_neighbor = neighbor
                # Find which row changed
                for row in range(BOARD_SIZE):
                    if neighbor[row] != board[row]:
                        best_row = row
                        break
        
        if best_conflicts >= current_conflicts:  # Local minimum reached
            break
        
        board = best_neighbor
        current_conflicts = best_conflicts
        draw_board(board, best_row, current_conflicts, "Hill Climbing")
        
        if current_conflicts == 0:  # Solution found
            break
    
    return board, current_conflicts

# 2. Simulated Annealing
def simulated_annealing():
    board = generate_initial_board()
    current_conflicts = count_conflicts(board)
    
    draw_board(board, None, current_conflicts, "Simulated Annealing")
    
    temperature = 1.0
    cooling_rate = 0.95
    min_temperature = 0.01
    iterations_per_temp = 5
    
    while temperature > min_temperature:
        for _ in range(iterations_per_temp):
            neighbor, changed_row = get_random_neighbor(board)
            neighbor_conflicts = count_conflicts(neighbor)
            
            delta_e = neighbor_conflicts - current_conflicts
            
            # Accept if better or with a probability
            if delta_e < 0 or random.random() < math.exp(-delta_e / temperature):
                board = neighbor
                current_conflicts = neighbor_conflicts
                draw_board(board, changed_row, current_conflicts, "Simulated Annealing")
            
            if current_conflicts == 0:  # Solution found
                return board, current_conflicts
        
        temperature *= cooling_rate
    
    return board, current_conflicts

# 3. Local Beam Search
def local_beam_search(k=5):
    # Generate k random states
    states = [generate_initial_board() for _ in range(k)]
    states_conflicts = [count_conflicts(state) for state in states]
    
    # Display initial states
    best_state_idx = np.argmin(states_conflicts)
    draw_board(states[best_state_idx], None, states_conflicts[best_state_idx], f"Local Beam Search (k={k})")
    
    max_iterations = 50
    iterations = 0
    
    while iterations < max_iterations:
        iterations += 1
        
        # Generate all neighbors for all current states
        all_successors = []
        for state in states:
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if col != state[row]:
                        successor = state.copy()
                        successor[row] = col
                        conflict = count_conflicts(successor)
                        all_successors.append((successor, conflict, row))
        
        # Sort successors by conflict count
        all_successors.sort(key=lambda x: x[1])
        
        # Take the k best successors
        new_states = []
        new_conflicts = []
        changed_rows = []
        
        for i in range(min(k, len(all_successors))):
            new_states.append(all_successors[i][0])
            new_conflicts.append(all_successors[i][1])
            changed_rows.append(all_successors[i][2])
        
        # Update states and visualize the best one
        states = new_states
        states_conflicts = new_conflicts
        
        best_state_idx = np.argmin(states_conflicts)
        best_conflict = states_conflicts[best_state_idx]
        
        draw_board(states[best_state_idx], changed_rows[best_state_idx], 
                  best_conflict, f"Local Beam Search (k={k})")
        
        if best_conflict == 0:  # Solution found
            return states[best_state_idx], best_conflict
    
    # Return the best state found
    best_state_idx = np.argmin(states_conflicts)
    return states[best_state_idx], states_conflicts[best_state_idx]

# Function to compare algorithms
def compare_algorithms(num_trials=10):
    results = {
        "Hill Climbing": {"success": 0, "avg_conflicts": 0, "avg_time": 0},
        "Sim_Ann": {"success": 0, "avg_conflicts": 0, "avg_time": 0},
        "LBS": {"success": 0, "avg_conflicts": 0, "avg_time": 0}
    }
    
    # Set a shorter delay for comparison runs
    global DELAY
    original_delay = DELAY
    DELAY = 0.1  # Faster execution for comparison
    
    screen.fill(WHITE)
    running_text = font.render("Running comparison...", True, BLACK)
    screen.blit(running_text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.update()
    
    for algorithm in results.keys():
        total_conflicts = 0
        total_time = 0
        
        for trial in range(num_trials):
            start_time = time.time()
            
            if algorithm == "Hill Climbing":
                board, conflicts = hill_climbing()
            elif algorithm == "Simulated Annealing":
                board, conflicts = simulated_annealing()
            else:  # Local Beam Search
                board, conflicts = local_beam_search()
            
            end_time = time.time()
            trial_time = end_time - start_time
            
            # Update results
            if conflicts == 0:
                results[algorithm]["success"] += 1
            total_conflicts += conflicts
            total_time += trial_time
            
            # Update the screen with progress
            screen.fill(WHITE)
            progress = font.render(f"Testing {algorithm}: {trial+1}/{num_trials}", True, BLACK)
            screen.blit(progress, (WIDTH // 2 - 120, HEIGHT // 2))
            pygame.display.update()
            handle_events()
        
        # Calculate averages
        results[algorithm]["avg_conflicts"] = total_conflicts / num_trials
        results[algorithm]["avg_time"] = total_time / num_trials
    
    # Restore original delay
    DELAY = original_delay
    
    return results

# Function to display the comparison results
def display_comparison_results(results):
    screen.fill(WHITE)
    title = font.render("Algorithm Comparison Results", True, BLACK)
    screen.blit(title, (WIDTH // 2 - 150, 50))
    
    y_pos = 100
    headers = ["Algorithm", "Success Rate", "Avg Conflicts", "Avg Time (s)"]
    
    # Display headers
    for i, header in enumerate(headers):
        text = font.render(header, True, BLACK)
        screen.blit(text, (50 + i * 140, y_pos))
    
    # Display results for each algorithm
    y_pos += 40
    for algorithm, data in results.items():
        success_rate = f"{data['success'] * 10}%"  # Assuming 10 trials
        avg_conflicts = f"{data['avg_conflicts']:.2f}"
        avg_time = f"{data['avg_time']:.2f}"
        
        algo_text = font.render(algorithm, True, BLACK)
        success_text = font.render(success_rate, True, BLACK)
        conflicts_text = font.render(avg_conflicts, True, BLACK)
        time_text = font.render(avg_time, True, BLACK)
        
        screen.blit(algo_text, (50, y_pos))
        screen.blit(success_text, (190, y_pos))
        screen.blit(conflicts_text, (330, y_pos))
        screen.blit(time_text, (470, y_pos))
        
        y_pos += 30
    
    # Display instructions
    instruction = font.render("Press any key to continue", True, BLACK)
    screen.blit(instruction, (WIDTH // 2 - 120, HEIGHT - 50))
    
    pygame.display.update()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

# Function to display the final solved board
def display_final_board(board, algorithm_name):
    conflicts = count_conflicts(board)
    solved = conflicts == 0
    
    screen.fill(WHITE)
    
    # Draw the chess board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw queens with visual indicator for conflicts
    for row in range(BOARD_SIZE):
        col = board[row]
        
        # Check if this queen is in conflict
        in_conflict = False
        for other_row in range(BOARD_SIZE):
            if other_row != row:
                if board[other_row] == col or abs(board[other_row] - col) == abs(other_row - row):
                    in_conflict = True
                    break
        
        if use_image:
            screen.blit(QUEEN_IMAGE, (col * CELL_SIZE, row * CELL_SIZE))
            # Draw a highlight circle around the queen if it's in conflict
            if in_conflict:
                pygame.draw.circle(screen, RED, 
                                 (col * CELL_SIZE + CELL_SIZE // 2, 
                                  row * CELL_SIZE + CELL_SIZE // 2), 
                                 CELL_SIZE // 2, 3)
        else:
            # Fallback: Draw a circle with 'Q' text
            cell_center = (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
            pygame.draw.circle(screen, RED if in_conflict else GREEN, cell_center, CELL_SIZE // 2 - 5)
            text = font.render('Q', True, BLACK)
            text_rect = text.get_rect(center=cell_center)
            screen.blit(text, text_rect)
    
    # Display information about the solution
    title = font.render(f"Final Board - {algorithm_name}", True, BLACK)
    screen.blit(title, (WIDTH // 2 - 150, HEIGHT - 100))
    
    status = font.render(f"{'SOLVED!' if solved else 'Not Solved'} - Conflicts: {conflicts}", True, 
                        GREEN if solved else RED)
    screen.blit(status, (WIDTH // 2 - 150, HEIGHT - 70))
    
    instruction = font.render("Press any key to continue", True, BLACK)
    screen.blit(instruction, (WIDTH // 2 - 120, HEIGHT - 40))
    
    pygame.display.update()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

# Main function
# Modified main function
def main():
    pygame.init()
    
    running = True
    results = []
    
    while running:
        screen.fill(WHITE)
        title = font.render("8-Queens Problem Solver", True, BLACK)
        screen.blit(title, (WIDTH // 2 - 120, 50))
        
        # Menu options
        options = [
            "1. Run Hill Climbing",
            "2. Run Simulated Annealing",
            "3. Run Local Beam Search",
            "4. Compare All Algorithms",
            "5. Quit"
        ]
        
        for i, option in enumerate(options):
            y_pos = 150 + i * 40
            text = font.render(option, True, BLACK)
            screen.blit(text, (WIDTH // 2 - 100, y_pos))
        
        # Display results from previous runs
        y_pos = 400
        for i, result in enumerate(results):
            algo_name, conflicts = result
            result_text = font.render(f"{algo_name}: {conflicts} conflicts", True, BLACK)
            screen.blit(result_text, (WIDTH // 2 - 150, y_pos + i * 30))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    board, conflicts = hill_climbing()
                    results.append(("Hill Climbing", conflicts))
                    display_final_board(board, "Hill Climbing")
                elif event.key == pygame.K_2:
                    board, conflicts = simulated_annealing()
                    results.append(("Sm_A", conflicts))
                    display_final_board(board, "Sm_A")
                elif event.key == pygame.K_3:
                    board, conflicts = local_beam_search()
                    results.append(("LBS", conflicts))
                    display_final_board(board, "LBS")
                elif event.key == pygame.K_4:
                    comparison_results = compare_algorithms()
                    display_comparison_results(comparison_results)
                elif event.key == pygame.K_5 or event.key == pygame.K_q:
                    running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()