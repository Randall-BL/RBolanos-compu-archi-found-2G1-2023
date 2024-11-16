import pygame
import threading
import time

# Configuración de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 900, 700
BG_COLOR = (30, 30, 30)  # Fondo gris oscuro
FONT_COLOR = (255, 255, 255)  # Texto blanco
FONT_SIZE = 24

ACTIVE_COLOR = (50, 150, 50)  # Verde para etapas activas
INACTIVE_COLOR = (100, 100, 100)  # Gris para etapas vacías

BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Dimensiones del botón
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20

def initialize_pygame():
    """
    Inicializa Pygame y configura la ventana y fuente.
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simulación del Procesador")
    font = pygame.font.Font(None, FONT_SIZE)
    return screen, font

def draw_buttons(screen, font, buttons):
    """
    Dibuja los botones distribuidos en múltiples filas.
    """
    x_start = 20  # Coordenada X inicial de los botones
    y = WINDOW_HEIGHT - 150  # Coordenada Y inicial de los botones (un poco más arriba)
    max_buttons_per_row = 5  # Número máximo de botones por fila (ajústalo según el espacio)
    buttons_in_row = 0  # Contador de botones en la fila actual

    for button in buttons:
        # Crear el rectángulo del botón
        rect = pygame.Rect(x_start, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        button["rect"] = rect

        # Determinar el color según si está en hover
        color = BUTTON_HOVER_COLOR if button.get("hover", False) else BUTTON_COLOR

        # Dibujar el botón
        pygame.draw.rect(screen, color, rect)
        text = font.render(button["label"], True, BUTTON_TEXT_COLOR)
        screen.blit(text, (x_start + 20, y + 15))

        # Ajustar la posición para el próximo botón
        x_start += BUTTON_WIDTH + BUTTON_SPACING
        buttons_in_row += 1

        # Si alcanzamos el máximo por fila, pasar a la siguiente fila
        if buttons_in_row >= max_buttons_per_row:
            x_start = 20  # Reiniciar X para la nueva fila
            y += BUTTON_HEIGHT + 10  # Mover hacia abajo (nueva fila)
            buttons_in_row = 0

def draw_header(screen, font, cycle, start_time, registers):
    """
    Dibuja el encabezado con ciclo, tiempo transcurrido y PC (R8).
    """
    current_time = time.time() - start_time
    header_texts = [
        f"Ciclo: {cycle}",
        f"Tiempo: {current_time:.2f} segundos",
        f"PC (R8): {registers[8]}"  # Obtener el valor del registro R8
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

def draw_interface(screen, font, pipeline, registers, memory, buttons, cycle, start_time):
    """
    Dibuja todos los elementos en la interfaz gráfica.
    """
    # Limpiar la pantalla
    screen.fill(BG_COLOR)

    # Dibujar todos los elementos visuales
    draw_header(screen, font, cycle, start_time, registers)  # Obtener PC desde registers[8]
    draw_pipeline(screen, font, pipeline)
    draw_registers(screen, font, registers)
    draw_memory(screen, font, memory)
    draw_buttons(screen, font, buttons)

def execute_pipeline_in_thread(program, registers, memory, pipeline, program_counter, execute_cycle, screen, font, buttons, cycle, start_time):
    """
    Ejecuta el pipeline en un hilo separado para no bloquear la interfaz gráfica.
    """
    for i in range(6):  # Seis ciclos para que la instrucción pase por todas las etapas
        # Dibujar la interfaz después de cada ciclo
        draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
        pygame.display.flip()

        # Ejecutar un ciclo del pipeline
        program_counter = execute_cycle(program, registers, memory, pipeline, program_counter)

        # Mostrar el estado actualizado después de ejecutar el ciclo
        draw_interface(screen, font, pipeline, registers, memory, buttons, cycle + i, start_time)
        pygame.display.flip()

        # Retrasar para visualizar claramente cada ciclo
        time.sleep(0.5)

def visualize_with_pygame(program, registers, memory, pipeline, execute_cycle, buttons):
    """
    Visualiza el estado del procesador con Pygame y maneja botones.
    """
    screen, font = initialize_pygame()
    clock = pygame.time.Clock()

    program_counter = 0
    cycle = 1
    start_time = time.time()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Verificar si se presionó un botón
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        selected_instruction = button["instruction"]
                        print(f"Ejecutando instrucción: {selected_instruction}")

                        # Crear un hilo para ejecutar el pipeline sin bloquear la UI
                        pipeline_thread = threading.Thread(
                            target=execute_pipeline_in_thread,
                            args=(
                                [selected_instruction], registers, memory, pipeline, program_counter,
                                execute_cycle, screen, font, buttons, cycle, start_time
                            )
                        )
                        pipeline_thread.start()

        # Actualizar el estado de los botones para el efecto de hover
        for button in buttons:
            if "rect" in button:
                button["hover"] = button["rect"].collidepoint(mouse_pos)

        # Dibujar la interfaz completa después de los eventos del ciclo
        draw_interface(screen, font, pipeline, registers, memory, buttons, cycle, start_time)
        pygame.display.flip()  # Refrescar la pantalla
        clock.tick(60)  # Limitar la actualización a 60 FPS

    pygame.quit()
