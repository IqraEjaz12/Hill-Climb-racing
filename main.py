import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
SKY_BLUE = (135, 206, 235)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)


class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.5
        self.max_speed = 8
        self.friction = 0.95
        self.gravity = 0.3
        self.angle = 0
        self.angular_velocity = 0
        self.on_ground = False
        self.fuel = 80  # Start with less fuel
        self.max_fuel = 80  # Reduced max fuel
        self.jump_power = 8
        self.can_jump = True

    def update(self, terrain_points):
        # Handle input
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.fuel > 0:
                self.velocity_x += self.acceleration
                self.fuel -= 0.2  # Increased fuel consumption
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.fuel > 0:
                self.velocity_x -= self.acceleration
                self.fuel -= 0.2  # Increased fuel consumption

        # Jump mechanic - Press UP or W to jump when on ground
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground and self.can_jump:
            if self.fuel >= 8:  # Jumping costs more fuel
                self.velocity_y = -self.jump_power
                self.fuel -= 8
                self.can_jump = False
                self.on_ground = False

        # Apply friction and speed limit
        self.velocity_x *= self.friction
        self.velocity_x = max(-self.max_speed, min(self.max_speed, self.velocity_x))

        # Apply gravity
        self.velocity_y += self.gravity

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Check collision with terrain
        self.check_terrain_collision(terrain_points)

        # Update angle based on velocity for realistic car tilt
        if self.velocity_x != 0:
            self.angular_velocity += self.velocity_x * 0.02
        self.angular_velocity *= 0.95
        self.angle += self.angular_velocity
        self.angle = max(-45, min(45, self.angle))

        # Keep fuel above 0
        self.fuel = max(0, self.fuel)

    def check_terrain_collision(self, terrain_points):
        # Check collision with multiple points of the car
        car_bottom = self.y + self.height // 2
        car_left = self.x - self.width // 2
        car_right = self.x + self.width // 2

        # Check collision points
        collision_points = [car_left, self.x, car_right]
        max_terrain_y = 0

        for point_x in collision_points:
            terrain_y = self.get_terrain_height_at_x(point_x, terrain_points)
            if terrain_y > max_terrain_y:
                max_terrain_y = terrain_y

        if car_bottom >= max_terrain_y:
            self.y = max_terrain_y - self.height // 2
            self.velocity_y = 0
            self.on_ground = True
            self.can_jump = True  # Reset jump ability when landing

            # Calculate slope angle for realistic car rotation
            if len(terrain_points) > 1:
                slope_angle = self.get_slope_angle_at_x(self.x, terrain_points)
                self.angle = slope_angle * 0.5  # Dampen the rotation
        else:
            self.on_ground = False

    def get_terrain_height_at_x(self, x, terrain_points):
        if not terrain_points or x < terrain_points[0][0] or x > terrain_points[-1][0]:
            return SCREEN_HEIGHT

        # Find the two points to interpolate between
        for i in range(len(terrain_points) - 1):
            if terrain_points[i][0] <= x <= terrain_points[i + 1][0]:
                x1, y1 = terrain_points[i]
                x2, y2 = terrain_points[i + 1]

                # Linear interpolation
                if x2 - x1 == 0:
                    return y1
                t = (x - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)

        return SCREEN_HEIGHT

    def get_slope_angle_at_x(self, x, terrain_points):
        if not terrain_points or x < terrain_points[0][0] or x > terrain_points[-1][0]:
            return 0

        # Find the slope at the current position
        for i in range(len(terrain_points) - 1):
            if terrain_points[i][0] <= x <= terrain_points[i + 1][0]:
                x1, y1 = terrain_points[i]
                x2, y2 = terrain_points[i + 1]

                if x2 - x1 == 0:
                    return 0
                slope = (y2 - y1) / (x2 - x1)
                return math.degrees(math.atan(slope))

        return 0

    def draw(self, screen, camera_x):
        car_screen_x = self.x - camera_x
        car_screen_y = self.y

        # Create car surface
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw car body (realistic shape)
        pygame.draw.rect(car_surface, RED, (5, 10, 50, 15))
        pygame.draw.rect(car_surface, GRAY, (15, 5, 30, 10))  # Windshield

        # Draw wheels
        wheel_radius = 8
        pygame.draw.circle(car_surface, BLACK, (15, 25), wheel_radius)
        pygame.draw.circle(car_surface, BLACK, (45, 25), wheel_radius)
        pygame.draw.circle(car_surface, GRAY, (15, 25), wheel_radius - 2)
        pygame.draw.circle(car_surface, GRAY, (45, 25), wheel_radius - 2)

        # Rotate car based on angle
        rotated_car = pygame.transform.rotate(car_surface, -self.angle)
        rotated_rect = rotated_car.get_rect(center=(car_screen_x, car_screen_y))

        screen.blit(rotated_car, rotated_rect)

        # Draw fuel gauge with low fuel warning
        fuel_width = 100
        fuel_height = 10
        fuel_x = 10
        fuel_y = 10

        pygame.draw.rect(screen, BLACK, (fuel_x - 2, fuel_y - 2, fuel_width + 4, fuel_height + 4))
        pygame.draw.rect(screen, WHITE, (fuel_x, fuel_y, fuel_width, fuel_height))
        fuel_fill = int((self.fuel / self.max_fuel) * fuel_width)
        fuel_color = GREEN if self.fuel > 24 else YELLOW if self.fuel > 12 else RED
        pygame.draw.rect(screen, fuel_color, (fuel_x, fuel_y, fuel_fill, fuel_height))

        # Low fuel warning
        if self.fuel <= 16:
            font = pygame.font.Font(None, 24)
            warning_text = font.render("LOW FUEL!", True, RED)
            screen.blit(warning_text, (fuel_x + fuel_width + 10, fuel_y - 5))


class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        if self.type == "rock":
            pygame.draw.ellipse(screen, GRAY, (screen_x, self.y, self.width, self.height))
        elif self.type == "log":
            pygame.draw.rect(screen, BROWN, (screen_x, self.y, self.width, self.height))
        elif self.type == "pit":
            pygame.draw.rect(screen, BLACK, (screen_x, self.y, self.width, self.height))


class Collectible:
    def __init__(self, x, y, collectible_type):
        self.x = x
        self.y = y
        self.type = collectible_type
        self.width = 20
        self.height = 20
        self.collected = False
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, screen, camera_x):
        if not self.collected:
            screen_x = self.x - camera_x
            if self.type == "fuel":
                pygame.draw.circle(screen, YELLOW, (screen_x + self.width // 2, self.y + self.height // 2), 10)
                pygame.draw.circle(screen, RED, (screen_x + self.width // 2, self.y + self.height // 2), 6)


class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.terrain_points = self.generate_terrain()
        self.obstacles = self.generate_obstacles()
        self.collectibles = self.generate_collectibles()
        self.goal_x = max(point[0] for point in self.terrain_points) - 100

    def generate_terrain(self):
        points = []
        terrain_length = 2000 + self.level_number * 500
        x = 0
        y = SCREEN_HEIGHT - 100

        points.append((x, y))

        while x < terrain_length:
            # Increase difficulty with level
            max_height_change = 20 + self.level_number * 5
            height_change = random.randint(-max_height_change, max_height_change)

            # Create hills and valleys
            if random.random() < 0.3:  # 30% chance for big elevation change
                height_change *= 2

            x += random.randint(30, 80)
            y += height_change

            # Keep terrain within bounds
            y = max(200, min(SCREEN_HEIGHT - 50, y))
            points.append((x, y))

        return points

    def generate_obstacles(self):
        obstacles = []
        num_obstacles = 4 + self.level_number * 2

        for _ in range(num_obstacles):
            x = random.randint(300, max(point[0] for point in self.terrain_points) - 300)
            terrain_y = self.get_terrain_height_at_x(x)

            obstacle_type = random.choice(["rock", "log", "pit", "pit"])  # More pits
            if obstacle_type == "rock":
                width, height = 45, 35
                y = terrain_y - height
            elif obstacle_type == "log":
                width, height = 70, 25
                y = terrain_y - height
            else:  # pit - Make pits that REQUIRE jumping
                width = random.randint(80, 120)  # Wider pits
                height = 60  # Deeper pits
                y = terrain_y

            obstacles.append(Obstacle(x, y, width, height, obstacle_type))

        return obstacles

    def generate_collectibles(self):
        collectibles = []
        num_collectibles = 3 + self.level_number  # Fewer fuel cans

        for _ in range(num_collectibles):
            x = random.randint(200, max(point[0] for point in self.terrain_points) - 200)
            terrain_y = self.get_terrain_height_at_x(x)
            y = terrain_y - 40

            collectibles.append(Collectible(x, y, "fuel"))

        return collectibles

    def get_terrain_height_at_x(self, x):
        if not self.terrain_points:
            return SCREEN_HEIGHT

        for i in range(len(self.terrain_points) - 1):
            if self.terrain_points[i][0] <= x <= self.terrain_points[i + 1][0]:
                x1, y1 = self.terrain_points[i]
                x2, y2 = self.terrain_points[i + 1]

                if x2 - x1 == 0:
                    return y1
                t = (x - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)

        return SCREEN_HEIGHT

    def draw_terrain(self, screen, camera_x):
        # Draw sky
        screen.fill(SKY_BLUE)

        # Draw terrain
        visible_points = []
        for point in self.terrain_points:
            screen_x = point[0] - camera_x
            if -100 <= screen_x <= SCREEN_WIDTH + 100:
                visible_points.append((screen_x, point[1]))

        if len(visible_points) > 1:
            # Fill terrain
            ground_points = visible_points + [(SCREEN_WIDTH + 100, SCREEN_HEIGHT), (-100, SCREEN_HEIGHT)]
            pygame.draw.polygon(screen, DARK_GREEN, ground_points)

            # Draw terrain outline
            if len(visible_points) > 1:
                pygame.draw.lines(screen, GREEN, False, visible_points, 3)

    def draw_goal(self, screen, camera_x):
        goal_screen_x = self.goal_x - camera_x
        if -50 <= goal_screen_x <= SCREEN_WIDTH + 50:
            terrain_y = self.get_terrain_height_at_x(self.goal_x)
            # Draw finish flag
            pygame.draw.rect(screen, BLACK, (goal_screen_x, terrain_y - 80, 5, 80))
            pygame.draw.polygon(screen, RED, [(goal_screen_x + 5, terrain_y - 80),
                                              (goal_screen_x + 45, terrain_y - 65),
                                              (goal_screen_x + 5, terrain_y - 50)])


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hill Climb Racing")
        self.clock = pygame.time.Clock()
        self.running = True

        self.current_level = 1
        self.level = Level(self.current_level)
        self.car = Car(100, 400)
        self.camera_x = 0
        self.score = 0
        self.game_state = "playing"  # "playing", "level_complete", "game_over"

        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_state == "game_over":
                    self.reset_level()
                elif event.key == pygame.K_n and self.game_state == "level_complete":
                    self.next_level()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        if self.game_state == "playing":
            self.car.update(self.level.terrain_points)

            # Update camera to follow car
            self.camera_x = self.car.x - SCREEN_WIDTH // 3

            # Check collision with obstacles
            car_rect = pygame.Rect(self.car.x - self.car.width // 2,
                                   self.car.y - self.car.height // 2,
                                   self.car.width, self.car.height)

            for obstacle in self.level.obstacles:
                if car_rect.colliderect(obstacle.rect):
                    if obstacle.type == "pit":
                        # STRICT pit collision - you MUST jump to pass
                        car_center_y = self.car.y
                        pit_top = obstacle.y

                        # If car's center is at or below pit level, game over
                        if car_center_y >= pit_top and self.car.velocity_y >= -2:
                            self.game_state = "game_over"
                    else:
                        # Other obstacles are impassable without jumping
                        car_center_y = self.car.y
                        obstacle_top = obstacle.y

                        # If car is not jumping over obstacle, bounce back
                        if car_center_y >= obstacle_top - 10:
                            self.car.velocity_x *= -0.3
                            self.car.velocity_y -= 1

            # Check collision with collectibles
            for collectible in self.level.collectibles:
                if not collectible.collected and car_rect.colliderect(collectible.rect):
                    collectible.collected = True
                    if collectible.type == "fuel":
                        self.car.fuel = min(self.car.max_fuel, self.car.fuel + 20)  # Less fuel per can
                        self.score += 10

            # Check if car reached the goal
            if self.car.x >= self.level.goal_x:
                self.game_state = "level_complete"
                self.score += 100

            # Check if car fell off the world or ran out of fuel
            if self.car.y > SCREEN_HEIGHT + 100:
                self.game_state = "game_over"
            elif self.car.fuel <= 0:
                # Show low fuel warning before game over
                if self.car.velocity_x == 0 and self.car.on_ground:
                    self.game_state = "game_over"

    def draw(self):
        # Draw terrain
        self.level.draw_terrain(self.screen, self.camera_x)

        # Draw obstacles
        for obstacle in self.level.obstacles:
            obstacle.draw(self.screen, self.camera_x)

        # Draw collectibles
        for collectible in self.level.collectibles:
            collectible.draw(self.screen, self.camera_x)

        # Draw goal
        self.level.draw_goal(self.screen, self.camera_x)

        # Draw car
        self.car.draw(self.screen, self.camera_x)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        # Draw level and score
        level_text = self.font.render(f"Level: {self.current_level}", True, BLACK)
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(level_text, (SCREEN_WIDTH - 200, 10))
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 50))

        # Draw controls and tips
        controls_text = self.font.render("Arrow Keys/WASD: Move | UP/W: Jump (Required for holes!)", True, BLACK)
        fuel_tip = pygame.font.Font(None, 24).render("Collect yellow fuel cans to refuel", True, BLUE)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 60))
        self.screen.blit(fuel_tip, (10, SCREEN_HEIGHT - 35))

        # Draw game state messages
        if self.game_state == "level_complete":
            complete_text = self.big_font.render("LEVEL COMPLETE!", True, GREEN)
            next_text = self.font.render("Press N for next level", True, BLACK)
            text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(complete_text, text_rect)
            self.screen.blit(next_text, next_rect)

        elif self.game_state == "game_over":
            game_over_text = self.big_font.render("GAME OVER!", True, RED)
            restart_text = self.font.render("Press R to restart level", True, BLACK)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

    def reset_level(self):
        self.car = Car(100, 400)
        self.camera_x = 0
        self.game_state = "playing"

    def next_level(self):
        self.current_level += 1
        self.level = Level(self.current_level)
        self.car = Car(100, 400)
        self.camera_x = 0
        self.game_state = "playing"

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()