import pygame
import time
from typing import List, Tuple, Set, Dict
from collections import defaultdict


def are_points_collinear(p1: Tuple[int, int], p2: Tuple[int, int], p3: Tuple[int, int]) -> bool:
    """
    Check if three points lie on the same line using cross product.
    Returns True if points are collinear.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return (y2 - y1) * (x3 - x1) == (y3 - y1) * (x2 - x1)

def find_line_points(p1: Tuple[int, int], p2: Tuple[int, int], grid_size: Tuple[int, int]) -> Set[Tuple[int, int]]:
    """
    Find all grid points that lie on the line between two points, including endpoints.
    Only returns points within grid boundaries.
    """
    points = set()
    rows, cols = grid_size
    
    # Extract coordinates
    x1, y1 = p1
    x2, y2 = p2
    
    # Handle vertical lines
    if x1 == x2:
        start_y = min(y1, y2)
        end_y = max(y1, y2)
        for y in range(start_y, end_y + 1):
            if 0 <= y < rows and 0 <= x1 < cols:
                points.add((x1, y))
        return points
    
    # Calculate slope and intercept
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    
    # Find points along the line
    start_x = min(x1, x2)
    end_x = max(x1, x2)
    
    for x in range(start_x, end_x + 1):
        y = int(round(slope * x + intercept))
        if 0 <= x < cols and 0 <= y < rows:
            points.add((x, y))
    
    return points

def calculate_antinodes(grid: List[List[str]]) -> Set[Tuple[int, int]]:
    """Calculate all antinode positions using the line-of-sight model."""
    antinodes = set()
    rows, cols = len(grid), len(grid[0])
    
    # Group antenna positions by frequency
    frequency_positions = defaultdict(list)
    for i in range(rows):
        for j in range(cols):
            char = grid[i][j]
            if char != '.' and char != '#':
                frequency_positions[char].append((j, i))  # Note: using (x,y) coordinates
    
    # For each frequency group with multiple antennas
    for char, positions in frequency_positions.items():
        if len(positions) < 2:
            continue
            
        # For each triplet of positions
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                # Add antenna positions themselves as antinodes
                antinodes.add(positions[i])
                antinodes.add(positions[j])
                
                # Find all points on the line between these antennas
                line_points = find_line_points(positions[i], positions[j], (rows, cols))
                
                # For each point on this line
                for point in line_points:
                    # Check if this point is collinear with any other antenna of same frequency
                    for k in range(len(positions)):
                        if k != i and k != j and are_points_collinear(positions[i], positions[j], positions[k]):
                            antinodes.add(point)
    
    return antinodes

def load_grid_from_file(filename: str) -> List[List[str]]:
    """Load the grid from a text file."""
    grid = []
    with open(filename, "r") as file:
        for line in file:
            row = list(line.strip())
            grid.append(row)
    return grid

def find_matching_positions(grid: List[List[str]]) -> Dict[str, List[Tuple[int, int]]]:
    """Find all matching characters in the grid and their positions."""
    char_positions = defaultdict(list)
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            char = grid[i][j]
            if char not in ('.', '#'):  # Skip empty spaces and antinode markers
                char_positions[char].append((i, j))
    
    return {char: positions for char, positions in char_positions.items() 
            if len(positions) > 1}

def calculate_antinode_positions(pos1: Tuple[int, int], pos2: Tuple[int, int], grid_size: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Calculate antinode positions for a pair of nodes.
    Returns positions that are triple the distance in each direction.
    Only returns positions that fall within the grid boundaries.
    """
    rows, cols = grid_size
    y1, x1 = pos1
    y2, x2 = pos2
    
    # Calculate the vector between the points
    dy = y2 - y1
    dx = x2 - x1
    
    # Calculate potential antinode positions (triple the distance in each direction)
    antinodes = []
    
    # Calculate the first antinode (before pos1)
    anti_y1 = y1 - dy
    anti_x1 = x1 - dx
    
    # Calculate the second antinode (after pos2)
    anti_y2 = y2 + dy
    anti_x2 = x2 + dx
    
    # Check if antinodes are within grid boundaries
    if 0 <= anti_y1 < rows and 0 <= anti_x1 < cols:
        antinodes.append((anti_y1, anti_x1))
    
    if 0 <= anti_y2 < rows and 0 <= anti_x2 < cols:
        antinodes.append((anti_y2, anti_x2))
    
    return antinodes

class GridVisualizer:
    def __init__(self, grid: List[List[str]], window_size: int = 1000):
        pygame.init()
        self.grid = grid
        self.grid_size = len(grid)
        self.window_size = window_size
        self.base_cell_size = window_size // self.grid_size

        # Initialize connections dictionary
        self.connections = defaultdict(list)
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                char = grid[i][j]
                if char not in ('.', '#'):  # Skip empty spaces and antinode markers
                    self.connections[char].append((i, j))
        
        # Filter out single characters
        self.connections = {char: positions for char, positions in self.connections.items() 
                          if len(positions) > 1}

        # Zoom and pan variables
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 5.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False
        self.last_mouse_pos = None

        # Stats panel setup
        self.stats_panel_width = 200
        self.screen = pygame.display.set_mode((window_size + self.stats_panel_width, window_size))
        pygame.display.set_caption("Antenna and Antinode Visualizer")
        self.grid_surface = pygame.Surface((window_size, window_size))

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.LINE_COLOR = (100, 149, 237)  # Cornflower blue
        self.ANTINODE_COLOR = (255, 165, 0)  # Orange
        self.ANTENNA_COLOR = (50, 205, 50)   # Lime green

        # Font setup
        self.base_font_size = self.base_cell_size
        self.stats_font = pygame.font.Font(None, 24)

        # Calculate antinodes
        self.antinodes = calculate_antinodes(grid)
        
        # Mark antinodes in grid
        self.mark_antinodes()
        
    def mark_antinodes(self):
        """Mark antinode positions in the grid with '#'."""
        for x, y in self.antinodes:
            if self.grid[y][x] == '.':  # Only mark empty spaces
                self.grid[y][x] = '#'

    @property
    def cell_size(self):
        """Get current cell size based on zoom level."""
        return self.base_cell_size * self.zoom_level

    def calculate_all_antinodes(self) -> Set[Tuple[int, int]]:
        """Calculate all antinode positions for all connected nodes."""
        antinodes = set()
        grid_size = (len(self.grid), len(self.grid[0]))
        
        for positions in self.connections.values():
            # Calculate antinodes for each pair of matching characters
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    new_antinodes = calculate_antinode_positions(positions[i], positions[j], grid_size)
                    antinodes.update(new_antinodes)
                    
                    # Mark antinodes in the grid
                    for y, x in new_antinodes:
                        if self.grid[y][x] == '.':  # Only mark empty spaces
                            self.grid[y][x] = '#'
        
        return antinodes

    def get_font(self):
        """Get font sized according to zoom level."""
        size = max(int(self.base_font_size * self.zoom_level), 1)
        return pygame.font.Font(None, size)

    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to screen coordinates."""
        screen_x = grid_x * self.cell_size + self.pan_x + self.cell_size / 2
        screen_y = grid_y * self.cell_size + self.pan_y + self.cell_size / 2
        return screen_x, screen_y

    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates."""
        grid_x = (screen_x - self.pan_x) / self.cell_size
        grid_y = (screen_y - self.pan_y) / self.cell_size
        return int(grid_x), int(grid_y)

    def draw_connections(self):
        """Draw lines between matching characters and highlight antinodes."""
        # Draw node connections
        for positions in self.connections.values():
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    pos1 = positions[i]
                    pos2 = positions[j]
                    
                    screen_pos1 = self.grid_to_screen(pos1[1], pos1[0])
                    screen_pos2 = self.grid_to_screen(pos2[1], pos2[0])
                    
                    pygame.draw.line(
                        self.grid_surface,
                        self.LINE_COLOR,
                        screen_pos1,
                        screen_pos2,
                        max(1, int(2 * self.zoom_level))
                    )

        # Draw antinode connections
        for antinode in self.antinodes:
            screen_pos = self.grid_to_screen(antinode[1], antinode[0])
            
            # Draw a small circle for each antinode
            pygame.draw.circle(
                self.grid_surface,
                self.ANTINODE_COLOR,
                (int(screen_pos[0]), int(screen_pos[1])),
                max(3, int(4 * self.zoom_level))
            )

    def draw_grid(self):
        # Fill background
        self.grid_surface.fill(self.WHITE)
        
        # Draw connections first (so they appear behind the letters)
        self.draw_connections()

        # Calculate visible grid bounds
        start_x, start_y = self.screen_to_grid(0, 0)
        end_x, end_y = self.screen_to_grid(self.window_size, self.window_size)

        # Clamp to grid bounds
        start_x = max(0, min(start_x, self.grid_size))
        start_y = max(0, min(start_y, self.grid_size))
        end_x = max(0, min(end_x + 2, self.grid_size))
        end_y = max(0, min(end_y + 2, self.grid_size))

        # Draw grid lines
        for i in range(start_x, end_x + 1):
            pos = i * self.cell_size + self.pan_x
            pygame.draw.line(self.grid_surface, self.GRAY, (pos, 0), (pos, self.window_size))

        for i in range(start_y, end_y + 1):
            pos = i * self.cell_size + self.pan_y
            pygame.draw.line(self.grid_surface, self.GRAY, (0, pos), (self.window_size, pos))

        # Draw letters
        font = self.get_font()
        for i in range(start_y, end_y):
            for j in range(start_x, end_x):
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                    x = j * self.cell_size + self.pan_x
                    y = i * self.cell_size + self.pan_y
                    
                    letter = self.grid[i][j]
                    if letter != '.':
                        text = font.render(letter, True, self.BLACK)
                        text_rect = text.get_rect(
                            center=(x + self.cell_size // 2, y + self.cell_size // 2)
                        )
                        self.grid_surface.blit(text, text_rect)

        # Draw the grid surface and stats panel
        self.screen.fill(self.WHITE)
        self.screen.blit(self.grid_surface, (0, 0))
        self.draw_stats_panel()

        # Draw zoom indicator
        zoom_text = self.stats_font.render(f"Zoom: {self.zoom_level:.1f}x", True, self.BLACK)
        self.screen.blit(zoom_text, (10, 10))

        pygame.display.flip()

    def draw_stats_panel(self):
        panel_rect = pygame.Rect(self.window_size, 0, self.stats_panel_width, self.window_size)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect)
        pygame.draw.line(
            self.screen,
            self.BLACK,
            (self.window_size, 0),
            (self.window_size, self.window_size),
        )

        # Draw stats
        y_offset = 10
        
        # Connected nodes section
        title = self.stats_font.render("Connected Nodes", True, self.BLACK)
        self.screen.blit(title, (self.window_size + 10, y_offset))
        y_offset += 30

        count_text = self.stats_font.render(
            f"Node Pairs: {sum(len(pos) * (len(pos)-1) // 2 for pos in self.connections.values())}", 
            True, 
            self.BLACK
        )
        self.screen.blit(count_text, (self.window_size + 10, y_offset))
        y_offset += 30

        # Antinodes section
        antinode_title = self.stats_font.render("Antinodes", True, self.BLACK)
        self.screen.blit(antinode_title, (self.window_size + 10, y_offset))
        y_offset += 30

        antinode_count = self.stats_font.render(
            f"Count: {len(self.antinodes)}", 
            True, 
            self.BLACK
        )
        self.screen.blit(antinode_count, (self.window_size + 10, y_offset))

    def handle_mouse_wheel(self, y: int):
        """Handle mouse wheel scrolling for zoom."""
        old_zoom = self.zoom_level
        if y > 0:
            self.zoom_level = min(self.zoom_level * 1.1, self.max_zoom)
        else:
            self.zoom_level = max(self.zoom_level / 1.1, self.min_zoom)

        if old_zoom != self.zoom_level:
            center_x = self.window_size / 2
            center_y = self.window_size / 2
            self.pan_x = center_x - (center_x - self.pan_x) * (self.zoom_level / old_zoom)
            self.pan_y = center_y - (center_y - self.pan_y) * (self.zoom_level / old_zoom)

    def handle_mouse_drag(self, pos: Tuple[int, int]):
        """Handle mouse dragging for pan."""
        if self.last_mouse_pos:
            dx = pos[0] - self.last_mouse_pos[0]
            dy = pos[1] - self.last_mouse_pos[1]
            self.pan_x += dx
            self.pan_y += dy
        self.last_mouse_pos = pos

    def run(self):
        """Main loop to keep the window open."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    self.handle_mouse_wheel(event.y)
                    self.draw_grid()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.dragging = False
                        self.last_mouse_pos = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.handle_mouse_drag(event.pos)
                        self.draw_grid()

            time.sleep(0.01)
        pygame.quit()

if __name__ == "__main__":
    try:
        grid = load_grid_from_file("input.txt")
        visualizer = GridVisualizer(grid)
        visualizer.draw_grid()
        visualizer.run()
    except FileNotFoundError:
        print("Error: Could not find input.txt")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")