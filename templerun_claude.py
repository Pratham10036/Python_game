import pygame
import random
import math
import json
import os

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
SLIDE_DURATION = 30
LANE_WIDTH = SCREEN_WIDTH // 3
LANES = [LANE_WIDTH // 2, SCREEN_WIDTH // 2, SCREEN_WIDTH - LANE_WIDTH // 2]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3

class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, life=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity
        self.life -= 1
        
        # Fade out
        alpha = int(255 * (self.life / self.max_life))
        self.color = (*self.color[:3], alpha)
        
        return self.life > 0
    
    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Player:
    def __init__(self):
        self.lane = 1  # Middle lane
        self.x = LANES[self.lane]
        self.y = SCREEN_HEIGHT - 150
        self.width = 60
        self.height = 80
        self.ground_y = self.y
        self.velocity_y = 0
        self.is_jumping = False
        self.is_sliding = False
        self.slide_timer = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.target_x = self.x
        self.moving = False
        
    def update(self):
        # Handle lane switching
        if self.moving:
            if abs(self.x - self.target_x) > 5:
                self.x += (self.target_x - self.x) * 0.2
            else:
                self.x = self.target_x
                self.moving = False
        
        # Handle jumping
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
            
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.velocity_y = 0
                self.is_jumping = False
        
        # Handle sliding
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.height = 80
        
        # Handle invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.velocity_y = JUMP_STRENGTH
    
    def slide(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = SLIDE_DURATION
            self.height = 40
    
    def move_left(self):
        if self.lane > 0 and not self.moving:
            self.lane -= 1
            self.target_x = LANES[self.lane]
            self.moving = True
    
    def move_right(self):
        if self.lane < 2 and not self.moving:
            self.lane += 1
            self.target_x = LANES[self.lane]
            self.moving = True
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height, self.width, self.height)
    
    def draw(self, screen):
        # Draw player as animated rectangle (placeholder for sprite)
        color = BLUE
        if self.invincible:
            # Flash effect during invincibility
            color = YELLOW if (self.invincible_timer // 5) % 2 == 0 else BLUE
        
        rect = self.get_rect()
        pygame.draw.rect(screen, color, rect)
        
        # Draw eyes
        eye_size = 5
        eye_y = rect.y + 15
        pygame.draw.circle(screen, BLACK, (int(rect.x + 15), eye_y), eye_size)
        pygame.draw.circle(screen, BLACK, (int(rect.x + 45), eye_y), eye_size)
        
        # Draw running animation lines
        if self.animation_frame < 2:
            pygame.draw.line(screen, BLACK, (rect.x + 10, rect.y + 50), (rect.x + 20, rect.y + 70), 3)
            pygame.draw.line(screen, BLACK, (rect.x + 40, rect.y + 50), (rect.x + 50, rect.y + 70), 3)

class Obstacle:
    def __init__(self, x, y, obstacle_type):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.width = 60
        self.height = 80
        self.speed = 8
        
        if obstacle_type == "barrier":
            self.height = 100
            self.color = BROWN
        elif obstacle_type == "low":
            self.height = 40
            self.y = SCREEN_HEIGHT - 100
            self.color = GRAY
        elif obstacle_type == "pit":
            self.width = 120
            self.height = 50
            self.y = SCREEN_HEIGHT - 50
            self.color = BLACK
        elif obstacle_type == "moving":
            self.direction = random.choice([-1, 1])
            self.color = RED
    
    def update(self, game_speed):
        self.x -= game_speed
        
        if self.type == "moving":
            self.x += self.direction * 2
            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
                self.direction *= -1
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)
    
    def draw(self, screen):
        rect = self.get_rect()
        pygame.draw.rect(screen, self.color, rect)
        
        if self.type == "pit":
            pygame.draw.rect(screen, BLACK, rect)
        elif self.type == "barrier":
            # Draw spikes on top
            for i in range(0, self.width, 10):
                pygame.draw.polygon(screen, BLACK, [
                    (rect.x + i, rect.y),
                    (rect.x + i + 5, rect.y - 10),
                    (rect.x + i + 10, rect.y)
                ])

class Collectible:
    def __init__(self, x, y, collectible_type):
        self.x = x
        self.y = y
        self.type = collectible_type
        self.width = 20
        self.height = 20
        self.speed = 8
        self.animation_frame = 0
        self.collected = False
        
        if collectible_type == "coin":
            self.color = GOLD
            self.value = 10
        elif collectible_type == "gem":
            self.color = PURPLE
            self.value = 50
            self.width = 25
            self.height = 25
        elif collectible_type == "magnet":
            self.color = RED
            self.value = 0
        elif collectible_type == "speed":
            self.color = GREEN
            self.value = 0
        elif collectible_type == "invincibility":
            self.color = YELLOW
            self.value = 0
    
    def update(self, game_speed):
        self.x -= game_speed
        self.animation_frame = (self.animation_frame + 1) % 60
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)
    
    def draw(self, screen):
        if self.collected:
            return
            
        rect = self.get_rect()
        
        # Floating animation
        offset = math.sin(self.animation_frame * 0.1) * 3
        rect.y += offset
        
        pygame.draw.rect(screen, self.color, rect)
        
        if self.type == "coin":
            pygame.draw.circle(screen, GOLD, rect.center, 10)
            pygame.draw.circle(screen, YELLOW, rect.center, 6)
        elif self.type == "gem":
            pygame.draw.polygon(screen, PURPLE, [
                (rect.centerx, rect.y),
                (rect.x + rect.width, rect.y + rect.height // 2),
                (rect.centerx, rect.y + rect.height),
                (rect.x, rect.y + rect.height // 2)
            ])
        elif self.type == "magnet":
            pygame.draw.rect(screen, RED, rect)
            pygame.draw.rect(screen, WHITE, (rect.x + 5, rect.y + 5, 10, 10))
        elif self.type == "speed":
            pygame.draw.polygon(screen, GREEN, [
                (rect.x, rect.y + rect.height),
                (rect.x + rect.width, rect.centery),
                (rect.x, rect.y)
            ])
        elif self.type == "invincibility":
            pygame.draw.circle(screen, YELLOW, rect.center, 12)
            pygame.draw.circle(screen, ORANGE, rect.center, 8)

class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw_game_ui(self, screen, score, coins, lives, speed, powerups):
        # Score
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Coins
        coin_text = self.font.render(f"Coins: {coins}", True, GOLD)
        screen.blit(coin_text, (10, 50))
        
        # Lives
        for i in range(lives):
            pygame.draw.circle(screen, RED, (10 + i * 30, 100), 10)
        
        # Speed indicator
        speed_text = self.small_font.render(f"Speed: {speed:.1f}", True, WHITE)
        screen.blit(speed_text, (10, 120))
        
        # Power-up timers
        y_offset = 150
        for powerup, timer in powerups.items():
            if timer > 0:
                text = self.small_font.render(f"{powerup}: {timer//60}s", True, WHITE)
                screen.blit(text, (10, y_offset))
                y_offset += 25
    
    def draw_menu(self, screen):
        screen.fill(BLACK)
        
        # Title
        title = self.big_font.render("TEMPLE RUN", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "SPACE/UP: Jump",
            "DOWN: Slide",
            "LEFT/RIGHT: Switch lanes",
            "P: Pause",
            "ESC: Menu",
            "",
            "Press SPACE to start!"
        ]
        
        y_offset = 300
        for line in instructions:
            text = self.font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 40
    
    def draw_game_over(self, screen, score, high_score):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over = self.big_font.render("GAME OVER", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(game_over, game_over_rect)
        
        # Score
        score_text = self.font.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        screen.blit(score_text, score_rect)
        
        # High score
        high_score_text = self.font.render(f"High Score: {high_score}", True, GOLD)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        screen.blit(high_score_text, high_score_rect)
        
        # Restart instruction
        restart_text = self.font.render("Press SPACE to restart or ESC for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        screen.blit(restart_text, restart_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Temple Run Style Game")
        self.clock = pygame.time.Clock()
        
        self.state = MENU
        self.player = Player()
        self.obstacles = []
        self.collectibles = []
        self.particles = []
        self.ui = UI()
        
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.game_speed = 8
        self.base_speed = 8
        self.distance = 0
        self.spawn_timer = 0
        self.collectible_timer = 0
        
        # Power-ups
        self.powerups = {
            "magnet": 0,
            "speed": 0,
            "invincibility": 0,
            "double_coins": 0
        }
        
        # Background layers for parallax
        self.bg_layers = [
            {"x": 0, "speed": 2, "color": (50, 50, 100)},
            {"x": 0, "speed": 4, "color": (70, 70, 120)},
            {"x": 0, "speed": 6, "color": (90, 90, 140)}
        ]
        
        # High score
        self.high_score = self.load_high_score()
        
        # Screen shake
        self.screen_shake = 0
        
        # Combo system
        self.combo = 0
        self.combo_timer = 0
        
    def load_high_score(self):
        try:
            with open("high_score.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open("high_score.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
    
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.collectibles = []
        self.particles = []
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.game_speed = self.base_speed
        self.distance = 0
        self.spawn_timer = 0
        self.collectible_timer = 0
        self.powerups = {
            "magnet": 0,
            "speed": 0,
            "invincibility": 0,
            "double_coins": 0
        }
        self.screen_shake = 0
        self.combo = 0
        self.combo_timer = 0
    
    def spawn_obstacle(self):
        if self.spawn_timer <= 0:
            lane = random.randint(0, 2)
            x = LANES[lane]
            y = SCREEN_HEIGHT - 100
            
            obstacle_types = ["barrier", "low", "pit", "moving"]
            obstacle_type = random.choice(obstacle_types)
            
            if obstacle_type == "pit":
                x = LANES[lane] - 60
            
            self.obstacles.append(Obstacle(x, y, obstacle_type))
            self.spawn_timer = random.randint(60, 120)
        else:
            self.spawn_timer -= 1
    
    def spawn_collectible(self):
        if self.collectible_timer <= 0:
            lane = random.randint(0, 2)
            x = LANES[lane]
            y = SCREEN_HEIGHT - 200
            
            # Determine collectible type based on rarity
            rand = random.random()
            if rand < 0.6:
                collectible_type = "coin"
            elif rand < 0.8:
                collectible_type = "gem"
            elif rand < 0.9:
                collectible_type = "magnet"
            elif rand < 0.95:
                collectible_type = "speed"
            else:
                collectible_type = "invincibility"
            
            self.collectibles.append(Collectible(x, y, collectible_type))
            self.collectible_timer = random.randint(30, 90)
        else:
            self.collectible_timer -= 1
    
    def check_collisions(self):
        player_rect = self.player.get_rect()
        
        # Check obstacle collisions
        for obstacle in self.obstacles[:]:
            if obstacle.get_rect().colliderect(player_rect):
                if not self.player.invincible:
                    self.lives -= 1
                    self.screen_shake = 20
                    self.add_particles(self.player.x, self.player.y, RED, 10)
                    
                    if self.lives <= 0:
                        self.state = GAME_OVER
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                    else:
                        # Brief invincibility after hit
                        self.player.invincible = True
                        self.player.invincible_timer = 120
                
                self.obstacles.remove(obstacle)
                break
        
        # Check collectible collisions
        for collectible in self.collectibles[:]:
            if collectible.get_rect().colliderect(player_rect) and not collectible.collected:
                collectible.collected = True
                self.collect_item(collectible)
                self.collectibles.remove(collectible)
    
    def collect_item(self, collectible):
        if collectible.type == "coin":
            coin_value = collectible.value
            if self.powerups["double_coins"] > 0:
                coin_value *= 2
            self.coins += coin_value
            self.score += coin_value
            self.combo += 1
            self.combo_timer = 120
            
        elif collectible.type == "gem":
            gem_value = collectible.value
            if self.powerups["double_coins"] > 0:
                gem_value *= 2
            self.coins += gem_value
            self.score += gem_value
            
        elif collectible.type == "magnet":
            self.powerups["magnet"] = 600  # 10 seconds
            
        elif collectible.type == "speed":
            self.powerups["speed"] = 300  # 5 seconds
            
        elif collectible.type == "invincibility":
            self.powerups["invincibility"] = 300  # 5 seconds
            self.player.invincible = True
            self.player.invincible_timer = 300
        
        # Add particle effect
        self.add_particles(collectible.x, collectible.y, collectible.color, 5)
    
    def add_particles(self, x, y, color, count):
        for _ in range(count):
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-5, -1)
            self.particles.append(Particle(x, y, color, velocity_x, velocity_y))
    
    def update_powerups(self):
        for powerup in self.powerups:
            if self.powerups[powerup] > 0:
                self.powerups[powerup] -= 1
                
                if powerup == "speed" and self.powerups[powerup] > 0:
                    self.game_speed = self.base_speed * 1.5
                elif powerup == "speed" and self.powerups[powerup] == 0:
                    self.game_speed = self.base_speed
                
                if powerup == "invincibility" and self.powerups[powerup] == 0:
                    self.player.invincible = False
                    self.player.invincible_timer = 0
    
    def update_game(self):
        # Update player
        self.player.update()
        
        # Update distance and score
        self.distance += self.game_speed
        self.score += 1
        
        # Increase difficulty over time
        if self.distance > 0 and self.distance % 500 == 0:
            self.base_speed += 0.5
            if self.powerups["speed"] == 0:
                self.game_speed = self.base_speed
        
        # Update combo
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        # Spawn obstacles and collectibles
        self.spawn_obstacle()
        self.spawn_collectible()
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.game_speed)
            if obstacle.x < -100:
                self.obstacles.remove(obstacle)
        
        # Update collectibles
        for collectible in self.collectibles[:]:
            collectible.update(self.game_speed)
            if collectible.x < -100:
                self.collectibles.remove(collectible)
        
        # Magnet effect
        if self.powerups["magnet"] > 0:
            for collectible in self.collectibles:
                if collectible.type in ["coin", "gem"]:
                    dx = self.player.x - collectible.x
                    dy = self.player.y - collectible.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < 150:
                        collectible.x += dx * 0.1
                        collectible.y += dy * 0.1
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update power-ups
        self.update_powerups()
        
        # Check collisions
        self.check_collisions()
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
    
    def draw_background(self):
        # Draw parallax background layers
        for layer in self.bg_layers:
            layer["x"] -= layer["speed"]
            if layer["x"] <= -SCREEN_WIDTH:
                layer["x"] = 0
            
            # Draw repeating background rectangles
            for x in range(int(layer["x"]), SCREEN_WIDTH + 100, 100):
                pygame.draw.rect(self.screen, layer["color"], (x, 0, 100, SCREEN_HEIGHT))
        
        # Draw ground
        pygame.draw.rect(self.screen, BROWN, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Draw lane dividers
        for i in range(1, 3):
            x = i * LANE_WIDTH
            pygame.draw.line(self.screen, WHITE, (x, SCREEN_HEIGHT - 100), (x, SCREEN_HEIGHT), 2)
    
    def draw_game(self):
        # Apply screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Fill screen
        self.screen.fill(BLACK)
        
        # Draw background
        self.draw_background()
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self.ui.draw_game_ui(self.screen, self.score, self.coins, self.lives, self.game_speed, self.powerups)
        
        # Draw combo
        if self.combo > 1:
            combo_text = self.ui.font.render(f"COMBO x{self.combo}", True, YELLOW)
            self.screen.blit(combo_text, (SCREEN_WIDTH - 200, 10))
        
        # Apply shake offset
        if shake_x != 0 or shake_y != 0:
            # This is a simplified shake effect
            pass
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = PLAYING
                        self.reset_game()
                
                elif self.state == PLAYING:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.player.jump()
                    elif event.key == pygame.K_DOWN:
                        self.player.slide()
                    elif event.key == pygame.K_LEFT:
                        self.player.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.move_right()
                    elif event.key == pygame.K_p:
                        self.state = PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
                
                elif self.state == PAUSED:
                    if event.key == pygame.K_p:
                        self.state = PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
                
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.state = PLAYING
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
        
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if self.state == PLAYING:
                self.update_game()
                self.draw_game()
            elif self.state == MENU:
                self.ui.draw_menu(self.screen)
            elif self.state == PAUSED:
                self.draw_game()
                # Draw pause overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                pause_text = self.ui.big_font.render("PAUSED", True, WHITE)
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)
            elif self.state == GAME_OVER:
                self.draw_game()
                self.ui.draw_game_over(self.screen, self.score, self.high_score)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()