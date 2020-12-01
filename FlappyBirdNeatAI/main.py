import os
import random
import pygame
import neat

generation = 0
max_fitness = 0


class Sprites:
    brird_sprite = [pygame.image.load(f'assets/fb{n}.png') for n in [1, 2]]
    pipe_sprite = pygame.image.load('assets/pipe.png')
    background = pygame.image.load('assets/bg.png')


class Bird:
    WIDTH, HEIGHT = SIZE = 80, 60
    GRAVITY = 3.5
    JUMP_VEL = 20
    OFFSET = 50

    def __init__(self, genome, net):
        self.genome = genome
        self.genome.fitness = 0
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.x = Bird.OFFSET
        self.y = Game.HEIGHT/2
        self.jump_vel = 0
        self.sprite_index = 0
        self.dead = False

    def draw(self):
        self.sprite_index = (self.sprite_index+1) % len(Sprites.brird_sprite)
        sprite = Sprites.brird_sprite[self.sprite_index]
        angle = Bird.rotatation_angle(self.jump_vel)
        rotated_image = pygame.transform.rotate(sprite, angle)
        new_rect = rotated_image.get_rect(
            center=sprite.get_rect(topleft=(self.x, self.y)).center)
        Game.screen.blit(rotated_image, new_rect.topleft)

    @staticmethod
    def rotatation_angle(vel):
        return max(vel / Bird.JUMP_VEL * 60, -60)

    def update(self, pipes):
        if self.dead:
            self.x -= Pipe.VEL
        else:
            self.y = max(self.y - self.jump_vel, 0)
            self.jump_vel -= Bird.GRAVITY

            if self.get_collision(pipes):
                self.dead = True

            # activation
            activation_args = [self.y]
            pipes_ahead = list(
                filter(lambda p: p.x + Pipe.WIDTH > self.x, pipes))
            if not len(pipes_ahead):
                activation_args += [Game.HEIGHT/2]
            else:
                activation_args += [pipes_ahead[0].bot_y]

            output = self.net.activate(activation_args)

            self.genome.fitness += 0.1
            if output[0] > 0.5:
                self.jump()

        self.draw()

    def jump(self):
        self.jump_vel = Bird.JUMP_VEL

    def get_collision(self, pipes=None):
        if self.y >= Game.HEIGHT - Bird.HEIGHT:
            self.genome.fitness -= 1
            return True

        bird_mask = pygame.mask.from_surface(
            Sprites.brird_sprite[self.sprite_index])

        for pipe in pipes:
            def to_int(*arr): return list(int(v) for v in arr)
            offset_bot = to_int(pipe.x - self.x, pipe.bot_y - self.y)
            offset_top = to_int(pipe.x - self.x, pipe.top_y - self.y)
            pipe_top, pipe_bot = pipe.get_masks()

            offset = 0
            if bird_mask.overlap(pipe_top, offset_top):
                offset = pipe.top_y + Game.HEIGHT - self.y

            if bird_mask.overlap(pipe_bot, offset_bot):
                offset = self.y-pipe.bot_y

            if offset:
                self.genome.fitness -= offset/100
                return True

        return False


class Pipe:
    WIDTH = 150
    OFFSET = 80
    GAP = 250
    VEL = 10

    def __init__(self):
        self.x = Game.WIDTH
        self.pipe_top = Sprites.pipe_sprite
        self.pipe_bot = pygame.transform.flip(Sprites.pipe_sprite, False, True)
        self.bot_y = random.randrange(
            Pipe.GAP + Pipe.OFFSET, Game.HEIGHT - Pipe.OFFSET)
        self.top_y = self.bot_y - Pipe.GAP - Game.HEIGHT
        self.passed = False

    def draw(self):
        Game.screen.blit(self.pipe_top, (self.x, self.top_y))
        Game.screen.blit(self.pipe_bot, (self.x, self.bot_y))

    def update(self):
        self.x -= Pipe.VEL
        self.draw()

    def get_masks(self):
        return [pygame.mask.from_surface(surf)
                for surf in [self.pipe_bot, self.pipe_top]]


class Game():
    WIDTH, HEIGHT = SIZE = 500, 900
    FPS = 30
    BG_VEL = 5
    PIPE_SPREAD = 600

    pygame.init()
    pygame.display.set_caption("Flappy Birb")
    screen = pygame.display.set_mode((SIZE))
    clock = pygame.time.Clock()

    def __init__(self):
        self.scale_sprites()

    @staticmethod
    def check_close():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    @staticmethod
    def scale_sprites():
        Sprites.background = pygame.transform.scale(
            Sprites.background, (Game.WIDTH*2, Game.HEIGHT))
        Sprites.brird_sprite = [
            pygame.transform.scale(b, Bird.SIZE) for b in Sprites.brird_sprite]
        Sprites.pipe_sprite = pygame.transform.scale(
            Sprites.pipe_sprite, (Pipe.WIDTH, Game.HEIGHT))

    @staticmethod
    def display_text(text, pos, size=30, color=(230, 250, 230), center=False):
        font = pygame.font.SysFont('comicsans', size)
        text = font.render(f'{text}', 1, color)
        list(pos)[0] -= int(text.get_width()/2) * center
        Game.screen.blit(text, pos)

    @staticmethod
    def display_info(generation, max_fitness, gen_max_fitness):
        color = (230, 250, 230)
        infos = [
            f'Generation: {generation}',
            f'Max fitness: {round(max_fitness,3)}',
            f'Max fitness this generation: {round(gen_max_fitness,3)}'
        ]

        for i, info in enumerate(infos):
            Game.display_text(text=info, pos=(10, 10+i*20), color=color)

    def game_loop(self, genomes, config):
        birds = [Bird(genome, config) for _, genome in genomes]
        pipes = []
        bg_x = 0
        pipe_distance = Game.PIPE_SPREAD

        global generation
        global max_fitness
        generation += 1
        gen_max_fitness = 0

        while len(list(filter(lambda b: not b.dead, birds))):
            Game.clock.tick(Game.FPS)

            # update background
            bg_x = bg_x - Game.BG_VEL * (not bg_x < -Game.WIDTH)
            Game.screen.blit(Sprites.background, (bg_x, 0))

            # update pipes
            for pipe in pipes:
                pipe.update()
            pipes = list(filter(lambda p: not p.x < -Pipe.WIDTH, pipes))

            pipe_distance += Pipe.VEL
            if pipe_distance > Game.PIPE_SPREAD:
                pipes.append(Pipe())
                pipe_distance = 0

            # update birds
            for bird in birds:
                gen_max_fitness = max(gen_max_fitness, bird.genome.fitness)
                bird.update(pipes)

            max_fitness = max(gen_max_fitness, max_fitness)

            Game.display_info(generation, max_fitness, gen_max_fitness)
            Game.check_close()
            pygame.display.update()


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    game = Game()
    winner = p.run(game.game_loop, 50)
