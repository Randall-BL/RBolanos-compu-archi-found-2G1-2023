import time
import json
from datetime import datetime
class ProcessorMetrics:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.total_cycles = 0
        self.instructions_completed = 0
        self.clock_frequency = 0  # En Hz, ajustar según necesidad
        self.history_file = "processor_history.txt"

    def start_execution(self):
        self.start_time = time.time()

    def end_execution(self):
        self.end_time = time.time()

    def increment_cycle(self):
        self.total_cycles += 1

    def add_completed_instruction(self):
        self.instructions_completed += 1

    def get_metrics(self):
        if self.end_time is None or self.start_time is None:
            execution_time = time.time() - self.start_time if self.start_time else 0
        else:
            execution_time = self.end_time - self.start_time

        # Evitar división por cero
        if execution_time == 0:
            ipc = 0
            cpi = 0
            clock_frequency = 0
        else:
            ipc = self.instructions_completed / self.total_cycles if self.total_cycles > 0 else 0
            cpi = self.total_cycles / self.instructions_completed if self.instructions_completed > 0 else 0
            clock_frequency = self.total_cycles / execution_time

        metrics = {
            "tiempo": f"{execution_time:.2f}s",
            "ciclos": str(self.total_cycles),
            "cpi": f"{cpi:.2f}",
            "ipc": f"{ipc:.2f}",
            "frecuencia": f"{clock_frequency:.2f}Hz"
        }
        self.save_to_history(metrics)
        return metrics
    
    
    def save_to_history(self, metrics):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "timestamp": timestamp,
            "metrics": metrics
        }
        
        try:
            # Leer el historial existente
            existing_history = []
            try:
                with open(self.history_file, 'r') as f:
                    existing_history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_history = []
            
            # Añadir nueva entrada
            existing_history.append(history_entry)
            
            # Mantener solo los últimos 10 registros
            if len(existing_history) > 10:
                existing_history = existing_history[-10:]
            
            # Guardar el historial actualizado
            with open(self.history_file, 'w') as f:
                json.dump(existing_history, f, indent=2)
                
        except Exception as e:
            print(f"Error al guardar el historial: {e}")