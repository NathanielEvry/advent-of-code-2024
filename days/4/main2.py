# Notes: Does not currently visualize the 3x3 grids that have been matched. Just spits out the answer in console.

import pygame
import time
from typing import List, Tuple, Set


def load_grid_from_file(filename: str) -> List[List[str]]:
    """Load the word search grid from a text file."""
    grid = []
    with open(filename, "r") as file:
        for line in file:
            # Remove any whitespace and newlines, convert to uppercase
            row = list(line.strip().upper())
            grid.append(row)

    # Validate grid dimensions
    height = len(grid)
    if height != 140:
        raise ValueError(f"Expected 140 rows, got {height}")

    for i, row in enumerate(grid):
        if len(row) != 140:
            raise ValueError(f"Row {i} has {len(row)} characters, expected 140")

    return grid


class WordSearchVisualizer:
    def __init__(self, grid: List[List[str]], window_size: int = 800):
        pygame.init()
        self.grid = grid
        self.grid_size = len(grid)
        self.window_size = window_size
        self.base_cell_size = window_size // self.grid_size

        # Zoom and pan variables
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 5.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False
        self.last_mouse_pos = None

        # Adjust window size to account for stats panel
        self.stats_panel_width = 200
        self.screen = pygame.display.set_mode(
            (window_size + self.stats_panel_width, window_size)
        )
        pygame.display.set_caption("Word Search Visualizer")

        # Create a separate surface for the grid that we can scroll
        self.grid_surface = pygame.Surface((window_size, window_size))

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (200, 200, 200)

        # Font setup
        self.base_font_size = self.base_cell_size
        self.stats_font = pygame.font.Font(None, 24)

        # Track found words and their positions
        self.found_words: Set[str] = set()
        self.highlighted_positions: Set[Tuple[int, int]] = set()

    @property
    def cell_size(self):
        """Get current cell size based on zoom level."""
        return self.base_cell_size * self.zoom_level

    def get_font(self):
        """Get font sized according to zoom level."""
        size = max(int(self.base_font_size * self.zoom_level), 1)
        return pygame.font.Font(None, size)

    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates."""
        grid_x = (screen_x - self.pan_x) / self.cell_size
        grid_y = (screen_y - self.pan_y) / self.cell_size
        return int(grid_x), int(grid_y)

    def draw_grid(self):
        # Fill background
        self.grid_surface.fill(self.WHITE)

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
            pygame.draw.line(
                self.grid_surface, self.GRAY, (pos, 0), (pos, self.window_size)
            )

        for i in range(start_y, end_y + 1):
            pos = i * self.cell_size + self.pan_y
            pygame.draw.line(
                self.grid_surface, self.GRAY, (0, pos), (self.window_size, pos)
            )

        # Draw letters and highlights
        font = self.get_font()
        for i in range(start_y, end_y):
            for j in range(start_x, end_x):
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                    # Calculate position with pan offset
                    x = j * self.cell_size + self.pan_x
                    y = i * self.cell_size + self.pan_y

                    # Draw letter
                    letter = self.grid[i][j]
                    text = font.render(letter, True, self.BLACK)
                    text_rect = text.get_rect(
                        center=(x + self.cell_size // 2, y + self.cell_size // 2)
                    )
                    self.grid_surface.blit(text, text_rect)

                    # Draw oval highlight if position is found
                    if (i, j) in self.highlighted_positions:
                        pygame.draw.ellipse(
                            self.grid_surface,
                            self.RED,
                            (x + 2, y + 2, self.cell_size - 4, self.cell_size - 4),
                            2,
                        )

        # Draw the grid surface and stats panel
        self.screen.fill(self.WHITE)
        self.screen.blit(self.grid_surface, (0, 0))
        self.draw_stats_panel()

        # Draw zoom level indicator
        zoom_text = self.stats_font.render(
            f"Zoom: {self.zoom_level:.1f}x", True, self.BLACK
        )
        self.screen.blit(zoom_text, (10, 10))

        pygame.display.flip()

    def draw_stats_panel(self):
        # Draw panel background
        panel_rect = pygame.Rect(
            self.window_size, 0, self.stats_panel_width, self.window_size
        )
        pygame.draw.rect(self.screen, self.WHITE, panel_rect)
        pygame.draw.line(
            self.screen,
            self.BLACK,
            (self.window_size, 0),
            (self.window_size, self.window_size),
        )

        # Draw stats
        title = self.stats_font.render("Found Words", True, self.BLACK)
        self.screen.blit(title, (self.window_size + 10, 10))

        # Display word count
        count_text = self.stats_font.render(
            f"Count: {len(self.found_words)}", True, self.BLACK
        )
        self.screen.blit(count_text, (self.window_size + 10, 40))

        # List found words
        y_offset = 70
        for word in sorted(self.found_words):
            if y_offset + 20 < self.window_size:
                word_text = self.stats_font.render(word, True, self.BLACK)
                self.screen.blit(word_text, (self.window_size + 10, y_offset))
                y_offset += 25

    def handle_mouse_wheel(self, y: int):
        """Handle mouse wheel scrolling for zoom."""
        old_zoom = self.zoom_level

        # Adjust zoom level
        if y > 0:
            self.zoom_level = min(self.zoom_level * 1.1, self.max_zoom)
        else:
            self.zoom_level = max(self.zoom_level / 1.1, self.min_zoom)

        # Adjust pan to keep the center point consistent
        if old_zoom != self.zoom_level:
            center_x = self.window_size / 2
            center_y = self.window_size / 2
            self.pan_x = center_x - (center_x - self.pan_x) * (
                self.zoom_level / old_zoom
            )
            self.pan_y = center_y - (center_y - self.pan_y) * (
                self.zoom_level / old_zoom
            )

    def handle_mouse_drag(self, pos: Tuple[int, int]):
        """Handle mouse dragging for pan."""
        if self.last_mouse_pos:
            dx = pos[0] - self.last_mouse_pos[0]
            dy = pos[1] - self.last_mouse_pos[1]
            self.pan_x += dx
            self.pan_y += dy
        self.last_mouse_pos = pos

    def add_found_word(self, word: str, positions: List[Tuple[int, int]]):
        """Add a new found word and its positions to be highlighted."""
        self.found_words.add(word)
        self.highlighted_positions.update(positions)
        self.draw_grid()

    def add_found_pattern(self, positions: List[Tuple[int, int]]):
        """Highlight 3x3 patterns in the grid."""
        for x, y in positions:
            for i in range(3):
                for j in range(3):
                    self.highlighted_positions.add((x + i, y + j))
        self.draw_grid()

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


def search_words(grid: List[List[str]], words: List[str]) -> dict:
    """
    Search for all instances of words in the grid in all 8 directions.
    Returns a dictionary mapping found words to lists of their positions.
    """

    def is_valid_pos(x, y):
        return 0 <= x < len(grid) and 0 <= y < len(grid[0])

    # Define all 8 directions: right, down-right, down, down-left, left, up-left, up, up-right
    # directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    # Define diagonal-only, for x'd "MAS"
    directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

    found_words = {}
    word_set = set(words)

    # For each starting position in the grid
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            # Try each direction
            for dx, dy in directions:
                # Maximum word length to check from this position
                max_len = max(len(word) for word in words)

                # Build potential words in this direction
                x, y = i, j
                curr_word = ""
                positions = []

                for _ in range(max_len):
                    if not is_valid_pos(x, y):
                        break

                    curr_word += grid[x][y]
                    positions.append((x, y))

                    # Check if we've found a word
                    if curr_word in word_set:
                        # If word already found, append new positions to existing list
                        if curr_word in found_words:
                            found_words[curr_word].extend(positions)
                        else:
                            found_words[curr_word] = positions.copy()

                    x += dx
                    y += dy

    return found_words


def search_patterns(
    grid: List[List[str]], patterns: List[List[str]]
) -> List[Tuple[int, int]]:
    """
    Search for 3x3 patterns in the grid.

    Args:
        grid: The word search grid as a 2D list of characters.
        patterns: A list of 3x3 patterns to search for, where '*' is a wildcard.

    Returns:
        A list of top-left coordinates of the 3x3 grids matching any pattern.
    """

    def matches_pattern(sub_grid: List[List[str]], pattern: List[List[str]]) -> bool:
        """Check if a 3x3 sub-grid matches the given pattern."""
        for i in range(3):
            for j in range(3):
                if pattern[i][j] != "*" and sub_grid[i][j] != pattern[i][j]:
                    return False
        return True

    matches = []
    rows, cols = len(grid), len(grid[0])

    # Iterate over all possible 3x3 sub-grids
    for i in range(rows - 2):
        for j in range(cols - 2):
            # Extract the 3x3 sub-grid
            sub_grid = [row[j : j + 3] for row in grid[i : i + 3]]

            # Check against all patterns
            for pattern in patterns:
                if matches_pattern(sub_grid, pattern):
                    matches.append((i, j))
                    break  # Stop checking other patterns for this sub-grid

    return matches


# Example usage:
if __name__ == "__main__":
    try:
        # Load the grid from file
        grid = load_grid_from_file("grid.txt")

        # Initialize and run visualizer
        visualizer = WordSearchVisualizer(grid)
        visualizer.draw_grid()

        # words_to_find = ["MAS"]  # Add your words here

        # Find all instances of the words
        # found_words = search_words(grid, words_to_find)

        # Define the patterns
        patterns = [
            [
                ["M", "*", "M"],
                ["*", "A", "*"],
                ["S", "*", "S"],
            ],
            [
                ["M", "*", "S"],
                ["*", "A", "*"],
                ["M", "*", "S"],
            ],
            [
                ["S", "*", "S"],
                ["*", "A", "*"],
                ["M", "*", "M"],
            ],
            [
                ["S", "*", "M"],
                ["*", "A", "*"],
                ["S", "*", "M"],
            ],
        ]

        # Search for patterns
        matches = search_patterns(grid, patterns)
        
        # TODO Iterate through all matches and highlight them
        # for match in matches:
        #     row, col = match  # Extract the row and column of the match
        #     add_found_pattern(grid, row, col)  # Highlight the 3x3 grid starting at (row, col)

        print("Matches found at top-left coordinates:", matches)
        print("Total Matches found",len(matches))

        # Display all instances
        # for word, positions in found_words.items():
            # print(f"Found word: {word} at {len(positions)//len(word)} locations")
            # visualizer.add_found_word(word, positions)

        visualizer.run()

    except FileNotFoundError:
        print("Error: Could not find grid.txt")
    except ValueError as e:
        print(f"Error: Invalid grid format - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
