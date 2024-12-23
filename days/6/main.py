import pygame
import sys
import random
from typing import List, Tuple, Optional, Set
from pathlib import Path


class MazePathfinder:
    def __init__(self, filename: str):
        pygame.init()
        pygame.mixer.init()

        self.sounds = self.load_sounds()

        self.grid = self.load_maze(filename)
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.cell_size = 6

        # Calculate window height to accommodate controls and counters
        window_height = (
            self.height * self.cell_size + 80
        )  # Extra space for controls and stats
        self.screen = pygame.display.set_mode(
            (self.width * self.cell_size, window_height)
        )
        pygame.display.set_caption("Maze Pathfinder")

        self.COLORS = {
            "background": (255, 255, 255),
            "wall": (0, 0, 0),
            "player": (255, 0, 0),
            "path": (200, 200, 255),
            "button": (100, 100, 100),
            "slider": (80, 80, 80),
            "slider_handle": (120, 120, 120),
            "counter_text": (50, 50, 50),
        }

        self.player_pos = self.find_player()
        self.player_direction = self.get_initial_direction()
        # Using a set to track unique positions
        self.visited_tiles: Set[Tuple[int, int]] = {self.player_pos}
        self.total_steps = 0  # Keep track of total steps for comparison
        self.running = False

        # Speed control
        self.min_speed = 1
        self.max_speed = 500
        self.speed = 10
        self.slider_rect = pygame.Rect(70, window_height - 40, 200, 10)
        self.slider_handle_rect = pygame.Rect(0, 0, 20, 20)
        self.update_slider_handle()
        self.dragging_slider = False

        # Font for counters
        self.font = pygame.font.Font(None, 24)

        self.directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def update_slider_handle(self):
        # Calculate handle position based on speed
        speed_ratio = (self.speed - self.min_speed) / (self.max_speed - self.min_speed)
        handle_x = self.slider_rect.left + (self.slider_rect.width * speed_ratio) - 10
        self.slider_handle_rect.center = (handle_x, self.slider_rect.centery)

    def play_sound_with_variance(self, sound_key: str):
        """Play a sound with random pitch variance"""
        sound = self.sounds[sound_key]
        # Random pitch between 0.9 and 1.1
        pitch = random.uniform(0.9, 1.1)
        # Unfortunately, pygame.mixer.Sound doesn't support pitch shifting directly
        # So we'll use a channel to control playback speed which affects pitch
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)
            # Note: This is a simplified approach - for more precise pitch control,
            # you might want to use a library like sounddevice or pygame.sndarray

    def load_sounds(self) -> dict:
        """Load and return dictionary of sound effects"""
        sounds = {}
        try:
            sounds["step"] = pygame.mixer.Sound("step.wav")
            sounds["step"].set_volume(0.2)

            sounds["collision"] = pygame.mixer.Sound("collision.wav")
            sounds["collision"].set_volume(0.5)

            sounds["victory"] = pygame.mixer.Sound("victory.wav")
            sounds["victory"].set_volume(0.7)
        except FileNotFoundError as e:
            print(f"Warning: Could not load sound file: {e}")
            empty_sound = pygame.mixer.Sound(buffer=bytes([]))
            sounds = {
                "step": empty_sound,
                "collision": empty_sound,
                "victory": empty_sound,
            }
        return sounds

    def load_maze(self, filename: str) -> List[List[str]]:
        with open(filename, "r") as file:
            return [list(line.strip()) for line in file]

    def find_player(self) -> Tuple[int, int]:
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] in "^>v<":
                    return (y, x)
        raise ValueError("No player found in maze")

    def get_initial_direction(self) -> int:
        direction_chars = {"^": 0, ">": 1, "v": 2, "<": 3}
        return direction_chars[self.grid[self.player_pos[0]][self.player_pos[1]]]

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        y, x = pos
        return 0 <= y < self.height and 0 <= x < self.width

    def move_player(self) -> bool:
        if not self.running:
            return True

        dy, dx = self.directions[self.player_direction]
        new_pos = (self.player_pos[0] + dy, self.player_pos[1] + dx)

        if not self.is_valid_position(new_pos):
            final_message = (
                f"Maze completed!\n"
                f"Unique tiles visited: {len(self.visited_tiles)}\n"
                f"Total steps taken: {self.total_steps}"
            )
            print(final_message)
            self.play_sound_with_variance("victory")
            self.running = False
            return False

        if self.grid[new_pos[0]][new_pos[1]] == "#":
            self.play_sound_with_variance("collision")
            self.player_direction = (self.player_direction + 1) % 4
            return True

        self.play_sound_with_variance("step")
        self.player_pos = new_pos
        self.visited_tiles.add(new_pos)  # Add to set of unique positions
        self.total_steps += 1  # Increment total step counter
        return True

    def draw(self):
        self.screen.fill(self.COLORS["background"])

        # Draw maze
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                if self.grid[y][x] == "#":
                    pygame.draw.rect(self.screen, self.COLORS["wall"], rect)
                elif (y, x) in self.visited_tiles:
                    pygame.draw.rect(self.screen, self.COLORS["path"], rect)

        # Draw player
        player_rect = pygame.Rect(
            self.player_pos[1] * self.cell_size,
            self.player_pos[0] * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(self.screen, self.COLORS["player"], player_rect)

        # Draw GO button
        if not self.running:
            button_rect = pygame.Rect(10, 10, 50, 30)
            pygame.draw.rect(self.screen, self.COLORS["button"], button_rect)

        # Draw speed slider and label
        pygame.draw.rect(self.screen, self.COLORS["slider"], self.slider_rect)
        pygame.draw.rect(
            self.screen, self.COLORS["slider_handle"], self.slider_handle_rect
        )

        speed_text = self.font.render(
            f"Speed: {self.speed}", True, self.COLORS["counter_text"]
        )
        self.screen.blit(
            speed_text, (self.slider_rect.left - 60, self.slider_rect.top - 5)
        )

        # Draw counters
        unique_tiles_text = self.font.render(
            f"Unique Tiles: {len(self.visited_tiles)}",
            True,
            self.COLORS["counter_text"],
        )
        total_steps_text = self.font.render(
            f"Total Steps: {self.total_steps}", True, self.COLORS["counter_text"]
        )

        # Position counters in bottom-right corner
        self.screen.blit(unique_tiles_text, (self.width * self.cell_size - 150, 10))
        self.screen.blit(total_steps_text, (self.width * self.cell_size - 150, 35))

        pygame.display.flip()

    def handle_slider_interaction(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.slider_handle_rect.collidepoint(event.pos):
                self.dragging_slider = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = False

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            # Update speed based on slider position
            x = max(self.slider_rect.left, min(event.pos[0], self.slider_rect.right))
            ratio = (x - self.slider_rect.left) / self.slider_rect.width
            self.speed = int(self.min_speed + ratio * (self.max_speed - self.min_speed))
            self.update_slider_handle()

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.handle_slider_interaction(event)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.running:
                    if pygame.Rect(10, 10, 50, 30).collidepoint(event.pos):
                        self.running = True

            if self.running:
                if not self.move_player():
                    self.running = False

            self.draw()
            clock.tick(self.speed)


if __name__ == "__main__":
    game = MazePathfinder("maze.txt")
    game.run()
