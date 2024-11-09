import pygame
import time

# Configuración de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 900, 600
BG_COLOR = (30, 30, 30)  # Fondo gris oscuro
FONT_COLOR = (255, 255, 255)  # Texto blanco
FONT_SIZE = 24

ACTIVE_COLOR = (50, 150, 50)  # Verde para etapas activas
INACTIVE_COLOR = (100, 100, 100)  # Gris para etapas vacías


def initialize_pygame():
    """
    Inicializa Pygame y configura la ventana y fuente.
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simulación del Procesador")
    font = pygame.font.Font(None, FONT_SIZE)
    return screen, font


def draw_header(screen, font, cycle, start_time, program_counter):
    """
    Dibuja el encabezado con ciclo, tiempo transcurrido y PC.
    """
    current_time = time.time() - start_time
    header_texts = [
        f"Ciclo: {cycle}",
        f"Tiempo: {current_time:.2f} segundos",
        f"PC: {program_counter}",
    ]

    y = 10
    for text in header_texts:
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (10, y))
        y += 30


def draw_pipeline(screen, font, pipeline):
    """
    Dibuja el estado del pipeline con colores dinámicos.
    """
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    x_start = 50
    y = 100
    block_width = 120
    block_height = 50
    spacing = 20

    for i, stage in enumerate(stages):
        instruction = pipeline.get(stage, None)
        color = ACTIVE_COLOR if instruction else INACTIVE_COLOR
        pygame.draw.rect(screen, color, (x_start + i * (block_width + spacing), y, block_width, block_height))
        text = f"{stage}: {instruction['opcode'] if instruction else 'Vacío'}"
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (x_start + i * (block_width + spacing) + 10, y + 15))


def draw_registers(screen, font, registers):
    """
    Dibuja el estado de los registros en forma de tabla.
    """
    x_start = 50
    y_start = 200
    spacing_x = 150
    spacing_y = 30

    for i, value in enumerate(registers):
        text = f"R{i}: {value}"
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (x_start + (i % 4) * spacing_x, y_start + (i // 4) * spacing_y))


def draw_memory(screen, font, memory, start=0, end=8):
    """
    Dibuja un segmento de la memoria.
    """
    x_start = 50
    y_start = 350
    spacing_x = 150
    spacing_y = 30

    for i in range(start, min(end, len(memory))):
        text = f"[{i}]: {memory[i]}"
        render = font.render(text, True, FONT_COLOR)
        screen.blit(render, (x_start + (i % 4) * spacing_x, y_start + (i // 4) * spacing_y))


def visualize_with_pygame(program, registers, memory, pipeline, execute_cycle):
    """
    Visualiza el estado del procesador con Pygame.
    """
    screen, font = initialize_pygame()
    clock = pygame.time.Clock()
    program_counter = 0
    cycle = 1
    start_time = time.time()

    running = True
    while running:
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Ejecutar un ciclo cuando se presiona "Espacio"
                program_counter = execute_cycle(program, registers, memory, pipeline, program_counter)
                print(f"\nCiclo {cycle}")
                print(f"Pipeline: {pipeline}")
                print(f"Registros: {registers}")
                cycle += 1

        # Dibujar la interfaz
        screen.fill(BG_COLOR)
        draw_header(screen, font, cycle, start_time, program_counter)
        draw_pipeline(screen, font, pipeline)
        draw_registers(screen, font, registers)
        draw_memory(screen, font, memory)

        # Actualizar la ventana
        pygame.display.flip()
        clock.tick(60)  # Limitar a 60 FPS

    pygame.quit()
