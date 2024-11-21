import pygame
import sys
import random

# Inicialize o Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1200, 600
DARK_GRAY = (50, 50, 50)
COIN_COLOR = (255, 215, 0)
FONT_COLOR = (255, 255, 255)
GRAVITY = 1
GROUND_HEIGHT = 50
ENEMY_COLOR = (255, 0, 0)
BULLET_COLOR = (255, 255, 0)

# Configurações da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 74)

# Carregar a imagem do jogador
player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (140, 150))

# Carregar a imagem do inimigo
enemy_image = pygame.image.load('E.T.png')
enemy_image = pygame.transform.scale(enemy_image, (160, 180))

# Definir classes do jogo

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(100, HEIGHT - GROUND_HEIGHT - 60))
        self.collision_rect = self.rect.copy()
        self.collision_rect.width = self.rect.width // 2
        self.dx = 5
        self.dy = 0
        self.jump_height = 20
        self.is_on_ground = False
        self.can_double_jump = True
        self.is_crouching = False
        self.score = 0
        self.lives = 3
        self.facing_right = True

    def update(self):
        self.dy += GRAVITY
        self.rect.y += self.dy
        self.collision_rect.topleft = self.rect.topleft

        if self.is_crouching:
            self.rect.height = 60
            self.collision_rect.height = 60
        else:
            self.rect.height = 120
            self.collision_rect.height = 120

        self.collision_rect.x = self.rect.x + (self.rect.width - self.collision_rect.width) // 2

        if self.rect.bottom > HEIGHT - GROUND_HEIGHT:
            self.rect.bottom = HEIGHT - GROUND_HEIGHT
            self.dy = 0
            self.is_on_ground = True
            self.can_double_jump = True
        else:
            self.is_on_ground = False

    def jump(self):
        if self.is_on_ground:
            self.dy = -self.jump_height
            self.is_on_ground = False
            self.can_double_jump = True
        elif self.can_double_jump:
            self.dy = -self.jump_height
            self.can_double_jump = False

    def move(self, direction):
        self.rect.x += direction * self.dx

    def crouch(self):
        self.is_crouching = True

    def stand_up(self):
        self.is_crouching = False

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = 10 * direction

    def update(self):
        self.rect.x += self.dx
        if self.rect.x > WIDTH or self.rect.x < 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(x, y))
        self.collision_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 30, self.rect.width - 40, self.rect.height - 60)
        self.lives = 3
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 2000

    def update(self):
        self.collision_rect.topleft = (self.rect.x + 20, self.rect.y + 30)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = current_time

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery, -1)
        bullets.add(bullet)

    def take_damage(self):
        self.lives -= 1
        print(f"Inimigo atingido! Vidas restantes: {self.lives}")
        if self.lives <= 0:
            print("Inimigo derrotado!")
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        pygame.draw.rect(surface, (0, 255, 0), self.collision_rect, 2)

def generate_levels(num_levels):
    levels = []
    for i in range(num_levels):
        platforms = []
        coins = []
        enemies = []
        num_platforms = random.randint(3, 6 + i // 5)
        for _ in range(num_platforms):
            width = random.randint(100, 300)
            height = 20
            x = random.randint(0, WIDTH - width)
            y = random.randint(100, 400 - (i // 5) * 10)
            platforms.append(pygame.Rect(x, y, width, height))

        max_enemies = 2
        while len(enemies) < max_enemies:
            platform = random.choice(platforms)
            enemy_x = random.randint(platform.left + 10, platform.right - 10)
            enemy_y = platform.top - 30
            enemy = Enemy(enemy_x, enemy_y)
            enemies.append(enemy)

        for platform in platforms:
            num_coins_on_platform = random.randint(1, 3)
            for _ in range(num_coins_on_platform):
                coin_x = random.randint(platform.x + 10, platform.x + platform.width - 10)
                coin_rect = pygame.Rect(coin_x, platform.y - 10, 10, 10)
                coins.append(coin_rect)

        levels.append({"platforms": platforms, "enemies": enemies, "coins": coins})
    return levels

levels = generate_levels(5)
player = Player()
bullets = pygame.sprite.Group()
game_over = False
current_level = 0

def shoot():
    direction = 1 if player.facing_right else -1
    bullet = Bullet(player.rect.centerx, player.rect.centery, direction)
    bullets.add(bullet)

def main():
    global current_level
    global game_over
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_DOWN:
                    player.crouch()
                if event.key == pygame.K_SPACE:
                    shoot()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.stand_up()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1)
            player.facing_right = False
        if keys[pygame.K_RIGHT]:
            player.move(1)
            player.facing_right = True

        player.update()
        update_enemies()
        update_bullets()
        handle_collisions()

        if player.rect.right >= WIDTH:
            current_level += 1
            if current_level >= len(levels):
                current_level = 0
            player.rect.x = 100

        draw_scene()

        if game_over:
            show_game_over()
            break

        clock.tick(60)

def update_enemies():
    for enemy in levels[current_level]["enemies"]:
        enemy.update()

def update_bullets():
    for bullet in bullets:
        bullet.update()

def handle_collisions():
    global game_over
    coins_to_remove = []

    for platform in levels[current_level]["platforms"]:
        if player.collision_rect.colliderect(platform):
            if player.dy > 0 and player.rect.bottom >= platform.top and player.rect.y - player.dy < platform.top:
                player.rect.bottom = platform.top
                player.dy = 0
                player.is_on_ground = True
                player.can_double_jump = True
            elif player.dy < 0 and player.rect.top <= platform.bottom and player.rect.y - player.dy > platform.bottom:
                player.rect.top = platform.bottom
                player.dy = 0

    for enemy in levels[current_level]["enemies"]:
        if player.collision_rect.colliderect(enemy.rect):
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
            enemy.take_damage()

    for bullet in bullets:
        for enemy in levels[current_level]["enemies"]:
            if bullet.rect.colliderect(enemy.collision_rect):
                enemy.take_damage()
                bullet.kill()

    for coin in levels[current_level]["coins"]:
        if player.collision_rect.colliderect(coin):
            player.score += 1
            coins_to_remove.append(coin)

    for coin in coins_to_remove:
        levels[current_level]["coins"].remove(coin)

def draw_scene():
    screen.fill((173, 216, 230))  # Cor de fundo azul claro
    pygame.draw.rect(screen, DARK_GRAY, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    player.draw(screen)
    for platform in levels[current_level]["platforms"]:
        pygame.draw.rect(screen, (100, 100, 100), platform)
    for coin in levels[current_level]["coins"]:
        pygame.draw.circle(screen, COIN_COLOR, coin.center, 10)
    for enemy in levels[current_level]["enemies"]:
        enemy.draw(screen)
    bullets.draw(screen)
    score_text = font.render(f"Score: {player.score}", True, FONT_COLOR)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()

def show_game_over():
    game_over_text = font.render("GAME OVER", True, FONT_COLOR)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()

if __name__ == "__main__":
    main()
