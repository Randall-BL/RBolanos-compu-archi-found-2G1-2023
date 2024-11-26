import pygame
import json
from datetime import datetime

class MetricsHistory:
    def __init__(self):
        self.history_file = "processor_history.txt"
        self.window_width = 800
        self.window_height = 600
        self.background_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.font_size = 24

    def load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def show_history(self):
        pygame.init()
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Historial de Métricas")
        font = pygame.font.Font(None, self.font_size)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(self.background_color)
            
            history = self.load_history()
            y_pos = 50
            
            # Título
            title = font.render("Historial de Métricas (Últimos 10 registros)", True, self.text_color)
            screen.blit(title, (20, 20))
            
            # Mostrar cada entrada del historial
            for entry in history:
                timestamp = entry["timestamp"]
                metrics = entry["metrics"]
                
                # Mostrar timestamp
                time_text = font.render(f"Fecha: {timestamp}", True, self.text_color)
                screen.blit(time_text, (20, y_pos))
                y_pos += 30
                
                # Mostrar métricas
                for key, value in metrics.items():
                    metric_text = font.render(f"{key}: {value}", True, self.text_color)
                    screen.blit(metric_text, (40, y_pos))
                    y_pos += 25
                
                y_pos += 20  # Espacio entre entradas
            
            pygame.display.flip()
        
        pygame.quit()

# Para usar el historial:
if __name__ == "__main__":
    history_viewer = MetricsHistory()
    history_viewer.show_history()