import pygame
import sys
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass
from collections import deque
import copy

@dataclass
class CycleResult:
    forms_cycle: bool
    steps_before_cycle: int
    cycle_length: int
    visited_positions: Set[Tuple[int, int]]

class MazeCycleAnalyzer:
    def __init__(self, filename: str):
        self.original_grid = self.load_maze(filename)
        self.height = len(self.original_grid)
        self.width = len(self.original_grid[0])
        self.directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # up, right, down, left
        
        # Visual settings
        self.cell_size = 6
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.cell_size, self.height * self.cell_size))
        pygame.display.set_caption("Cycle Analysis")
        
        self.COLORS = {
            'background': (255, 255, 255),
            'wall': (0, 0, 0),
            'cycle_wall': (255, 0, 0),
            'path': (200, 200, 255),
            'cycle_path': (255, 200, 200)
        }

    def load_maze(self, filename: str) -> List[List[str]]:
        with open(filename, 'r') as file:
            return [list(line.strip()) for line in file]

    def find_player(self, grid: List[List[str]]) -> Tuple[int, int]:
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] in '^>v<':
                    return (y, x)
        raise ValueError("No player found in maze")

    def get_initial_direction(self, grid: List[List[str]], pos: Tuple[int, int]) -> int:
        direction_chars = {'^': 0, '>': 1, 'v': 2, '<': 3}
        return direction_chars[grid[pos[0]][pos[1]]]

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        y, x = pos
        return 0 <= y < self.height and 0 <= x < self.width

    def simulate_path(self, grid: List[List[str]], max_steps: int = 30000) -> CycleResult:
        pos = self.find_player(grid)
        direction = self.get_initial_direction(grid, pos)
        
        # Track position history for cycle detection
        position_history = []
        visited_positions = set()
        position_to_step = {}  # Maps positions to when we first saw them
        
        step = 0
        while step < max_steps:
            position_history.append((pos, direction))
            visited_positions.add(pos)
            position_to_step[pos] = step
            
            # Calculate next position
            dy, dx = self.directions[direction]
            new_pos = (pos[0] + dy, pos[1] + dx)
            
            # Check for exit
            if not self.is_valid_position(new_pos):
                return CycleResult(False, step, 0, visited_positions)
            
            # Check for wall collision
            if grid[new_pos[0]][new_pos[1]] == '#':
                direction = (direction + 1) % 4
                continue
            
            # Move to new position
            pos = new_pos
            
            # Check for cycle
            # cyounter = sum(1 for value in position_to_step.values() if value == pos)
            cyounter = 1
            if cyounter >= 2:
                cycle_start_step = position_to_step[pos]
                cycle_length = step - cycle_start_step
                return CycleResult(True, cycle_start_step, cycle_length, visited_positions)
            
            step += 1
        
        return CycleResult(True, max_steps, 0, visited_positions)

    def find_cycle_inducing_walls(self) -> List[Tuple[int, int]]:
        cycle_walls = []
        original_path_result = self.simulate_path(self.original_grid)
        print(f"Original path: {len(original_path_result.visited_positions)} unique tiles visited")
        
        # Try placing a wall at each empty position
        for y in range(self.height):
            for x in range(self.width):
                if self.original_grid[y][x] == '.':
                    # Create a new grid with an additional wall
                    test_grid = copy.deepcopy(self.original_grid)
                    test_grid[y][x] = '#'
                    
                    # Simulate path with new wall
                    result = self.simulate_path(test_grid)
                    
                    # If this creates a cycle, record it
                    if result.forms_cycle:
                        cycle_walls.append((y, x))
                        print(f"Found cycle-inducing wall at ({y}, {x})")
                        print(f"  Steps before cycle: {result.steps_before_cycle}")
                        print(f"  Cycle length: {result.cycle_length}")
                        self.visualize_cycle(test_grid, result)
                        # pygame.time.wait(100)  # Brief pause to show each cycle
                        pygame.time.wait(1)  # Brief pause to show each cycle
        
        return cycle_walls

    def visualize_cycle(self, grid: List[List[str]], result: CycleResult):
        self.screen.fill(self.COLORS['background'])
        
        # Draw the maze
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                                 self.cell_size, self.cell_size)
                
                if grid[y][x] == '#':
                    color = self.COLORS['wall']
                    pygame.draw.rect(self.screen, color, rect)
                elif (y, x) in result.visited_positions:
                    color = self.COLORS['cycle_path'] if result.forms_cycle else self.COLORS['path']
                    pygame.draw.rect(self.screen, color, rect)
        
        pygame.display.flip()

def main():
    analyzer = MazeCycleAnalyzer("maze.txt")
    cycle_walls = analyzer.find_cycle_inducing_walls()
    print(f"\nFound {len(cycle_walls)} cycle-inducing wall positions")
    
    # Keep window open
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()