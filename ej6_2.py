"""
Ejercicio 2 MEJORADO: Simulador Avanzado de Camiones con Carreteras
Autor: [Tu nombre]
Fecha: 17 de Noviembre de 2025

NUEVAS CARACTERÍSTICAS:
- 🛣️ Sistema de carreteras realista con curvas e intersecciones
- ⌨️ Controles de teclado (WASD o flechas) para manejar camiones
- 🚛 Gráficos realistas de camiones con cabina y remolque
- 📦 Mecánica de recogida y entrega de paquetes
- 🏭 Almacenes y puntos de entrega
- 🚦 Sistema de tráfico y colisiones

Controles:
- W/↑: Acelerar
- S/↓: Frenar/Reversa
- A/←: Girar izquierda
- D/→: Girar derecha
- SPACE: Freno de mano/Claxón
- Clic: Seleccionar camión
- R: Recoger/Entregar paquetes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Importar las clases del ejercicio 1
from ej6_1 import Caja, Camion

try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
    print("✓ Pygame cargado correctamente")
except ImportError:
    print("⚠️ Pygame no disponible. Instala con: pip install pygame")
    SOUND_AVAILABLE = False

# Nuevas clases para el sistema mejorado
@dataclass
class Point:
    """Representa un punto en el mapa"""
    x: float
    y: float

@dataclass
class RoadSegment:
    """Representa un segmento de carretera"""
    start: Point
    end: Point
    width: float = 40
    lanes: int = 2

class PackageState(Enum):
    """Estado de un paquete"""
    WAREHOUSE = "warehouse"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"

@dataclass
class Package:
    """Representa un paquete para entregar"""
    id: str
    pickup_point: Point
    delivery_point: Point
    weight: float
    state: PackageState = PackageState.WAREHOUSE
    assigned_truck: Optional[str] = None

@dataclass
class Building:
    """Representa un edificio (almacén o punto de entrega)"""
    position: Point
    size: Tuple[float, float]
    type: str  # "warehouse", "delivery"
    name: str
    color: str

class TruckPhysics:
    """Maneja la física realista de los camiones"""
    
    def __init__(self, position: Point, heading: float = 0):
        self.position = position
        self.heading = heading  # En grados
        self.velocity = 0.0
        self.max_speed = 3.0
        self.acceleration = 0.1
        self.deceleration = 0.15
        self.turn_rate = 2.0  # Grados por frame
        self.friction = 0.95
        
    def update(self, controls: Dict[str, bool]):
        """Actualiza la física basada en los controles"""
        # Acelerar/Frenar
        if controls.get('forward', False):
            self.velocity = min(self.max_speed, self.velocity + self.acceleration)
        elif controls.get('backward', False):
            self.velocity = max(-self.max_speed * 0.5, self.velocity - self.deceleration)
        else:
            # Fricción
            if abs(self.velocity) < 0.01:
                self.velocity = 0
            else:
                self.velocity *= self.friction
        
        # Girar (solo si se está moviendo)
        if abs(self.velocity) > 0.1:
            turn_factor = abs(self.velocity) / self.max_speed
            if controls.get('left', False):
                self.heading -= self.turn_rate * turn_factor
            elif controls.get('right', False):
                self.heading += self.turn_rate * turn_factor
        
        # Mantener heading entre 0-360
        self.heading = self.heading % 360
        
        # Actualizar posición
        if abs(self.velocity) > 0.01:
            angle_rad = math.radians(self.heading - 90)  # -90 para que 0° sea arriba
            self.position.x += self.velocity * math.cos(angle_rad)
            self.position.y += self.velocity * math.sin(angle_rad)

class RoadSystem:
    """Sistema de carreteras mejorado"""
    
    def __init__(self, canvas_width: int, canvas_height: int):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.roads = []
        self.intersections = []
        self.buildings = []
        self.packages = []
        self._create_road_network()
        self._create_buildings()
        self._create_packages()
    
    def _create_road_network(self):
        """Crea una red de carreteras realista"""
        margin = 50
        
        # Carretera principal horizontal
        self.roads.append(RoadSegment(
            Point(margin, self.canvas_height // 2),
            Point(self.canvas_width - margin, self.canvas_height // 2),
            width=50
        ))
        
        # Carretera principal vertical
        self.roads.append(RoadSegment(
            Point(self.canvas_width // 2, margin),
            Point(self.canvas_width // 2, self.canvas_height - margin),
            width=50
        ))
        
        # Carreteras secundarias
        quarter_h = self.canvas_height // 4
        quarter_w = self.canvas_width // 4
        
        # Horizontales secundarias
        self.roads.append(RoadSegment(
            Point(margin, quarter_h),
            Point(self.canvas_width - margin, quarter_h),
            width=35
        ))
        
        self.roads.append(RoadSegment(
            Point(margin, quarter_h * 3),
            Point(self.canvas_width - margin, quarter_h * 3),
            width=35
        ))
        
        # Verticales secundarias
        self.roads.append(RoadSegment(
            Point(quarter_w, margin),
            Point(quarter_w, self.canvas_height - margin),
            width=35
        ))
        
        self.roads.append(RoadSegment(
            Point(quarter_w * 3, margin),
            Point(quarter_w * 3, self.canvas_height - margin),
            width=35
        ))
        
        # Carretera curva (simulada con segmentos)
        center_x, center_y = self.canvas_width * 0.75, self.canvas_height * 0.25
        radius = 60
        for i in range(8):
            angle1 = (i / 8) * math.pi
            angle2 = ((i + 1) / 8) * math.pi
            
            x1 = center_x + radius * math.cos(angle1)
            y1 = center_y + radius * math.sin(angle1)
            x2 = center_x + radius * math.cos(angle2)
            y2 = center_y + radius * math.sin(angle2)
            
            self.roads.append(RoadSegment(
                Point(x1, y1),
                Point(x2, y2),
                width=30
            ))
    
    def _create_buildings(self):
        """Crea almacenes y puntos de entrega"""
        # Almacenes (color azul)
        self.buildings.extend([
            Building(Point(80, 80), (60, 40), "warehouse", "Almacén Central", "#3498db"),
            Building(Point(720, 80), (50, 35), "warehouse", "Almacén Norte", "#3498db"),
            Building(Point(80, 520), (55, 40), "warehouse", "Almacén Sur", "#3498db"),
        ])
        
        # Puntos de entrega (color verde)
        self.buildings.extend([
            Building(Point(720, 520), (40, 30), "delivery", "Tienda 1", "#2ecc71"),
            Building(Point(400, 120), (35, 30), "delivery", "Oficina A", "#2ecc71"),
            Building(Point(600, 450), (40, 35), "delivery", "Tienda 2", "#2ecc71"),
            Building(Point(200, 450), (45, 30), "delivery", "Centro Comercial", "#2ecc71"),
        ])
    
    def _create_packages(self):
        """Crea paquetes para entregar"""
        for i in range(10):
            warehouse = random.choice([b for b in self.buildings if b.type == "warehouse"])
            delivery = random.choice([b for b in self.buildings if b.type == "delivery"])
            
            package = Package(
                id=f"PKG{i+1:03d}",
                pickup_point=warehouse.position,
                delivery_point=delivery.position,
                weight=random.uniform(10, 100)
            )
            self.packages.append(package)
    
    def draw_roads(self, canvas):
        """Dibuja las carreteras en el canvas"""
        canvas.delete("road")
        
        # Fondo verde (césped)
        canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, 
                              fill="#27ae60", tags="road")
        
        # Dibujar carreteras
        for road in self.roads:
            # Asfalto
            canvas.create_line(
                road.start.x, road.start.y,
                road.end.x, road.end.y,
                width=road.width, fill="#34495e", tags="road",
                capstyle=tk.ROUND, joinstyle=tk.ROUND
            )
            
            # Líneas centrales (discontinuas)
            if road.width > 35:
                segments = 10
                for i in range(segments):
                    if i % 2 == 0:  # Línea discontinua
                        start_ratio = i / segments
                        end_ratio = (i + 0.5) / segments
                        
                        line_start_x = road.start.x + (road.end.x - road.start.x) * start_ratio
                        line_start_y = road.start.y + (road.end.y - road.start.y) * start_ratio
                        line_end_x = road.start.x + (road.end.x - road.start.x) * end_ratio
                        line_end_y = road.start.y + (road.end.y - road.start.y) * end_ratio
                        
                        canvas.create_line(
                            line_start_x, line_start_y,
                            line_end_x, line_end_y,
                            width=3, fill="#f1c40f", tags="road"
                        )
        
        # Dibujar edificios
        for building in self.buildings:
            x, y = building.position.x, building.position.y
            w, h = building.size
            
            # Edificio
            canvas.create_rectangle(
                x - w//2, y - h//2,
                x + w//2, y + h//2,
                fill=building.color, outline="#2c3e50", width=2, tags="road"
            )
            
            # Icono según tipo
            icon = "🏭" if building.type == "warehouse" else "🏪"
            canvas.create_text(x, y - 5, text=icon, font=('Arial', 16), tags="road")
            
            # Nombre
            canvas.create_text(x, y + h//2 + 15, text=building.name, 
                             font=('Arial', 8), fill="#2c3e50", tags="road")

class AdvancedTruckSimulator:
    """Simulador avanzado de camiones con carreteras y física realista"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚛 Simulador Avanzado de Camiones - Con Carreteras")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Variables del simulador
        self.camiones: List[Camion] = []
        self.truck_physics: Dict[str, TruckPhysics] = {}
        self.camion_activo: Optional[Camion] = None
        self.running = False
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Sistema de carreteras
        self.road_system = RoadSystem(self.canvas_width, self.canvas_height)
        
        # Controles de teclado
        self.keys_pressed = set()
        self.controls = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'brake': False
        }
        
        # Crear interfaz
        self.create_widgets()
        self.create_sample_trucks()
        self.setup_keyboard_controls()
        
        # Cargar sonidos
        self.load_sounds()
        
        # Iniciar simulación
        self.start_simulation()
    
    def create_widgets(self):
        """Crea la interfaz mejorada"""
        # Configurar grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - Controles
        left_panel = ttk.Frame(self.root, width=300)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_panel.grid_propagate(False)
        
        # Panel central - Mapa
        center_frame = ttk.LabelFrame(self.root, text="🗺️ Mapa de Carreteras", padding=10)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Canvas principal
        self.canvas = tk.Canvas(center_frame, width=self.canvas_width, height=self.canvas_height, 
                               bg='#27ae60', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack()
        self.canvas.focus_set()  # Para recibir eventos de teclado
        
        # Panel derecho - Información
        right_panel = ttk.Frame(self.root, width=250)
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(0, 10), pady=10)
        right_panel.grid_propagate(False)
        
        # === PANEL IZQUIERDO ===
        self.create_left_panel(left_panel)
        
        # === PANEL DERECHO ===
        self.create_right_panel(right_panel)
        
        # Eventos del canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
    
    def create_left_panel(self, parent):
        """Crea el panel izquierdo con controles"""
        # Instrucciones de control
        controls_frame = ttk.LabelFrame(parent, text="🎮 Controles", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        controls_text = """⌨️ CONTROLES DE TECLADO:
• W/↑ : Acelerar
• S/↓ : Frenar/Reversa  
• A/← : Girar izquierda
• D/→ : Girar derecha
• SPACE : Claxón/Freno
• R : Recoger/Entregar

🖱️ CONTROLES DE RATÓN:
• Clic izq: Seleccionar camión
• Clic der: Información"""
        
        ttk.Label(controls_frame, text=controls_text.strip(), 
                 font=('Consolas', 9), justify=tk.LEFT).pack()
        
        # Estado del camión activo
        status_frame = ttk.LabelFrame(parent, text="📊 Estado del Camión", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.speed_label = ttk.Label(status_frame, text="Velocidad: 0 km/h", font=('Arial', 10))
        self.speed_label.pack(anchor=tk.W)
        
        self.heading_label = ttk.Label(status_frame, text="Rumbo: 0°", font=('Arial', 10))
        self.heading_label.pack(anchor=tk.W)
        
        self.position_label = ttk.Label(status_frame, text="Posición: (0, 0)", font=('Arial', 10))
        self.position_label.pack(anchor=tk.W)
        
        self.cargo_label = ttk.Label(status_frame, text="Carga: 0 kg", font=('Arial', 10))
        self.cargo_label.pack(anchor=tk.W)
        
        # Botones de acción
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="🚛 Nuevo Camión", 
                  command=self.create_new_truck).pack(fill=tk.X, pady=2)
        
        ttk.Button(action_frame, text="📦 Nueva Misión", 
                  command=self.create_new_mission).pack(fill=tk.X, pady=2)
        
        ttk.Button(action_frame, text="🔊 Claxón", 
                  command=self.play_claxon).pack(fill=tk.X, pady=2)
    
    def create_right_panel(self, parent):
        """Crea el panel derecho con información detallada"""
        # Información del camión
        truck_info_frame = ttk.LabelFrame(parent, text="🚛 Info del Camión", padding=10)
        truck_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.truck_info_text = tk.Text(truck_info_frame, height=8, width=30, 
                                     font=('Consolas', 9), wrap=tk.WORD, state=tk.DISABLED)
        self.truck_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Lista de camiones
        trucks_frame = ttk.LabelFrame(parent, text="🚚 Flota de Camiones", padding=10)
        trucks_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.trucks_listbox = tk.Listbox(trucks_frame, height=4, font=('Arial', 9))
        self.trucks_listbox.pack(fill=tk.X)
        self.trucks_listbox.bind("<<ListboxSelect>>", self.on_truck_select)
        
        # Misiones de entrega
        missions_frame = ttk.LabelFrame(parent, text="📦 Misiones Activas", padding=10)
        missions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.missions_listbox = tk.Listbox(missions_frame, height=6, font=('Consolas', 8))
        self.missions_listbox.pack(fill=tk.BOTH, expand=True)
    
    def setup_keyboard_controls(self):
        """Configura los controles de teclado"""
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
    
    def on_key_press(self, event):
        """Maneja las teclas presionadas"""
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        
        # Actualizar controles
        self.controls['forward'] = 'w' in self.keys_pressed or 'up' in self.keys_pressed
        self.controls['backward'] = 's' in self.keys_pressed or 'down' in self.keys_pressed
        self.controls['left'] = 'a' in self.keys_pressed or 'left' in self.keys_pressed
        self.controls['right'] = 'd' in self.keys_pressed or 'right' in self.keys_pressed
        self.controls['brake'] = 'space' in self.keys_pressed
        
        # Acciones especiales
        if key == 'r':
            self.handle_pickup_delivery()
        elif key == 'space':
            self.play_claxon()
    
    def on_key_release(self, event):
        """Maneja las teclas liberadas"""
        key = event.keysym.lower()
        self.keys_pressed.discard(key)
        
        # Actualizar controles
        self.controls['forward'] = 'w' in self.keys_pressed or 'up' in self.keys_pressed
        self.controls['backward'] = 's' in self.keys_pressed or 'down' in self.keys_pressed
        self.controls['left'] = 'a' in self.keys_pressed or 'left' in self.keys_pressed
        self.controls['right'] = 'd' in self.keys_pressed or 'right' in self.keys_pressed
        self.controls['brake'] = 'space' in self.keys_pressed
    
    def create_sample_trucks(self):
        """Crea camiones de ejemplo"""
        # Camión 1
        camion1 = Camion("TRK001", "Carlos Rodríguez", 8000.0, "Reparto urbano", 90, 0)
        physics1 = TruckPhysics(Point(400, 300), 0)
        self.truck_physics[camion1.matricula] = physics1
        
        # Camión 2  
        camion2 = Camion("TRK002", "Ana López", 6000.0, "Entregas rápidas", 180, 0)
        physics2 = TruckPhysics(Point(200, 150), 90)
        self.truck_physics[camion2.matricula] = physics2
        
        self.camiones = [camion1, camion2]
        self.camion_activo = camion1
        
        self.update_truck_list()
        self.update_missions_list()
    
    def draw_truck(self, canvas, camion: Camion):
        """Dibuja un camión realista"""
        if camion.matricula not in self.truck_physics:
            return
            
        physics = self.truck_physics[camion.matricula]
        x, y = physics.position.x, physics.position.y
        heading = physics.heading
        
        # Color según si está activo
        if camion == self.camion_activo:
            cab_color = "#e74c3c"
            trailer_color = "#c0392b"
        else:
            cab_color = "#3498db"
            trailer_color = "#2980b9"
        
        # Calcular puntos del camión rotado
        angle_rad = math.radians(heading - 90)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        
        # Dimensiones del camión
        cab_length, cab_width = 25, 12
        trailer_length, trailer_width = 35, 15
        
        # Cabina (parte delantera)
        cab_points = self._rotate_rectangle(x, y, cab_length, cab_width, cos_a, sin_a, offset_x=15)
        canvas.create_polygon(cab_points, fill=cab_color, outline="#2c3e50", width=2, tags="truck")
        
        # Remolque (parte trasera)
        trailer_points = self._rotate_rectangle(x, y, trailer_length, trailer_width, cos_a, sin_a, offset_x=-20)
        canvas.create_polygon(trailer_points, fill=trailer_color, outline="#2c3e50", width=2, tags="truck")
        
        # Ruedas
        wheel_positions = [
            (10, 8), (10, -8),    # Ruedas delanteras
            (-15, 10), (-15, -10), # Ruedas traseras delanteras  
            (-30, 10), (-30, -10)  # Ruedas traseras traseras
        ]
        
        for wheel_x, wheel_y in wheel_positions:
            # Rotar posición de la rueda
            rot_x = x + wheel_x * cos_a - wheel_y * sin_a
            rot_y = y + wheel_x * sin_a + wheel_y * cos_a
            
            canvas.create_oval(rot_x - 3, rot_y - 3, rot_x + 3, rot_y + 3,
                             fill="#2c3e50", outline="#34495e", tags="truck")
        
        # Dirección (flecha en la cabina)
        arrow_x = x + 20 * cos_a
        arrow_y = y + 20 * sin_a
        canvas.create_line(x, y, arrow_x, arrow_y,
                         fill="#f1c40f", width=3, arrow=tk.LAST,
                         arrowshape=(10, 15, 5), tags="truck")
        
        # Etiqueta
        canvas.create_text(x, y - 30, text=camion.matricula, 
                         fill="#2c3e50", font=('Arial', 10, 'bold'), tags="truck")
        
        # Velocidad
        speed_kmh = abs(physics.velocity) * 20  # Conversión a km/h visual
        canvas.create_text(x, y + 35, text=f"{speed_kmh:.0f} km/h", 
                         fill="#7f8c8d", font=('Arial', 8), tags="truck")
        
        # Indicador de carga
        peso_actual = camion.peso_total()
        if peso_actual > 0:
            canvas.create_text(x + 25, y - 10, text=f"{peso_actual:.0f}kg", 
                             fill="#e67e22", font=('Arial', 8, 'bold'), tags="truck")
    
    def _rotate_rectangle(self, cx, cy, length, width, cos_a, sin_a, offset_x=0, offset_y=0):
        """Rota un rectángulo alrededor de un punto central"""
        # Puntos del rectángulo sin rotar (relativo al centro)
        half_l, half_w = length/2, width/2
        points = [
            (-half_l + offset_x, -half_w + offset_y),
            (half_l + offset_x, -half_w + offset_y),
            (half_l + offset_x, half_w + offset_y),
            (-half_l + offset_x, half_w + offset_y)
        ]
        
        # Rotar y trasladar
        rotated_points = []
        for px, py in points:
            rx = cx + px * cos_a - py * sin_a
            ry = cy + px * sin_a + py * cos_a
            rotated_points.extend([rx, ry])
        
        return rotated_points
    
    def update_physics(self):
        """Actualiza la física de todos los camiones"""
        for camion in self.camiones:
            if camion.matricula in self.truck_physics:
                physics = self.truck_physics[camion.matricula]
                
                # Aplicar controles solo al camión activo
                if camion == self.camion_activo:
                    physics.update(self.controls)
                    
                    # Mantener en carreteras (opcional)
                    self._keep_on_road(physics)
                    
                    # Actualizar velocidad del camión (para compatibilidad)
                    camion.velocidad = int(abs(physics.velocity) * 20)  # Conversión visual
                    camion.rumbo = int(physics.heading)
    
    def _keep_on_road(self, physics: TruckPhysics):
        """Mantiene el camión cerca de las carreteras"""
        current_pos = physics.position
        
        # Verificar límites del canvas
        margin = 30
        if current_pos.x < margin:
            current_pos.x = margin
            physics.velocity *= -0.5
        elif current_pos.x > self.canvas_width - margin:
            current_pos.x = self.canvas_width - margin  
            physics.velocity *= -0.5
            
        if current_pos.y < margin:
            current_pos.y = margin
            physics.velocity *= -0.5
        elif current_pos.y > self.canvas_height - margin:
            current_pos.y = self.canvas_height - margin
            physics.velocity *= -0.5
    
    def draw_packages(self, canvas):
        """Dibuja los paquetes en el mapa"""
        for package in self.road_system.packages:
            if package.state == PackageState.WAREHOUSE:
                # Paquete en almacén
                x, y = package.pickup_point.x, package.pickup_point.y
                canvas.create_rectangle(x-8, y-8, x+8, y+8, 
                                      fill="#f39c12", outline="#e67e22", width=2, tags="package")
                canvas.create_text(x, y, text="📦", font=('Arial', 12), tags="package")
            elif package.state == PackageState.DELIVERED:
                # Paquete entregado
                x, y = package.delivery_point.x, package.delivery_point.y
                canvas.create_oval(x-6, y-6, x+6, y+6, 
                                 fill="#2ecc71", outline="#27ae60", width=2, tags="package")
                canvas.create_text(x, y, text="✓", font=('Arial', 10, 'bold'), 
                                  fill="white", tags="package")
    
    def handle_pickup_delivery(self):
        """Maneja la recogida y entrega de paquetes"""
        if not self.camion_activo or self.camion_activo.matricula not in self.truck_physics:
            return
            
        physics = self.truck_physics[self.camion_activo.matricula]
        truck_pos = physics.position
        
        # Buscar paquetes cercanos para recoger
        for package in self.road_system.packages:
            if package.state == PackageState.WAREHOUSE:
                distance = math.sqrt((truck_pos.x - package.pickup_point.x)**2 + 
                                   (truck_pos.y - package.pickup_point.y)**2)
                
                if distance < 50:  # Radio de recogida
                    # Crear caja correspondiente
                    nueva_caja = Caja(
                        package.id,
                        package.weight,
                        f"Entrega para {package.delivery_point.x:.0f},{package.delivery_point.y:.0f}",
                        50, 40, 30
                    )
                    
                    # Intentar añadir al camión
                    peso_antes = self.camion_activo.peso_total()
                    self.camion_activo.add_caja(nueva_caja)
                    peso_despues = self.camion_activo.peso_total()
                    
                    if peso_despues > peso_antes:
                        package.state = PackageState.IN_TRANSIT
                        package.assigned_truck = self.camion_activo.matricula
                        self.play_pickup_sound()
                        print(f"📦 Paquete {package.id} recogido por {self.camion_activo.matricula}")
                        self.update_missions_list()
                        return
        
        # Buscar paquetes para entregar
        for package in self.road_system.packages:
            if (package.state == PackageState.IN_TRANSIT and 
                package.assigned_truck == self.camion_activo.matricula):
                
                distance = math.sqrt((truck_pos.x - package.delivery_point.x)**2 + 
                                   (truck_pos.y - package.delivery_point.y)**2)
                
                if distance < 50:  # Radio de entrega
                    # Buscar y remover la caja del camión
                    for caja in self.camion_activo.cajas:
                        if caja.codigo == package.id:
                            self.camion_activo.cajas.remove(caja)
                            package.state = PackageState.DELIVERED
                            self.play_delivery_sound()
                            print(f"📦 Paquete {package.id} entregado por {self.camion_activo.matricula}")
                            self.update_missions_list()
                            return
    
    def update_status_labels(self):
        """Actualiza las etiquetas de estado"""
        if self.camion_activo and self.camion_activo.matricula in self.truck_physics:
            physics = self.truck_physics[self.camion_activo.matricula]
            speed_kmh = abs(physics.velocity) * 20
            
            self.speed_label.config(text=f"Velocidad: {speed_kmh:.0f} km/h")
            self.heading_label.config(text=f"Rumbo: {physics.heading:.0f}°")
            self.position_label.config(text=f"Posición: ({physics.position.x:.0f}, {physics.position.y:.0f})")
            self.cargo_label.config(text=f"Carga: {self.camion_activo.peso_total():.0f} kg")
    
    def update_truck_list(self):
        """Actualiza la lista de camiones"""
        self.trucks_listbox.delete(0, tk.END)
        for i, camion in enumerate(self.camiones):
            peso = camion.peso_total()
            status = "🟢" if camion == self.camion_activo else "⚪"
            info = f"{status} {camion.matricula} - {peso:.0f}kg"
            self.trucks_listbox.insert(tk.END, info)
            if camion == self.camion_activo:
                self.trucks_listbox.selection_set(i)
    
    def update_missions_list(self):
        """Actualiza la lista de misiones"""
        self.missions_listbox.delete(0, tk.END)
        
        if self.camion_activo:
            # Mostrar paquetes en el camión
            for caja in self.camion_activo.cajas:
                # Buscar el paquete correspondiente
                package = next((p for p in self.road_system.packages 
                              if p.id == caja.codigo and p.state == PackageState.IN_TRANSIT), None)
                if package:
                    info = f"🚛 {package.id} → Entregar en ({package.delivery_point.x:.0f}, {package.delivery_point.y:.0f})"
                    self.missions_listbox.insert(tk.END, info)
            
            # Mostrar paquetes disponibles cercanos
            if self.camion_activo.matricula in self.truck_physics:
                truck_pos = self.truck_physics[self.camion_activo.matricula].position
                
                nearby_packages = []
                for package in self.road_system.packages:
                    if package.state == PackageState.WAREHOUSE:
                        distance = math.sqrt((truck_pos.x - package.pickup_point.x)**2 + 
                                           (truck_pos.y - package.pickup_point.y)**2)
                        if distance < 100:
                            nearby_packages.append((package, distance))
                
                nearby_packages.sort(key=lambda x: x[1])  # Ordenar por distancia
                
                for package, distance in nearby_packages[:3]:  # Mostrar solo los 3 más cercanos
                    info = f"📦 {package.id} - {distance:.0f}m (Recoger)"
                    self.missions_listbox.insert(tk.END, info)
    
    def update_truck_info(self):
        """Actualiza la información detallada del camión"""
        self.truck_info_text.config(state=tk.NORMAL)
        self.truck_info_text.delete('1.0', tk.END)
        
        if self.camion_activo:
            physics = self.truck_physics.get(self.camion_activo.matricula)
            peso_total = self.camion_activo.peso_total()
            porcentaje = (peso_total / self.camion_activo.capacidad_kg) * 100
            
            info = f"🚛 {self.camion_activo.matricula}\n"
            info += f"👤 {self.camion_activo.conductor}\n"
            info += f"📦 {self.camion_activo.descripcion_carga}\n\n"
            
            if physics:
                speed_kmh = abs(physics.velocity) * 20
                info += f"⚡ {speed_kmh:.1f} km/h\n"
                info += f"🧭 {physics.heading:.0f}°\n"
                info += f"📍 ({physics.position.x:.0f}, {physics.position.y:.0f})\n\n"
            
            info += f"⚖️ {peso_total:.1f}/{self.camion_activo.capacidad_kg} kg ({porcentaje:.1f}%)\n"
            info += f"📦 {len(self.camion_activo.cajas)} cajas\n\n"
            
            if self.camion_activo.cajas:
                info += "CAJAS CARGADAS:\n"
                for i, caja in enumerate(self.camion_activo.cajas, 1):
                    info += f"{i}. {caja.codigo}: {caja.peso_kg}kg\n"
            
            self.truck_info_text.insert(tk.END, info)
        else:
            self.truck_info_text.insert(tk.END, "No hay camión seleccionado")
        
        self.truck_info_text.config(state=tk.DISABLED)
    
    def simulation_loop(self):
        """Bucle principal de la simulación mejorada"""
        if self.running:
            # Actualizar física
            self.update_physics()
            
            # Dibujar todo
            self.canvas.delete("truck")
            self.canvas.delete("package")
            
            # Dibujar carreteras (solo si es necesario)
            self.road_system.draw_roads(self.canvas)
            
            # Dibujar paquetes
            self.draw_packages(self.canvas)
            
            # Dibujar camiones
            for camion in self.camiones:
                self.draw_truck(self.canvas, camion)
            
            # Actualizar interfaz
            self.update_status_labels()
            self.update_truck_info()
            self.update_missions_list()
            
            # Continuar simulación
            self.root.after(50, self.simulation_loop)  # 20 FPS
    
    def on_canvas_click(self, event):
        """Maneja clics en el canvas para seleccionar camiones"""
        x, y = event.x, event.y
        
        # Buscar el camión más cercano
        closest_truck = None
        min_distance = float('inf')
        
        for camion in self.camiones:
            if camion.matricula not in self.truck_physics:
                continue
            
            physics = self.truck_physics[camion.matricula]
            truck_x, truck_y = physics.position.x, physics.position.y
            distance = math.sqrt((x - truck_x)**2 + (y - truck_y)**2)
            
            if distance < 40 and distance < min_distance:  # Radio de selección
                closest_truck = camion
                min_distance = distance
        
        if closest_truck:
            self.camion_activo = closest_truck
            self.update_truck_list()
            self.canvas.focus_set()  # Para mantener el foco del teclado
            print(f"✓ Camión {closest_truck.matricula} seleccionado")
    
    def on_right_click(self, event):
        """Maneja clic derecho para mostrar información"""
        if self.camion_activo:
            self.show_truck_details()
    
    def show_truck_details(self):
        """Muestra detalles completos del camión activo"""
        if not self.camion_activo:
            return
            
        details = str(self.camion_activo)
        messagebox.showinfo(f"Detalles - {self.camion_activo.matricula}", details)
    
    def on_truck_select(self, event):
        """Maneja selección de camión en la lista"""
        selection = self.trucks_listbox.curselection()
        if selection and len(selection) > 0:
            index = selection[0]
            if 0 <= index < len(self.camiones):
                self.camion_activo = self.camiones[index]
                self.canvas.focus_set()  # Mantener foco para teclado
    
    def load_sounds(self):
        """Carga los archivos de audio"""
        if SOUND_AVAILABLE:
            try:
                self.create_sounds()
            except Exception as e:
                print(f"⚠️ Error cargando sonidos: {e}")
                self.claxon_sound = None
                self.pickup_sound = None
                self.delivery_sound = None
        else:
            self.claxon_sound = None
            self.pickup_sound = None
            self.delivery_sound = None
    
    def create_sounds(self):
        """Crea varios efectos de sonido"""
        if not SOUND_AVAILABLE:
            return
            
        sample_rate = 22050
        
        # Sonido de claxón
        duration = 0.5
        frequency = 800
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 4096 * math.sin(frequency * 2 * math.pi * i / sample_rate)
            arr.append([int(wave), int(wave)])
        sound_array = pygame.sndarray.array(arr)
        self.claxon_sound = pygame.sndarray.make_sound(sound_array)
        
        # Sonido de recogida (pitch alto)
        duration = 0.3
        frequency = 1200
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 2048 * math.sin(frequency * 2 * math.pi * i / sample_rate)
            arr.append([int(wave), int(wave)])
        sound_array = pygame.sndarray.array(arr)
        self.pickup_sound = pygame.sndarray.make_sound(sound_array)
        
        # Sonido de entrega (doble beep)
        duration = 0.6
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            # Crear un patrón de doble beep
            time_pos = i / sample_rate
            if time_pos < 0.2 or (0.3 < time_pos < 0.5):
                wave = 2048 * math.sin(1000 * 2 * math.pi * time_pos)
            else:
                wave = 0
            arr.append([int(wave), int(wave)])
        sound_array = pygame.sndarray.array(arr)
        self.delivery_sound = pygame.sndarray.make_sound(sound_array)
    
    def play_claxon(self):
        """Reproduce el sonido del claxón"""
        if self.camion_activo:
            self.camion_activo.claxon()
            
            if self.claxon_sound and SOUND_AVAILABLE:
                try:
                    self.claxon_sound.play()
                except Exception as e:
                    print(f"⚠️ Error reproduciendo claxón: {e}")
    
    def play_pickup_sound(self):
        """Reproduce sonido de recogida"""
        if self.pickup_sound and SOUND_AVAILABLE:
            try:
                self.pickup_sound.play()
            except Exception as e:
                print(f"⚠️ Error reproduciendo pickup: {e}")
    
    def play_delivery_sound(self):
        """Reproduce sonido de entrega"""
        if self.delivery_sound and SOUND_AVAILABLE:
            try:
                self.delivery_sound.play()
            except Exception as e:
                print(f"⚠️ Error reproduciendo delivery: {e}")
    
    def create_new_truck(self):
        """Crea un nuevo camión"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🚛 Nuevo Camión")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Variables
        matricula_var = tk.StringVar()
        conductor_var = tk.StringVar()
        capacidad_var = tk.DoubleVar(value=6000.0)
        descripcion_var = tk.StringVar(value="Reparto general")
        
        # Formulario
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Matrícula:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=matricula_var, width=20).grid(row=0, column=1, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(frame, text="Conductor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=conductor_var, width=20).grid(row=1, column=1, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(frame, text="Capacidad (kg):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=capacidad_var, width=20).grid(row=2, column=1, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(frame, text="Descripción:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=descripcion_var, width=20).grid(row=3, column=1, pady=5, sticky=tk.W+tk.E)
        
        frame.columnconfigure(1, weight=1)
        
        def crear_camion():
            try:
                matricula = matricula_var.get().strip()
                conductor = conductor_var.get().strip()
                
                if not matricula or not conductor:
                    messagebox.showerror("Error", "Matrícula y conductor son obligatorios")
                    return
                
                # Verificar que la matrícula no exista
                if any(c.matricula == matricula for c in self.camiones):
                    messagebox.showerror("Error", "Ya existe un camión con esa matrícula")
                    return
                
                # Crear camión
                nuevo_camion = Camion(
                    matricula, conductor, capacidad_var.get(),
                    descripcion_var.get(), 90, 0
                )
                
                # Crear física
                pos_x = random.randint(100, self.canvas_width - 100)
                pos_y = random.randint(100, self.canvas_height - 100)
                nueva_fisica = TruckPhysics(Point(pos_x, pos_y), random.randint(0, 359))
                
                self.truck_physics[matricula] = nueva_fisica
                self.camiones.append(nuevo_camion)
                self.camion_activo = nuevo_camion
                
                self.update_truck_list()
                
                messagebox.showinfo("Éxito", f"Camión {matricula} creado correctamente")
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Error en los datos: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="✅ Crear Camión", command=crear_camion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_new_mission(self):
        """Crea una nueva misión de entrega"""
        # Seleccionar puntos aleatoriamente
        warehouse = random.choice([b for b in self.road_system.buildings if b.type == "warehouse"])
        delivery = random.choice([b for b in self.road_system.buildings if b.type == "delivery"])
        
        package_id = f"PKG{len(self.road_system.packages)+1:03d}"
        new_package = Package(
            id=package_id,
            pickup_point=warehouse.position,
            delivery_point=delivery.position,
            weight=random.uniform(20, 150)
        )
        
        self.road_system.packages.append(new_package)
        
        messagebox.showinfo("Nueva Misión", 
                           f"Misión {package_id} creada:\n"
                           f"Recoger en {warehouse.name}\n"
                           f"Entregar en {delivery.name}\n"
                           f"Peso: {new_package.weight:.1f} kg")
    
    def start_simulation(self):
        """Inicia la simulación"""
        self.running = True
        # Dibujar carreteras inicialmente
        self.road_system.draw_roads(self.canvas)
        self.simulation_loop()
    
    def run(self):
        """Ejecuta la aplicación"""
        print("🚛 Iniciando simulador avanzado de camiones...")
        print("✓ Interfaz gráfica cargada")
        print("⌨️ Usa WASD o flechas para manejar")
        print("📦 Presiona R cerca de paquetes para recoger/entregar")
        self.root.mainloop()
        self.running = False


def main():
    """Función principal"""
    try:
        app = AdvancedTruckSimulator()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        messagebox.showerror("Error Fatal", f"No se pudo iniciar la aplicación:\n{e}")


if __name__ == "__main__":
    main()