"""
CONTROLES
En cualquier lugar -> ESC: salir
Menú principal -> 1: nivel anterior. 2: siguiente nivel. SPACE: iniciar juego.
Juego -> SPACE/UP: saltar y activar el orbe.
    Orbe: salto en el aire cuando se activa
Si mueres o completas el nivel, presiona SPACE para reiniciar o pasar al siguiente nivel
"""
import csv
import os
import random
import pygame
from pygame.math import Vector2
from pygame.draw import rect

# Inicializa el módulo pygame
pygame.init()

# Crea una pantalla de tamaño 800 x 600 píxeles
screen = pygame.display.set_mode([800, 600])

# Controla el bucle principal del juego
done = False

# Controla si el juego inicia desde el menú principal
start = False

# Establece la tasa de fotogramas del programa
clock = pygame.time.Clock()

"""
CONSTANTES
"""
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Función lambda para generar un color aleatorio
color = lambda: tuple([random.randint(0, 255) for i in range(3)])
GRAVITY = Vector2(0, 0.86)  # Vector de gravedad para el jugador

"""
Clase principal para el jugador
"""

class Player(pygame.sprite.Sprite):
    """Clase que representa al jugador. Contiene métodos de actualización, variables de victoria y muerte, colisiones y más."""
    win: bool
    died: bool

    def __init__(self, image, platforms, pos, *groups):
        """
        Inicializa el jugador
        :param image: imagen del avatar del jugador
        :param platforms: obstáculos como monedas, bloques, picos y orbes
        :param pos: posición inicial del jugador
        :param groups: acepta cualquier cantidad de grupos de sprites
        """
        super().__init__(*groups)
        self.onGround = False  # ¿El jugador está en el suelo?
        self.platforms = platforms  # Lista de obstáculos
        self.died = False  # ¿El jugador ha muerto?
        self.win = False  # ¿El jugador ha ganado el nivel?

        self.image = pygame.transform.smoothscale(image, (32, 32))
        self.rect = self.image.get_rect(center=pos)  # Rectángulo de la imagen del jugador
        self.jump_amount = 12  # Fuerza del salto
        self.particles = []  # Rastro de partículas detrás del jugador
        self.isjump = False  # ¿El jugador está saltando?
        self.vel = Vector2(0, 0)  # Velocidad inicial en cero

    def draw_particle_trail(self, x, y, color=(255, 255, 255)):
        """Dibuja un rastro de partículas detrás del jugador."""
        
        self.particles.append(
            [[x - 5, y - 8], [random.randint(0, 25) / 10 - 1, 0], random.randint(5, 8)]
        )

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.5
            particle[1][0] -= 0.4
            rect(alpha_surf, color, ([int(particle[0][0]), int(particle[0][1])], [int(particle[2])] * 2))
            if particle[2] <= 0:
                self.particles.remove(particle)


    def collide(self, yvel, platforms):
        """Gestiona las colisiones del jugador con las plataformas y otros objetos."""
    
        global coins

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                # Método de colisión incorporado de pygame.sprite
                # Comprueba si el jugador está colisionando con algún obstáculo
                if isinstance(p, Orb) and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
                    pygame.draw.circle(alpha_surf, (255, 255, 0), p.rect.center, 18)
                    screen.blit(pygame.image.load("images/editor-0.9s-47px.gif"), p.rect.center)
                    self.jump_amount = 12  # Aumenta la fuerza de salto al tocar un orbe
                    self.jump()
                    self.jump_amount = 10  # Restaura la fuerza de salto a su valor original

                if isinstance(p, End):
                    self.win = True  # Marca victoria al llegar al final del nivel

                if isinstance(p, Spike):
                    self.died = True  # Marca muerte al tocar un pico

                if isinstance(p, Coin):
                    # Lleva el registro de todas las monedas obtenidas en el juego (máximo de 6)
                    coins += 1

                    # Borra la moneda
                    p.rect.x = 0
                    p.rect.y = 0

                if isinstance(p, Platform):  # Estas son las plataformas (puede ser confuso debido a self.platforms)

                    if yvel > 0:
                        # Si el jugador está cayendo (yvel es positivo)
                        self.rect.bottom = p.rect.top  # Evita que el jugador atraviese el suelo
                        self.vel.y = 0  # Restaura la velocidad en y porque el jugador está en el suelo

                        # Establece self.onGround en True porque el jugador está en el suelo
                        self.onGround = True

                        # Reinicia el salto
                        self.isjump = False
                    elif yvel < 0:
                        # Si yvel es negativo, el jugador colisionó mientras saltaba
                        self.rect.top = p.rect.bottom  # La parte superior del jugador se establece en la parte inferior del bloque, como si golpeara su cabeza
                    else:
                        # De lo contrario, si el jugador choca con un bloque, muere
                        self.vel.x = 0
                        self.rect.right = p.rect.left  # Evita que el jugador atraviese paredes
                        self.died = True

    def jump(self):
        """Hace que el jugador salte"""
        self.vel.y = -self.jump_amount  # La velocidad vertical del jugador es negativa (salto hacia arriba)

    def update(self):
        """Actualiza el estado del jugador"""
        if self.isjump:
            if self.onGround:
                # Si el jugador quiere saltar y está en el suelo, solo entonces se permite el salto
                self.jump()

        if not self.onGround:  # Acelera con la gravedad solo si está en el aire
            self.vel += GRAVITY  # Aplica la gravedad

            # Velocidad máxima de caída
            if self.vel.y > 100: 
                self.vel.y = 100

        # Colisiones en el eje X
        self.collide(0, self.platforms)

        # Incremento en la dirección Y
        self.rect.top += self.vel.y

        # Se asume que el jugador está en el aire; si no, se ajustará en collide
        self.onGround = False

        # Colisiones en el eje Y
        self.collide(self.vel.y, self.platforms)

        # Verifica si el jugador ganó o murió
        eval_outcome(self.win, self.died)


"""
Clases de Obstáculos
"""


# Clase principal
class Draw(pygame.sprite.Sprite):
    """Clase padre para todos los obstáculos; hereda de Sprite"""

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


# =========================================================================================================
# Clases para todos los tipos de obstáculos. Esto puede parecer repetitivo, pero es útil en ciertos casos.
# =========================================================================================================

# Clase hija para plataformas
class Platform(Draw):
    """Clase para representar los bloques"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

# =========================================================================================================
# Clases para todos los tipos de obstáculos. Esto puede parecer repetitivo, pero es útil en ciertos casos.
# =========================================================================================================

# Clases hijas de Draw
class Platform(Draw):
    """bloque"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):
    """pico"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Coin(Draw):
    """moneda. Obtén 6 para ganar el juego"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Orb(Draw):
    """orbe. Presiona espacio o flecha hacia arriba mientras estás sobre él para saltar en el aire"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Trick(Draw):
    """bloque, pero es un truco porque puedes atravesarlo"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class End(Draw):
    """coloca esto al final del nivel"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


"""
Funciones
"""


def init_level(map):
    """Similar a listas 2D. Recorre una lista de listas y crea instancias de ciertos obstáculos 
    dependiendo del elemento en la lista."""
    x = 0
    y = 0

    for row in map:
        for col in row:

            if col == "0":
                Platform(block, (x, y), elements)

            if col == "Coin":
                Coin(coin, (x, y), elements)

            if col == "Spike":
                Spike(spike, (x, y), elements)

            if col == "Orb":
                orbs.append([x, y])
                Orb(orb, (x, y), elements)

            if col == "T":
                Trick(trick, (x, y), elements)

            if col == "End":
                End(avatar, (x, y), elements)
            x += 32
        y += 32
        x = 0


def blitRotate(surf, image, pos, originpos: tuple, angle: float):
    """
    Rota la imagen del jugador
    :param surf: Superficie en la que se dibuja
    :param image: imagen a rotar
    :param pos: posición de la imagen
    :param originpos: posición x, y del origen alrededor del cual rotar
    :param angle: ángulo de rotación
    """
    # Calcula el cuadro delimitador alineado al eje de la imagen rotada
    w, h = image.get_size()
    box = [Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]

    # Asegura que el jugador no se sobreponga; usa algunas funciones lambda (nuevas cosas que no aprendimos en número 1)
    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # Calcula la traslación del pivote
    pivot = Vector2(originpos[0], -originpos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move = pivot_rotate - pivot

    # Calcula el origen en la esquina superior izquierda de la imagen rotada
    origin = (pos[0] - originpos[0] + min_box[0] - pivot_move[0], pos[1] - originpos[1] - max_box[1] + pivot_move[1])

    # Obtén una imagen rotada
    rotated_image = pygame.transform.rotozoom(image, angle, 1)

    # Rota y dibuja la imagen
    surf.blit(rotated_image, origin)

def won_screen():
    """Muestra esta pantalla cuando se completa un nivel"""
    global attempts, level, fill
    attempts = 0
    player_sprite.clear(player.image, screen)
    screen.fill(pygame.Color("yellow"))
    txt_win1 = txt_win2 = "Nada"
    if level == 1:
        if coins == 6:
            txt_win1 = f"Monedas: {coins}/6! "
            txt_win2 = "¡Completaste el juego, Felicitaciones!"
    else:
        txt_win1 = f"Nivel {level}"
        txt_win2 = f"Monedas: {coins}/6. "
    txt_win = f"{txt_win1} Completaste {txt_win2}! Presiona ESPACIO para reiniciar, o ESC para salir"

    won_game = font.render(txt_win, True, BLUE)

    screen.blit(won_game, (200, 300))
    level += 1

    wait_for_key()
    reset()


def death_screen():
    """Muestra esta pantalla al morir"""
    global attempts, fill
    fill = 0
    player_sprite.clear(player.image, screen)
    attempts += 1
    game_over = font.render("Game Over. [ESPACIO] para reiniciar", True, WHITE)

    screen.fill(pygame.Color("sienna1"))
    screen.blits([[game_over, (100, 100)], [tip, (100, 400)]])

    wait_for_key()
    reset()


def eval_outcome(won: bool, died: bool):
    """Función sencilla para mostrar la pantalla de ganar o morir después de verificar si se ganó o murió"""
    if won:
        won_screen()
    if died:
        death_screen()


def block_map(level_num):
    """
    :type level_num: rect(screen, BLACK, (0, 0, 32, 32))
    Abre un archivo CSV que contiene el mapa correcto del nivel
    """
    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl


def start_screen():
    """Pantalla de inicio. Opción para cambiar de nivel, guía de controles y visión general del juego."""
    global level
    if not start:
        screen.fill(BLACK)
        if pygame.key.get_pressed()[pygame.K_1]:
            level = 0
        if pygame.key.get_pressed()[pygame.K_2]:
            level = 1

        welcome = font.render(f"Bienvenido a Pydash.", True, WHITE)
        welcome1 = font.render(f"Elige nivel ({level + 1})  con el teclado numérico", True, WHITE)
        controls = font.render("Controles: salto: Espacio/Arriba, salir: Esc", True, GREEN)

        screen.blits([[welcome, (50, 100)],[welcome1, (50, 150)] ,[controls, (50, 400)], [tip, (50, 500)]])

        level_memo = font.render(f"Nivel {level + 1}.", True, (255, 255, 0))
        screen.blit(level_memo, (50, 200))


def reset():
    """Restablece los grupos de sprites, música, etc. para reiniciar en caso de muerte o nuevo nivel"""
    global player, elements, player_sprite, level

    if level == 1:
        pygame.mixer.music.load(os.path.join("music", "castle-town.mp3"))
    pygame.mixer_music.play()
    player_sprite = pygame.sprite.Group()
    elements = pygame.sprite.Group()
    player = Player(avatar, elements, (150, 150), player_sprite)
    init_level(block_map(level_num=levels[level]))


def move_map():
    """Mueve los obstáculos a lo largo de la pantalla"""
    for sprite in elements:
        sprite.rect.x -= CameraX


def draw_stats(surf, money=0):
    """
    Dibuja la barra de progreso del nivel, el número de intentos, muestra las monedas recolectadas 
    y cambia progresivamente el color de la barra de progreso.
    """
    global fill
    progress_colors = [pygame.Color("red"), pygame.Color("orange"), pygame.Color("yellow"), pygame.Color("lightgreen"),
                       pygame.Color("green")]

    tries = font.render(f"Intento {str(attempts)}", True, WHITE)
    BAR_LENGTH = 600
    BAR_HEIGHT = 10
    for i in range(1, money):
        screen.blit(coin, (BAR_LENGTH, 25))
    fill += 0.5
    outline_rect = pygame.Rect(0, 0, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(0, 0, fill, BAR_HEIGHT)
    col = progress_colors[int(fill / 100)]
    rect(surf, col, fill_rect, 0, 4)
    rect(surf, WHITE, outline_rect, 3, 4)
    screen.blit(tries, (BAR_LENGTH, 0))

def wait_for_key():
    """Bucle separado del juego para esperar la pulsación de una tecla mientras sigue corriendo el bucle principal del juego"""
    global level, start
    waiting = True
    while waiting:
        clock.tick(60)
        pygame.display.flip()

        if not start:
            start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()


def coin_count(coins):
    """Cuenta las monedas"""
    if coins >= 3:
        coins = 3
    coins += 1
    return coins


def resize(img, size=(32, 32)):
    """Redimensiona las imágenes
    :param img: imagen a redimensionar
    :type img: no estoy seguro, probablemente un objeto
    :param size: el tamaño por defecto es 32 porque ese es el tamaño de los bloques
    :type size: tupla
    :return: imagen redimensionada

    :rtype: objeto?
    """
    resized = pygame.transform.smoothscale(img, size)
    return resized


"""
Variables globales
"""
font = pygame.font.SysFont("lucidaconsole", 20)

# El bloque cuadrado con cara es el personaje principal, y es el ícono de la ventana del juego
avatar = pygame.image.load(os.path.join("images", "avatar.png"))  # Carga el personaje principal
pygame.display.set_icon(avatar)

# Esta superficie tiene un valor alfa con los colores, así que el rastro del jugador se desvanecerá usando opacidad
alpha_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

# Grupos de sprites
player_sprite = pygame.sprite.Group()
elements = pygame.sprite.Group()

# Imágenes
spike = pygame.image.load(os.path.join("images", "obj-spike.png"))
spike = resize(spike)
coin = pygame.image.load(os.path.join("images", "coin.png"))
coin = pygame.transform.smoothscale(coin, (32, 32))
block = pygame.image.load(os.path.join("images", "block_1.png"))
block = pygame.transform.smoothscale(block, (32, 32))
orb = pygame.image.load((os.path.join("images", "orb-yellow.png")))
orb = pygame.transform.smoothscale(orb, (32, 32))
trick = pygame.image.load((os.path.join("images", "obj-breakable.png")))
trick = pygame.transform.smoothscale(trick, (32, 32))

# Enteros
fill = 0
num = 0
CameraX = 0
attempts = 0
coins = 0
angle = 0
level = 0

# Listas
particles = []
orbs = []
win_cubes = []

# Inicializa el nivel con
levels = ["level_1.csv", "level_2.csv"]
level_list = block_map(levels[level])
level_width = (len(level_list[0]) * 32)
level_height = len(level_list) * 32
init_level(level_list)

# Establece el título de la ventana adecuado para el juego
pygame.display.set_caption('Pydash: Geometry Dash en Python')

# Inicializa la variable de la fuente para dibujar texto más tarde
text = font.render('imagen', False, (255, 255, 0))

# Música
music = pygame.mixer_music.load(os.path.join("music", "bossfight-Vextron.mp3"))
pygame.mixer_music.play()

# Imagen de fondo
bg = pygame.image.load(os.path.join("images", "bg.png"))

# Crea el objeto de la clase Player
player = Player(avatar, elements, (150, 150), player_sprite)
# mostrar consejo al inicio y al morir
tip = font.render("consejo:toca y mantén presionado durante los primeros segundos del nivel", True, BLUE)

while not done:
    keys = pygame.key.get_pressed()

    if not start:
        wait_for_key()
        reset()

        start = True

    player.vel.x = 6

    eval_outcome(player.win, player.died)
    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
        player.isjump = True

    # Reduce el alfa de todos los píxeles en esta superficie en cada fotograma.
    # Controla la velocidad del desvanecimiento con el valor alfa.

    alpha_surf.fill((255, 255, 255, 1), special_flags=pygame.BLEND_RGBA_MULT)

    player_sprite.update()
    CameraX = player.vel.x  # para mover los obstáculos
    move_map()  # aplica CameraX a todos los elementos

    screen.blit(bg, (0, 0))  # Borra la pantalla (con el fondo)

    player.draw_particle_trail(player.rect.left - 1, player.rect.bottom + 2,
                               WHITE)
    screen.blit(alpha_surf, (0, 0))  # Dibuja alpha_surf en la pantalla.
    draw_stats(screen, coin_count(coins))

    if player.isjump:
        """Rota al jugador por un ángulo y dibuja si el jugador está saltando"""
        angle -= 8.1712  # este puede ser el ángulo necesario para hacer un giro de 360 grados en el espacio cubierto en un salto por el jugador
        blitRotate(screen, player.image, player.rect.center, (16, 16), angle)
    else:
        """Si player.isjump es falso, simplemente dibuja normalmente (usando Group().draw() para los sprites)"""
        player_sprite.draw(screen)  # dibuja el grupo de sprites del jugador
    elements.draw(screen)  # dibuja todos los demás obstáculos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                """Salida amigable para el usuario"""
                done = True
            if event.key == pygame.K_2:
                """Cambia el nivel con el teclado"""
                player.jump_amount += 1

            if event.key == pygame.K_1:
                """Cambia el nivel con el teclado"""

                player.jump_amount -= 1

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
