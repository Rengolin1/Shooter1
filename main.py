from pygame import *
from random import *
FPS = 60
GAME_FINISHED, GAME_RUN = False, True
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
CLOCK = time.Clock()

KILLS, LOST = 0, 0

WINDOW = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display.set_caption("Shooter")

mixer.init()

mixer.music.load("music.mp3")
mixer_music.set_volume(0.025)
mixer.music.play()

fire_sound = mixer.Sound("fire.mp3")
exp_sound = mixer.Sound("exp.mp3")
pass_sound = mixer.Sound("pass.mp3")
win_sound = mixer.Sound("win.mp3")
game_over = mixer.Sound("game-over.mp3")
font.init()
score_font = font.SysFont("Arial", 32, True)
main_font = font.SysFont("Arial", 72, True)
class GameSprite(sprite.Sprite):
    def __init__(self, img, position, size, speed):
        super().__init__()

        self.image = transform.smoothscale(
            image.load(img),
            size
        )

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.speed = speed
        self.width, self.height = size

    def reset(self):
        WINDOW.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    fire_delay = FPS * 0.25
    fire_timer = fire_delay
    can_fire = True

    def update(self):

        if not self.can_fire:
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                self.fire_timer = self.fire_delay
                self.can_fire = True

        keys = key.get_pressed()
        if keys[K_a]:
            if self.rect.x > 0:
                self.rect.x -= self.speed
        if keys[K_d]:
            if self.rect.x < WINDOW_WIDTH - self.width:
                self.rect.x += self.speed
        
        if keys[K_SPACE] and self.can_fire:
            fire_sound.play()
            self.fire()
            self.can_fire = False

    def fire(self):
        new_bullet = Bullet(img="bullet.png",
                           position=(self.rect.centerx - 4, self.rect.y),
                           size=(8, 8),
                           speed=10)
        
        bullets_group.add(new_bullet)

class Enemy(GameSprite):
    def __init__(self, img, position, size, speed, health):
        super().__init__(img, position, size, speed)

        self.health = health
        
    def update(self):
        global LOST

        self.rect.y += self.speed

        self.health_text = score_font.render(str(self.health), True, (255, 255, 255))
        WINDOW.blit(self.health_text, self.rect.bottomleft)
        if self.rect.y >= WINDOW_HEIGHT or sprite.collide_rect(self, player):
            LOST += 1
            pass_sound.play()
            self.kill()

class Bullet(GameSprite):
    def update(self):
        global KILLS

        self.rect.y -= self.speed

        enemys_colided_list = sprite.spritecollide(self, enemys_group, False)

        if self.rect.y <= 0:
            self.kill()

        if len(enemys_colided_list) > 0:

            enemy = enemys_colided_list[0]
            if enemy.health > 1:
                enemy.health -= 1
            else:
                KILLS += 1
                exp_sound.play()
                enemy.kill()

            self.kill()

bg = GameSprite(img="bg.jpg",
                position=(0, 0),
                size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                speed=0)

player = Player(img="player.png",
                position=(5, WINDOW_HEIGHT - 64),
                size=(96, 64),
                speed=7)

enemys_group = sprite.Group()
bullets_group = sprite.Group()
enemys_spawn_delay = FPS * 0.25
enemys_spawn_timer = enemys_spawn_delay

while GAME_RUN:
    
    for ev in event.get():
        if ev.type == QUIT:
            GAME_RUN = False

    bg.reset()
    player.reset()
    enemys_group.draw(WINDOW)
    bullets_group.draw(WINDOW)

    if KILLS >= 15:
        screen_text = main_font.render("Ты победил!", True, (0, 255, 0))
        WINDOW.blit(screen_text, (WINDOW_WIDTH / 2 - screen_text.get_width() / 2,
                                  WINDOW_HEIGHT / 2 - screen_text.get_height() / 2))
        win_sound.play()
        GAME_FINISHED = True

    if LOST >= 15:
        screen_text = main_font.render("Ты проиграл!", True, (255, 0, 0))
        WINDOW.blit(screen_text, (WINDOW_WIDTH / 2 - screen_text.get_width() / 2,
                                  WINDOW_HEIGHT / 2 - screen_text.get_height() / 2))
        game_over.play()
        GAME_FINISHED = True

    
    if not GAME_FINISHED:
        if enemys_spawn_timer > 0:
            enemys_spawn_timer -= 1
        else:
            new_enemy = Enemy(img="enemy.png",
                              position=(randint(100, WINDOW_WIDTH - 100), -100),
                              size=(96, 64),
                              speed=randint(2, 7),
                              health=randint(1, 3))
            
            enemys_group.add(new_enemy)
            enemys_spawn_timer = enemys_spawn_delay

    player.update()
    enemys_group.update()
    bullets_group.update()
        
    kills_text = score_font.render("Убито:" + str(KILLS), True, (255, 255, 255))
    lost_text = score_font.render("Пропущено:" + str(LOST), True, (255, 255, 255))

    WINDOW.blit(kills_text, (5, 5))
    WINDOW.blit(lost_text, (5, 37))

    display.update()
    CLOCK.tick(FPS)
