# -*- coding: utf-8 -*-
"""
TRUCK TYCOON SIMULATOR - Juego Avanzado de GestiÃ³n de Camiones
VersiÃ³n Completa y Funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import time
import json
import os
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

# Importar las clases del ejercicio 1
try:
    from ej6_1 import Caja, Camion
except ImportError:
    print("Advertencia: No se pudo importar ej6_1.py, creando clases bÃ¡sicas...")
    
    class Caja:
        def __init__(self, peso: float, largo: float, alto: float, ancho: float, fragilidad: str):
            self.peso = peso
            self.largo = largo
            self.alto = alto
            self.ancho = ancho
            self.fragilidad = fragilidad
    
    class Camion:
        def __init__(self):
            self.cajas = []
            self.velocidad = 0
            self.rumbo = 0
            
        def peso_total(self):
            return sum(caja.peso for caja in self.cajas)
            
        def add_caja(self, caja):
            self.cajas.append(caja)
            
        def setVelocidad(self, vel):
            self.velocidad = vel
            
        def setRumbo(self, rumbo):
            self.rumbo = rumbo
            
        def claxon(self):
            print("Â¡BEEP BEEP!")

try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

# ========== ENUMS ==========

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    ACHIEVEMENTS = "achievements"

class MissionType(Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    EXPRESS = "express"
    FRAGILE = "fragile"
    BULK = "bulk"

class TruckType(Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SUPER_HEAVY = "super_heavy"

# ========== DATACLASSES ==========

@dataclass
class GameStats:
    money: float = 1000.0
    experience: int = 0
    level: int = 1
    missions_completed: int = 0
    total_distance: float = 0.0
    total_cargo: float = 0.0
    fuel_consumed: float = 0.0
    playtime: float = 0.0

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    reward: int
    unlocked: bool = False
    progress: int = 0
    target: int = 1

@dataclass
class Mission:
    id: str
    type: MissionType
    cargo_type: str
    weight: float
    distance: float
    reward: int
    time_limit: int
    pickup_location: Tuple[float, float]
    delivery_location: Tuple[float, float]
    difficulty: int
    is_active: bool = False
    start_time: Optional[float] = None

@dataclass
class Point:
    x: float
    y: float

@dataclass
class TruckSpec:
    name: str
    max_speed: float
    capacity: float
    fuel_efficiency: float
    price: int
    maintenance_cost: int

# ========== CONSTANTS ==========

TRUCK_SPECS = {
    TruckType.LIGHT: TruckSpec("CamiÃ³n Ligero", 4.0, 3000, 8.0, 15000, 50),
    TruckType.MEDIUM: TruckSpec("CamiÃ³n Mediano", 3.5, 6000, 6.0, 30000, 80),
    TruckType.HEAVY: TruckSpec("CamiÃ³n Pesado", 3.0, 12000, 4.0, 60000, 120),
    TruckType.SUPER_HEAVY: TruckSpec("Super Pesado", 2.5, 20000, 3.0, 100000, 200),
}

# ========== GAME CLASSES ==========

class ProceduralMap:
    def __init__(self, width: int, height: int, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(1, 1000000)
        random.seed(self.seed)
        
        self.roads = []
        self.buildings = []
        self.traffic_lights = []
        
        self._generate_map()
    
    def _generate_map(self):
        grid_spacing = 200
        road_width = 60
        
        # Carreteras horizontales principales
        for y in range(grid_spacing, self.height, grid_spacing):
            self.roads.append({
                'start': Point(0, y),
                'end': Point(self.width, y),
                'width': road_width,
                'type': 'main'
            })
        
        # Carreteras verticales principales  
        for x in range(grid_spacing, self.width, grid_spacing):
            self.roads.append({
                'start': Point(x, 0),
                'end': Point(x, self.height),
                'width': road_width,
                'type': 'main'
            })
        
        self._generate_buildings()
        self._generate_intersections()
    
    def _generate_buildings(self):
        building_types = [
            {'type': 'warehouse', 'name': 'Almacen', 'color': '#3498db'},
            {'type': 'factory', 'name': 'Fabrica', 'color': '#e67e22'},
            {'type': 'store', 'name': 'Tienda', 'color': '#2ecc71'},
            {'type': 'mall', 'name': 'Centro', 'color': '#9b59b6'},
            {'type': 'office', 'name': 'Oficina', 'color': '#34495e'},
        ]
        
        num_buildings = (self.width * self.height) // 50000
        
        for _ in range(num_buildings):
            building_type = random.choice(building_types)
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            
            # Verificar distancia mÃ­nima
            valid_position = True
            for building in self.buildings:
                distance = math.sqrt((x - building['position'].x)**2 + (y - building['position'].y)**2)
                if distance < 200:
                    valid_position = False
                    break
            
            if valid_position:
                size = (random.randint(60, 120), random.randint(40, 80))
                self.buildings.append({
                    'position': Point(x, y),
                    'size': size,
                    'type': building_type['type'],
                    'name': f"{building_type['name']} {len([b for b in self.buildings if b['type'] == building_type['type']]) + 1}",
                    'color': building_type['color']
                })
    
    def _generate_intersections(self):
        grid_spacing = 200
        for x in range(grid_spacing, self.width, grid_spacing):
            for y in range(grid_spacing, self.height, grid_spacing):
                if random.random() < 0.7:
                    self.traffic_lights.append({
                        'position': Point(x, y),
                        'state': random.choice(['red', 'yellow', 'green']),
                        'timer': random.randint(30, 120)
                    })

class EnhancedTruckPhysics:
    def __init__(self, position: Point, truck_type: TruckType, heading: float = 0):
        self.position = position
        self.heading = heading
        self.velocity = 0.0
        self.truck_type = truck_type
        
        spec = TRUCK_SPECS[truck_type]
        self.max_speed = spec.max_speed
        self.fuel_tank = 100.0
        self.fuel_level = 100.0
        self.fuel_efficiency = spec.fuel_efficiency
        
        self.acceleration = 0.15  # Más rápido para acelerar
        self.deceleration = 0.18  # Más rápido para frenar
        self.turn_rate = 2.2      # Más ágil al girar
        self.friction = 0.94      # Menos fricción para mejor deslizamiento
        
        self.odometer = 0.0
        self.engine_hours = 0.0
        self.maintenance_needed = False
        
    def update(self, controls: Dict[str, bool], dt: float = 1.0/60.0):
        if self.fuel_level <= 0:
            self.velocity *= 0.95
            return
        
        # Frame multiplier para consistencia
        frame_time = min(dt, 1.0/30.0)  # Cap a 30 FPS mínimo
        
        # Acelerar/Frenar con delta time
        if controls.get('forward', False) and self.fuel_level > 0:
            self.velocity = min(self.max_speed, self.velocity + self.acceleration * frame_time * 60)
        elif controls.get('backward', False):
            self.velocity = max(-self.max_speed * 0.5, self.velocity - self.deceleration * frame_time * 60)
        else:
            if abs(self.velocity) < 0.01:
                self.velocity = 0
            else:
                # Aplicar fricción basada en tiempo
                friction_rate = 1 - self.friction
                self.velocity *= friction_rate ** (frame_time * 60)
        
        # Girar con mejor responsividad
        if abs(self.velocity) > 0.1:
            turn_factor = min(1.0, abs(self.velocity) / self.max_speed * 2)  # Más responsivo
            turn_amount = self.turn_rate * turn_factor * frame_time * 60
            if controls.get('left', False):
                self.heading -= turn_amount
            elif controls.get('right', False):
                self.heading += turn_amount
        
        self.heading = self.heading % 360
        
        # Actualizar posiciÃ³n
        if abs(self.velocity) > 0.01:
            angle_rad = math.radians(self.heading - 90)
            distance = abs(self.velocity) * dt * 60
            
            self.position.x += distance * math.cos(angle_rad)
            self.position.y += distance * math.sin(angle_rad)
            
            km_traveled = distance / 100
            self.odometer += km_traveled
            
            if self.velocity > 0:
                fuel_consumed = km_traveled / self.fuel_efficiency
                self.fuel_level = max(0, self.fuel_level - fuel_consumed)
                
            self.engine_hours += dt / 3600
            
            if self.odometer % 1000 < 1:
                self.maintenance_needed = True
                
    def claxon(self):
        print("Â¡BEEP BEEP!")

class GameEngine:
    def __init__(self):
        self.state = GameState.MENU
        self.stats = GameStats()
        self.achievements = self._load_achievements()
        self.active_missions = []
        self.completed_missions = []
        
        self.map_width = 2000
        self.map_height = 1500
        self.current_map = ProceduralMap(self.map_width, self.map_height)
        
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 1.0
        
        self.player_trucks = []
        self.active_truck = None
        
        self.game_start_time = time.time()
        self.last_update_time = time.time()
        
        self.settings = {
            'sound_enabled': True,
            'music_volume': 0.7,
            'auto_save': True,
            'difficulty': 'normal'
        }
        
    def _load_achievements(self) -> List[Achievement]:
        return [
            Achievement("first_delivery", "Primera Entrega", "Completa tu primera mision", 100),
            Achievement("millionaire", "Millonario", "Acumula $100,000", 1000),
            Achievement("speed_demon", "Demonio de Velocidad", "Alcanza velocidad maxima 100 veces", 500),
            Achievement("long_hauler", "Transportista", "Recorre 10,000 km", 2000),
            Achievement("fleet_master", "Maestro de Flota", "Posee 5 camiones", 1500),
            Achievement("perfect_week", "Semana Perfecta", "Completa 50 misiones", 3000),
        ]
    
    def generate_mission(self) -> Mission:
        if not self.current_map.buildings or len(self.current_map.buildings) < 2:
            return Mission(
                id=f"M{int(time.time() * 1000) % 100000}",
                type=MissionType.DELIVERY,
                cargo_type="Carga General",
                weight=1000,
                distance=500,
                reward=200,
                time_limit=300,
                pickup_location=(400, 300),
                delivery_location=(800, 600),
                difficulty=1
            )
            
        cargo_types = ["Electronicos", "Alimentos", "Muebles", "Ropa", "Maquinaria", "Materiales"]
        
        warehouse_buildings = [b for b in self.current_map.buildings if b['type'] in ['warehouse', 'factory']]
        delivery_buildings = [b for b in self.current_map.buildings if b['type'] in ['store', 'mall', 'office']]
        
        if not warehouse_buildings:
            warehouse_buildings = self.current_map.buildings[:len(self.current_map.buildings)//2]
        if not delivery_buildings:
            delivery_buildings = self.current_map.buildings[len(self.current_map.buildings)//2:]
            
        pickup_building = random.choice(warehouse_buildings)
        delivery_building = random.choice(delivery_buildings)
        
        distance = math.sqrt(
            (pickup_building['position'].x - delivery_building['position'].x)**2 + 
            (pickup_building['position'].y - delivery_building['position'].y)**2
        )
        
        difficulty = random.randint(1, 5)
        base_weight = 500 + difficulty * 200
        weight = random.uniform(base_weight * 0.8, base_weight * 1.2)
        
        base_reward = int(distance * 0.5 + weight * 0.1 + difficulty * 100)
        reward = random.randint(int(base_reward * 0.8), int(base_reward * 1.2))
        
        time_limit = max(300, int(distance * 2 + difficulty * 60))
        
        return Mission(
            id=f"M{int(time.time() * 1000) % 100000}",
            type=random.choice(list(MissionType)),
            cargo_type=random.choice(cargo_types),
            weight=weight,
            distance=distance,
            reward=reward,
            time_limit=time_limit,
            pickup_location=(pickup_building['position'].x, pickup_building['position'].y),
            delivery_location=(delivery_building['position'].x, delivery_building['position'].y),
            difficulty=difficulty
        )
    
    def complete_mission(self, mission: Mission):
        self.stats.money += mission.reward
        exp_gained = mission.difficulty * 20 + int(mission.distance / 10)
        self.stats.experience += exp_gained
        self.stats.missions_completed += 1
        self.stats.total_cargo += mission.weight
        
        level_threshold = self.stats.level * 1000
        level_up = False
        if self.stats.experience >= level_threshold:
            self.stats.level += 1
            self.stats.money += self.stats.level * 500
            level_up = True
        
        self._check_achievements()
        
        if mission in self.active_missions:
            self.active_missions.remove(mission)
        self.completed_missions.append(mission)
        
        return {
            'money': mission.reward,
            'experience': exp_gained,
            'level_up': level_up
        }
    
    def _check_achievements(self):
        for achievement in self.achievements:
            if not achievement.unlocked:
                if achievement.id == "first_delivery" and self.stats.missions_completed >= 1:
                    self._unlock_achievement(achievement)
                elif achievement.id == "millionaire" and self.stats.money >= 100000:
                    self._unlock_achievement(achievement)
                elif achievement.id == "long_hauler" and self.stats.total_distance >= 10000:
                    self._unlock_achievement(achievement)
                elif achievement.id == "perfect_week" and self.stats.missions_completed >= 50:
                    self._unlock_achievement(achievement)
                elif achievement.id == "fleet_master" and len(self.player_trucks) >= 5:
                    self._unlock_achievement(achievement)
    
    def _unlock_achievement(self, achievement: Achievement):
        achievement.unlocked = True
        self.stats.money += achievement.reward
        print(f"Logro desbloqueado: {achievement.name}! +${achievement.reward}")

# ========== MAIN GAME CLASS ==========

class TruckTycoonGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Truck Tycoon Simulator")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#2c3e50')
        
        self.engine = GameEngine()
        
        self.canvas_width = 1200
        self.canvas_height = 800
        self.main_canvas = None
        
        self.keys_pressed = set()
        self.controls = {'forward': False, 'backward': False, 'left': False, 'right': False}
        self.running = False
        
        self.create_menu_interface()
        
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.focus_set()
        
    def create_menu_interface(self):
        self.clear_interface()
        
        menu_frame = tk.Frame(self.root, bg='#2c3e50')
        menu_frame.pack(fill='both', expand=True)
        
        title_label = tk.Label(
            menu_frame, 
            text="TRUCK TYCOON SIMULATOR",
            font=('Arial', 36, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack(pady=50)
        
        subtitle_label = tk.Label(
            menu_frame,
            text="El simulador de camiones mas realista",
            font=('Arial', 14),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=10)
        
        buttons_frame = tk.Frame(menu_frame, bg='#2c3e50')
        buttons_frame.pack(pady=50)
        
        # Botones del menÃº
        tk.Button(
            buttons_frame,
            text="JUGAR",
            command=self.start_new_game,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#3498db',
            fg='white'
        ).pack(pady=10)
        
        tk.Button(
            buttons_frame,
            text="CARGAR PARTIDA",
            command=self.load_game,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#27ae60',
            fg='white'
        ).pack(pady=10)
        
        tk.Button(
            buttons_frame,
            text="CONFIGURACION",
            command=self.show_settings,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#f39c12',
            fg='white'
        ).pack(pady=10)
        
        tk.Button(
            buttons_frame,
            text="LOGROS",
            command=self.show_achievements,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#9b59b6',
            fg='white'
        ).pack(pady=10)
        
        tk.Button(
            buttons_frame,
            text="SALIR",
            command=self.root.quit,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#e74c3c',
            fg='white'
        ).pack(pady=10)
        
        # EstadÃ­sticas
        stats_frame = tk.Frame(menu_frame, bg='#34495e')
        stats_frame.pack(side='bottom', fill='x', pady=20, padx=50)
        
        stats_text = f"Dinero: ${self.engine.stats.money:,.0f} | Nivel: {self.engine.stats.level} | Misiones: {self.engine.stats.missions_completed}"
        tk.Label(
            stats_frame,
            text=stats_text,
            font=('Arial', 12),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(pady=10)
    
    def create_game_interface(self):
        self.clear_interface()
        
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True)
        
        # HUD superior
        hud_frame = tk.Frame(main_frame, bg='#34495e', height=80)
        hud_frame.pack(fill='x', side='top')
        hud_frame.pack_propagate(False)
        
        self.create_hud(hud_frame)
        
        # Frame principal dividido
        game_frame = tk.Frame(main_frame, bg='#2c3e50')
        game_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo
        left_panel = tk.Frame(game_frame, bg='#34495e', width=300)
        left_panel.pack(fill='y', side='left')
        left_panel.pack_propagate(False)
        
        self.create_control_panel(left_panel)
        
        # Canvas principal
        canvas_frame = tk.Frame(game_frame, bg='#000000')
        canvas_frame.pack(fill='both', expand=True, side='left')
        
        self.main_canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='#27ae60',
            highlightthickness=0
        )
        self.main_canvas.pack(fill='both', expand=True)
        
        # Panel derecho
        right_panel = tk.Frame(game_frame, bg='#34495e', width=250)
        right_panel.pack(fill='y', side='right')
        right_panel.pack_propagate(False)
        
        self.create_info_panel(right_panel)
        
        self.main_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.main_canvas.focus_set()
        
        if not self.engine.player_trucks:
            self.create_initial_truck()
    
    def create_hud(self, parent):
        info_frame = tk.Frame(parent, bg='#34495e')
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        self.money_label = tk.Label(
            info_frame,
            text=f"Dinero: ${self.engine.stats.money:,.0f}",
            font=('Arial', 14, 'bold'),
            fg='#f1c40f',
            bg='#34495e'
        )
        self.money_label.pack(side='left', padx=20)
        
        self.level_label = tk.Label(
            info_frame,
            text=f"Nivel {self.engine.stats.level}",
            font=('Arial', 14, 'bold'),
            fg='#e74c3c',
            bg='#34495e'
        )
        self.level_label.pack(side='left', padx=20)
        
        exp_needed = self.engine.stats.level * 1000
        exp_progress = (self.engine.stats.experience / exp_needed) * 100 if exp_needed > 0 else 0
        self.exp_label = tk.Label(
            info_frame,
            text=f"EXP: {self.engine.stats.experience}/{exp_needed} ({exp_progress:.1f}%)",
            font=('Arial', 12),
            fg='#3498db',
            bg='#34495e'
        )
        self.exp_label.pack(side='left', padx=20)
        
        # Botones de control
        control_frame = tk.Frame(parent, bg='#34495e')
        control_frame.pack(side='right', padx=10, pady=10)
        
        tk.Button(
            control_frame,
            text="PAUSA",
            command=self.pause_game,
            font=('Arial', 10, 'bold'),
            bg='#f39c12',
            fg='white'
        ).pack(side='right', padx=5)
        
        tk.Button(
            control_frame,
            text="MAPA",
            command=self.toggle_full_map,
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white'
        ).pack(side='right', padx=5)
        
        tk.Button(
            control_frame,
            text="MENU",
            command=self.return_to_menu,
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white'
        ).pack(side='right', padx=5)
    
    def create_control_panel(self, parent):
        title_label = tk.Label(
            parent,
            text="CONTROLES Y MISIONES",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        title_label.pack(pady=10)
        
        # Info del camiÃ³n
        truck_frame = tk.LabelFrame(
            parent,
            text="Camion Actual",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        truck_frame.pack(fill='x', padx=10, pady=5)
        
        self.truck_info_label = tk.Label(
            truck_frame,
            text="Sin camion activo",
            font=('Arial', 9),
            fg='#bdc3c7',
            bg='#34495e',
            justify='left'
        )
        self.truck_info_label.pack(padx=5, pady=5)
        
        # Controles
        controls_frame = tk.LabelFrame(
            parent,
            text="Controles",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        controls_text = """WASD / Flechas: Mover
SPACE: Claxon  
R: Recoger/Entregar
ESC: Pausar
M: Vista mapa completo"""
        
        tk.Label(
            controls_frame,
            text=controls_text,
            font=('Arial', 9),
            fg='#bdc3c7',
            bg='#34495e',
            justify='left'
        ).pack(padx=5, pady=5)
        
        # Misiones activas
        missions_frame = tk.LabelFrame(
            parent,
            text="Misiones Activas",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        missions_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lista de misiones con scroll
        self.missions_list_frame = tk.Frame(missions_frame, bg='#34495e')
        self.missions_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # BotÃ³n para nueva misiÃ³n
        tk.Button(
            parent,
            text="+ Nueva Mision",
            command=self.generate_new_mission,
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white'
        ).pack(pady=10)
    
    def create_info_panel(self, parent):
        title_label = tk.Label(
            parent,
            text="INFORMACION",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        title_label.pack(pady=10)
        
        # EstadÃ­sticas
        stats_frame = tk.LabelFrame(
            parent,
            text="Estadisticas",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_label = tk.Label(
            stats_frame,
            text=self.get_stats_text(),
            font=('Arial', 9),
            fg='#bdc3c7',
            bg='#34495e',
            justify='left'
        )
        self.stats_label.pack(padx=5, pady=5)
        
        # Minimap
        minimap_frame = tk.LabelFrame(
            parent,
            text="Mini-Mapa",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        minimap_frame.pack(fill='x', padx=10, pady=5)
        
        self.minimap_canvas = tk.Canvas(
            minimap_frame,
            width=200,
            height=150,
            bg='#27ae60',
            highlightthickness=1,
            highlightbackground='#7f8c8d'
        )
        self.minimap_canvas.pack(padx=5, pady=5)
        
        # Logros recientes
        achievements_frame = tk.LabelFrame(
            parent,
            text="Logros Recientes",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        achievements_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        unlocked_achievements = [a for a in self.engine.achievements if a.unlocked]
        if unlocked_achievements:
            for achievement in unlocked_achievements[-3:]:
                tk.Label(
                    achievements_frame,
                    text=f"* {achievement.name}",
                    font=('Arial', 9),
                    fg='#f1c40f',
                    bg='#34495e'
                ).pack(anchor='w', padx=5, pady=2)
        else:
            tk.Label(
                achievements_frame,
                text="No hay logros desbloqueados",
                font=('Arial', 9),
                fg='#7f8c8d',
                bg='#34495e'
            ).pack(padx=5, pady=5)
    
    def create_initial_truck(self):
        start_x = self.engine.map_width // 4
        start_y = self.engine.map_height // 4
        
        if self.engine.current_map.roads:
            for road in self.engine.current_map.roads[:5]:
                road_center_x = (road['start'].x + road['end'].x) / 2
                road_center_y = (road['start'].y + road['end'].y) / 2
                start_x = road_center_x
                start_y = road_center_y
                break
        
        truck_physics = EnhancedTruckPhysics(
            Point(start_x, start_y),
            TruckType.LIGHT,
            heading=0
        )
        
        self.engine.player_trucks.append(truck_physics)
        self.engine.active_truck = truck_physics
        
        self.engine.camera_x = start_x - self.canvas_width // 2
        self.engine.camera_y = start_y - self.canvas_height // 2
    
    # ========== GAME METHODS ==========
    
    def start_new_game(self):
        self.engine.stats = GameStats()
        self.engine.active_missions = []
        self.engine.completed_missions = []
        self.engine.player_trucks = []
        
        self.engine.current_map = ProceduralMap(self.engine.map_width, self.engine.map_height)
        
        self.engine.state = GameState.PLAYING
        self.create_game_interface()
        
        self.create_initial_truck()
        
        for _ in range(3):
            self.generate_new_mission()
        
        self.running = True
        self.game_loop()
    
    def load_game(self):
        try:
            if os.path.exists("truck_tycoon_save.json"):
                with open("truck_tycoon_save.json", 'r') as f:
                    save_data = json.load(f)
                
                self.engine.stats = GameStats(**save_data['stats'])
                
                for i, achievement_data in enumerate(save_data.get('achievements', [])):
                    if i < len(self.engine.achievements):
                        self.engine.achievements[i].unlocked = achievement_data.get('unlocked', False)
                
                messagebox.showinfo("Carga Exitosa", "Partida cargada correctamente")
                self.start_new_game()
            else:
                messagebox.showwarning("Sin Guardado", "No se encontrÃ³ ninguna partida guardada")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la partida: {str(e)}")
    
    def save_game(self):
        try:
            save_data = {
                'stats': asdict(self.engine.stats),
                'achievements': [{'unlocked': a.unlocked} for a in self.engine.achievements],
                'settings': self.engine.settings,
                'timestamp': datetime.now().isoformat()
            }
            
            with open("truck_tycoon_save.json", 'w') as f:
                json.dump(save_data, f, indent=2)
            
            messagebox.showinfo("Guardado", "Partida guardada exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def generate_new_mission(self):
        mission = self.engine.generate_mission()
        self.engine.active_missions.append(mission)
        self.update_missions_display()
    
    def game_loop(self):
        if not self.running or self.engine.state != GameState.PLAYING:
            return
        
        current_time = time.time()
        dt = current_time - self.engine.last_update_time
        self.engine.last_update_time = current_time
        
        if self.engine.active_truck:
            self.engine.active_truck.update(self.controls, dt)
            self.update_camera_follow()
            self.engine.stats.playtime += dt
        
        self.update_missions()
        self.render_game()
        self.update_interface()
        
        self.root.after(16, self.game_loop)
    
    def update_camera_follow(self):
        if not self.engine.active_truck:
            return
        
        truck = self.engine.active_truck
        
        target_x = truck.position.x - self.canvas_width // 2
        target_y = truck.position.y - self.canvas_height // 2
        
        # Cámara más responsiva basada en velocidad del truck
        base_speed = 0.15
        velocity_factor = min(1.0, abs(truck.velocity) / truck.max_speed)
        camera_speed = base_speed + (velocity_factor * 0.1)
        
        self.engine.camera_x += (target_x - self.engine.camera_x) * camera_speed
        self.engine.camera_y += (target_y - self.engine.camera_y) * camera_speed
        
        self.engine.camera_x = max(0, min(self.engine.camera_x, self.engine.map_width - self.canvas_width))
        self.engine.camera_y = max(0, min(self.engine.camera_y, self.engine.map_height - self.canvas_height))
    
    # ========== RENDERING METHODS ==========
    
    def render_game(self):
        if not self.main_canvas:
            return
        
        self.main_canvas.delete("all")
        self.render_map()
        self.render_trucks()
        self.render_mission_markers()
        self.render_game_ui()
        self.update_minimap()
    
    def render_map(self):
        camera_x = self.engine.camera_x
        camera_y = self.engine.camera_y
        
        # Renderizar carreteras
        for road in self.engine.current_map.roads:
            start_x = road['start'].x - camera_x
            start_y = road['start'].y - camera_y
            end_x = road['end'].x - camera_x
            end_y = road['end'].y - camera_y
            
            if self.is_visible(start_x, start_y, end_x, end_y):
                self.main_canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    width=road['width'],
                    fill='#2c3e50',
                    capstyle='round'
                )
                
                if road['type'] == 'main' and road['width'] > 50:
                    self.main_canvas.create_line(
                        start_x, start_y, end_x, end_y,
                        width=3,
                        fill='#f1c40f',
                        dash=(10, 10)
                    )
        
        # Renderizar edificios
        for building in self.engine.current_map.buildings:
            x = building['position'].x - camera_x
            y = building['position'].y - camera_y
            width, height = building['size']
            
            if self.is_visible(x - width//2, y - height//2, x + width//2, y + height//2):
                # Sombra
                self.main_canvas.create_rectangle(
                    x - width//2 + 5, y - height//2 + 5,
                    x + width//2 + 5, y + height//2 + 5,
                    fill='#2c3e50', outline='', width=0
                )
                
                # Edificio
                self.main_canvas.create_rectangle(
                    x - width//2, y - height//2,
                    x + width//2, y + height//2,
                    fill=building['color'],
                    outline='#34495e',
                    width=2
                )
                
                # Nombre
                name = building['name'][:8] + "..." if len(building['name']) > 8 else building['name']
                self.main_canvas.create_text(
                    x, y,
                    text=name,
                    font=('Arial', 8, 'bold'),
                    fill='white'
                )
        
        # Renderizar semÃ¡foros
        for traffic_light in self.engine.current_map.traffic_lights:
            x = traffic_light['position'].x - camera_x
            y = traffic_light['position'].y - camera_y
            
            if self.is_visible(x - 20, y - 20, x + 20, y + 20):
                # Poste
                self.main_canvas.create_rectangle(
                    x - 8, y - 15,
                    x + 8, y + 15,
                    fill='#2c3e50',
                    outline='#34495e'
                )
                
                # Luz
                light_colors = {
                    'red': '#e74c3c',
                    'yellow': '#f1c40f',
                    'green': '#27ae60'
                }
                light_color = light_colors.get(traffic_light['state'], '#7f8c8d')
                
                self.main_canvas.create_oval(
                    x - 6, y - 6,
                    x + 6, y + 6,
                    fill=light_color,
                    outline='#34495e'
                )
    
    def render_trucks(self):
        camera_x = self.engine.camera_x
        camera_y = self.engine.camera_y
        
        for truck in self.engine.player_trucks:
            x = truck.position.x - camera_x
            y = truck.position.y - camera_y
            
            if self.is_visible(x - 30, y - 30, x + 30, y + 30):
                self.render_truck(truck, x, y)
    
    def render_truck(self, truck_physics, screen_x, screen_y):
        truck_sizes = {
            TruckType.LIGHT: (20, 12),
            TruckType.MEDIUM: (24, 14),
            TruckType.HEAVY: (28, 16),
            TruckType.SUPER_HEAVY: (32, 18)
        }
        
        width, height = truck_sizes.get(truck_physics.truck_type, (24, 14))
        
        truck_colors = {
            TruckType.LIGHT: '#3498db',
            TruckType.MEDIUM: '#e67e22',
            TruckType.HEAVY: '#e74c3c',
            TruckType.SUPER_HEAVY: '#8e44ad'
        }
        
        color = truck_colors.get(truck_physics.truck_type, '#3498db')
        
        # Calcular rectÃ¡ngulo rotado
        angle = math.radians(truck_physics.heading - 90)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        
        points = [
            (-width//2, -height//2), (width//2, -height//2),
            (width//2, height//2), (-width//2, height//2)
        ]
        
        rotated_points = []
        for px, py in points:
            rx = px * cos_a - py * sin_a + screen_x
            ry = px * sin_a + py * cos_a + screen_y
            rotated_points.extend([rx, ry])
        
        # Sombra
        shadow_points = [p + 3 for p in rotated_points]
        self.main_canvas.create_polygon(
            shadow_points,
            fill='#2c3e50',
            outline='',
            width=0
        )
        
        # Cuerpo del camiÃ³n
        self.main_canvas.create_polygon(
            rotated_points,
            fill=color,
            outline='#2c3e50',
            width=2
        )
        
        # Cabina
        cabin_width = width // 3
        cabin_points = [
            (-cabin_width//2, -height//2), (cabin_width//2, -height//2),
            (cabin_width//2, -height//4), (-cabin_width//2, -height//4)
        ]
        
        rotated_cabin = []
        for px, py in cabin_points:
            rx = px * cos_a - py * sin_a + screen_x
            ry = px * sin_a + py * cos_a + screen_y
            rotated_cabin.extend([rx, ry])
        
        darker_color = self.darken_color(color)
        self.main_canvas.create_polygon(
            rotated_cabin,
            fill=darker_color,
            outline='#2c3e50',
            width=1
        )
        
        # Indicador de camiÃ³n activo
        if truck_physics == self.engine.active_truck:
            self.main_canvas.create_oval(
                screen_x - width//2 - 8, screen_y - height//2 - 8,
                screen_x + width//2 + 8, screen_y + height//2 + 8,
                outline='#f1c40f',
                width=3
            )
        
        # Barra de combustible si estÃ¡ bajo
        if truck_physics.fuel_level < 30:
            fuel_width = 30
            fuel_height = 4
            fuel_x = screen_x - fuel_width // 2
            fuel_y = screen_y + height//2 + 15
            
            # Fondo
            self.main_canvas.create_rectangle(
                fuel_x, fuel_y,
                fuel_x + fuel_width, fuel_y + fuel_height,
                fill='#2c3e50',
                outline='#7f8c8d'
            )
            
            # Nivel de combustible
            fuel_level_width = (truck_physics.fuel_level / 100.0) * fuel_width
            fuel_color = '#e74c3c' if truck_physics.fuel_level < 20 else '#f39c12'
            
            if fuel_level_width > 0:
                self.main_canvas.create_rectangle(
                    fuel_x, fuel_y,
                    fuel_x + fuel_level_width, fuel_y + fuel_height,
                    fill=fuel_color,
                    outline=''
                )
            
            # Texto
            self.main_canvas.create_text(
                screen_x, fuel_y + fuel_height + 8,
                text=f"Fuel {truck_physics.fuel_level:.0f}%",
                font=('Arial', 8),
                fill='white'
            )
    
    def render_mission_markers(self):
        camera_x = self.engine.camera_x
        camera_y = self.engine.camera_y
        
        for mission in self.engine.active_missions:
            # Marcador de recogida
            pickup_x = mission.pickup_location[0] - camera_x
            pickup_y = mission.pickup_location[1] - camera_y
            
            if self.is_visible(pickup_x - 30, pickup_y - 30, pickup_x + 30, pickup_y + 30):
                # Pulso
                pulse = abs(math.sin(time.time() * 3)) * 10 + 15
                
                self.main_canvas.create_oval(
                    pickup_x - pulse, pickup_y - pulse,
                    pickup_x + pulse, pickup_y + pulse,
                    outline='#f39c12',
                    width=3,
                    fill='#f39c12'
                )
                
                marker_text = "OK" if mission.is_active else "P"
                self.main_canvas.create_text(
                    pickup_x, pickup_y,
                    text=marker_text,
                    font=('Arial', 12, 'bold'),
                    fill='white'
                )
                
                self.main_canvas.create_text(
                    pickup_x, pickup_y + 25,
                    text=f"${mission.reward}",
                    font=('Arial', 10, 'bold'),
                    fill='#f1c40f'
                )
            
            # Marcador de entrega (solo si activa)
            if mission.is_active:
                delivery_x = mission.delivery_location[0] - camera_x
                delivery_y = mission.delivery_location[1] - camera_y
                
                if self.is_visible(delivery_x - 30, delivery_y - 30, delivery_x + 30, delivery_y + 30):
                    self.main_canvas.create_oval(
                        delivery_x - 15, delivery_y - 15,
                        delivery_x + 15, delivery_y + 15,
                        outline='#27ae60',
                        width=3,
                        fill='#27ae60'
                    )
                    
                    self.main_canvas.create_text(
                        delivery_x, delivery_y,
                        text="D",
                        font=('Arial', 12, 'bold'),
                        fill='white'
                    )
    
    def render_game_ui(self):
        if not self.engine.active_truck:
            return
        
        truck = self.engine.active_truck
        
        # VelocÃ­metro
        speedometer_x = 80
        speedometer_y = self.canvas_height - 80
        speedometer_radius = 50
        
        # CÃ­rculo del velocÃ­metro
        self.main_canvas.create_oval(
            speedometer_x - speedometer_radius, speedometer_y - speedometer_radius,
            speedometer_x + speedometer_radius, speedometer_y + speedometer_radius,
            fill='#2c3e50',
            outline='#ecf0f1',
            width=3
        )
        
        # Marcas
        max_speed_display = max(truck.max_speed * 1.2, 5)
        for i in range(0, int(max_speed_display) + 1, max(1, int(max_speed_display // 5))):
            angle = math.radians(225 - (i / max_speed_display) * 270)
            x1 = speedometer_x + (speedometer_radius - 10) * math.cos(angle)
            y1 = speedometer_y + (speedometer_radius - 10) * math.sin(angle)
            x2 = speedometer_x + (speedometer_radius - 5) * math.cos(angle)
            y2 = speedometer_y + (speedometer_radius - 5) * math.sin(angle)
            
            self.main_canvas.create_line(x1, y1, x2, y2, fill='#ecf0f1', width=2)
        
        # Aguja
        speed_ratio = min(abs(truck.velocity) / max_speed_display, 1.0)
        needle_angle = math.radians(225 - speed_ratio * 270)
        needle_length = speedometer_radius - 15
        
        needle_x = speedometer_x + needle_length * math.cos(needle_angle)
        needle_y = speedometer_y + needle_length * math.sin(needle_angle)
        
        self.main_canvas.create_line(
            speedometer_x, speedometer_y,
            needle_x, needle_y,
            fill='#e74c3c',
            width=4,
            capstyle='round'
        )
        
        # Texto de velocidad
        self.main_canvas.create_text(
            speedometer_x, speedometer_y + 20,
            text=f"{abs(truck.velocity):.1f}",
            font=('Arial', 12, 'bold'),
            fill='#ecf0f1'
        )
        
        # BrÃºjula
        compass_x = self.canvas_width - 60
        compass_y = 60
        compass_radius = 30
        
        self.main_canvas.create_oval(
            compass_x - compass_radius, compass_y - compass_radius,
            compass_x + compass_radius, compass_y + compass_radius,
            fill='#34495e',
            outline='#ecf0f1',
            width=2
        )
        
        # Aguja de la brÃºjula
        north_angle = math.radians(-truck.heading)
        north_x = compass_x + (compass_radius - 10) * math.cos(north_angle)
        north_y = compass_y + (compass_radius - 10) * math.sin(north_angle)
        
        self.main_canvas.create_line(
            compass_x, compass_y,
            north_x, north_y,
            fill='#e74c3c',
            width=3,
            arrow=tk.LAST
        )
        
        # N
        self.main_canvas.create_text(
            compass_x, compass_y - compass_radius - 15,
            text="N",
            font=('Arial', 12, 'bold'),
            fill='#ecf0f1'
        )
    
    def update_minimap(self):
        if not hasattr(self, 'minimap_canvas'):
            return
        
        self.minimap_canvas.delete("all")
        
        scale_x = 200 / self.engine.map_width
        scale_y = 150 / self.engine.map_height
        
        # Carreteras en minimapa
        for road in self.engine.current_map.roads[:20]:
            x1 = road['start'].x * scale_x
            y1 = road['start'].y * scale_y
            x2 = road['end'].x * scale_x
            y2 = road['end'].y * scale_y
            
            self.minimap_canvas.create_line(
                x1, y1, x2, y2,
                fill='#34495e',
                width=1
            )
        
        # Edificios
        for building in self.engine.current_map.buildings[:15]:
            x = building['position'].x * scale_x
            y = building['position'].y * scale_y
            
            self.minimap_canvas.create_rectangle(
                x - 2, y - 2, x + 2, y + 2,
                fill=building['color'],
                outline=''
            )
        
        # CamiÃ³n activo
        if self.engine.active_truck:
            truck_x = self.engine.active_truck.position.x * scale_x
            truck_y = self.engine.active_truck.position.y * scale_y
            
            self.minimap_canvas.create_oval(
                truck_x - 3, truck_y - 3,
                truck_x + 3, truck_y + 3,
                fill='#f1c40f',
                outline='#2c3e50'
            )
        
        # Ãrea visible
        camera_x1 = self.engine.camera_x * scale_x
        camera_y1 = self.engine.camera_y * scale_y
        camera_x2 = (self.engine.camera_x + self.canvas_width) * scale_x
        camera_y2 = (self.engine.camera_y + self.canvas_height) * scale_y
        
        self.minimap_canvas.create_rectangle(
            camera_x1, camera_y1, camera_x2, camera_y2,
            outline='#ecf0f1',
            width=2,
            fill=''
        )
    
    # ========== CONTROL METHODS ==========
    
    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        
        self.controls['forward'] = 'w' in self.keys_pressed or 'up' in self.keys_pressed
        self.controls['backward'] = 's' in self.keys_pressed or 'down' in self.keys_pressed
        self.controls['left'] = 'a' in self.keys_pressed or 'left' in self.keys_pressed
        self.controls['right'] = 'd' in self.keys_pressed or 'right' in self.keys_pressed
        
        if key == 'space':
            self.honk_horn()
        elif key == 'r':
            self.interact_with_nearby()
        elif key == 'escape':
            self.pause_game()
        elif key == 'm':
            self.toggle_full_map()
    
    def on_key_release(self, event):
        key = event.keysym.lower()
        self.keys_pressed.discard(key)
        
        self.controls['forward'] = 'w' in self.keys_pressed or 'up' in self.keys_pressed
        self.controls['backward'] = 's' in self.keys_pressed or 'down' in self.keys_pressed
        self.controls['left'] = 'a' in self.keys_pressed or 'left' in self.keys_pressed
        self.controls['right'] = 'd' in self.keys_pressed or 'right' in self.keys_pressed
    
    def honk_horn(self):
        if self.engine.active_truck:
            self.engine.active_truck.claxon()
    
    def interact_with_nearby(self):
        if not self.engine.active_truck:
            return
        
        truck_pos = self.engine.active_truck.position
        interaction_distance = 50
        
        for mission in self.engine.active_missions:
            pickup_distance = math.sqrt(
                (truck_pos.x - mission.pickup_location[0])**2 + 
                (truck_pos.y - mission.pickup_location[1])**2
            )
            
            delivery_distance = math.sqrt(
                (truck_pos.x - mission.delivery_location[0])**2 + 
                (truck_pos.y - mission.delivery_location[1])**2
            )
            
            if pickup_distance < interaction_distance and not mission.is_active:
                mission.is_active = True
                mission.start_time = time.time()
                messagebox.showinfo("Carga Recogida", 
                    f"Â¡Carga recogida!\nTipo: {mission.cargo_type}\nPeso: {mission.weight:.0f} kg")
                break
            
            elif delivery_distance < interaction_distance and mission.is_active:
                completion_result = self.engine.complete_mission(mission)
                
                message = f"""Â¡Mision completada!
Dinero ganado: ${completion_result['money']}
Experiencia: +{completion_result['experience']}"""
                
                if completion_result.get('level_up'):
                    message += f"\nÂ¡Subiste al nivel {self.engine.stats.level}!"
                
                messagebox.showinfo("Mision Completada", message)
                self.update_missions_display()
                break
    
    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.engine.zoom_level = min(2.0, self.engine.zoom_level * 1.1)
        else:
            self.engine.zoom_level = max(0.5, self.engine.zoom_level * 0.9)
    
    # ========== UTILITY METHODS ==========
    
    def is_visible(self, x1, y1, x2, y2):
        return not (x2 < 0 or x1 > self.canvas_width or y2 < 0 or y1 > self.canvas_height)
    
    def darken_color(self, color):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.7)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def get_stats_text(self):
        stats = self.engine.stats
        return f"""Dinero: ${stats.money:,.0f}
Nivel: {stats.level}
EXP: {stats.experience:,}
Misiones: {stats.missions_completed}
Distancia: {stats.total_distance:.1f} km
Tiempo: {stats.playtime/3600:.1f}h
Carga: {stats.total_cargo:,.0f} kg"""
    
    def update_interface(self):
        if self.engine.state != GameState.PLAYING:
            return
        
        if hasattr(self, 'money_label'):
            self.money_label.config(text=f"Dinero: ${self.engine.stats.money:,.0f}")
        
        if hasattr(self, 'level_label'):
            self.level_label.config(text=f"Nivel {self.engine.stats.level}")
        
        if hasattr(self, 'exp_label'):
            exp_needed = self.engine.stats.level * 1000
            exp_progress = (self.engine.stats.experience / exp_needed) * 100 if exp_needed > 0 else 0
            self.exp_label.config(
                text=f"EXP: {self.engine.stats.experience}/{exp_needed} ({exp_progress:.1f}%)"
            )
        
        if hasattr(self, 'truck_info_label') and self.engine.active_truck:
            physics = self.engine.active_truck
            spec = TRUCK_SPECS[physics.truck_type]
            
            maintenance_status = "MANTENIMIENTO" if physics.maintenance_needed else "OK"
            
            self.truck_info_label.config(text=f"""Tipo: {spec.name}
Velocidad: {physics.velocity:.1f}/{physics.max_speed:.1f}
Combustible: {physics.fuel_level:.1f}/100L
Odometro: {physics.odometer:.1f} km
Estado: {maintenance_status}""")
        
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text=self.get_stats_text())
    
    def update_missions(self):
        current_time = time.time()
        missions_to_remove = []
        
        for mission in self.engine.active_missions:
            if mission.is_active and mission.start_time:
                elapsed_time = current_time - mission.start_time
                if elapsed_time > mission.time_limit:
                    missions_to_remove.append(mission)
                    messagebox.showwarning("Mision Expirada", 
                        f"La mision {mission.id} ha expirado!")
        
        for mission in missions_to_remove:
            if mission in self.engine.active_missions:
                self.engine.active_missions.remove(mission)
        
        if missions_to_remove:
            self.update_missions_display()
    
    def update_missions_display(self):
        if not hasattr(self, 'missions_list_frame'):
            return
        
        for widget in self.missions_list_frame.winfo_children():
            widget.destroy()
        
        if not self.engine.active_missions:
            tk.Label(
                self.missions_list_frame,
                text="No hay misiones activas",
                font=('Arial', 10),
                fg='#7f8c8d',
                bg='#34495e'
            ).pack(pady=10)
            return
        
        for mission in self.engine.active_missions:
            mission_frame = tk.Frame(self.missions_list_frame, bg='#2c3e50', relief='raised', bd=1)
            mission_frame.pack(fill='x', padx=5, pady=2)
            
            status_text = "EN CURSO" if mission.is_active else "DISPONIBLE"
            
            time_text = ""
            if mission.is_active and mission.start_time:
                elapsed = time.time() - mission.start_time
                remaining = max(0, mission.time_limit - elapsed)
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                time_text = f" - {minutes}:{seconds:02d}"
            
            tk.Label(
                mission_frame,
                text=f"{mission.id} - {status_text}{time_text}",
                font=('Arial', 9, 'bold'),
                fg='#ecf0f1',
                bg='#2c3e50'
            ).pack(anchor='w', padx=5, pady=2)
            
            details_text = f"""{mission.cargo_type} ({mission.weight:.0f} kg)
Recompensa: ${mission.reward}
Distancia: {mission.distance:.0f}m
Dificultad: {'*' * mission.difficulty}"""
            
            tk.Label(
                mission_frame,
                text=details_text,
                font=('Arial', 8),
                fg='#bdc3c7',
                bg='#2c3e50',
                justify='left'
            ).pack(anchor='w', padx=10, pady=2)
    
    def pause_game(self):
        if self.engine.state == GameState.PLAYING:
            self.engine.state = GameState.PAUSED
            self.running = False
            messagebox.showinfo("Juego Pausado", "Presiona ESC nuevamente para continuar")
        elif self.engine.state == GameState.PAUSED:
            self.engine.state = GameState.PLAYING
            self.running = True
            self.game_loop()
    
    def toggle_full_map(self):
        if self.engine.zoom_level > 0.8:
            self.engine.zoom_level = 0.3
        else:
            self.engine.zoom_level = 1.0
    
    def return_to_menu(self):
        if messagebox.askyesno("Volver al Menu", "Â¿Quieres guardar antes de salir?"):
            self.save_game()
        
        self.running = False
        self.engine.state = GameState.MENU
        self.create_menu_interface()
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configuracion")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#2c3e50')
        
        sound_frame = tk.LabelFrame(
            settings_window,
            text="Sonido",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        sound_frame.pack(fill='x', padx=20, pady=10)
        
        sound_var = tk.BooleanVar(value=self.engine.settings['sound_enabled'])
        tk.Checkbutton(
            sound_frame,
            text="Habilitar sonidos",
            variable=sound_var,
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#34495e',
            selectcolor='#27ae60',
            command=lambda: self.engine.settings.update({'sound_enabled': sound_var.get()})
        ).pack(anchor='w', padx=10, pady=5)
        
        difficulty_frame = tk.LabelFrame(
            settings_window,
            text="Dificultad",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        difficulty_frame.pack(fill='x', padx=20, pady=10)
        
        difficulty_var = tk.StringVar(value=self.engine.settings['difficulty'])
        difficulties = ["Facil", "Normal", "Dificil", "Extremo"]
        for diff in difficulties:
            tk.Radiobutton(
                difficulty_frame,
                text=diff,
                variable=difficulty_var,
                value=diff.lower(),
                font=('Arial', 10),
                fg='#ecf0f1',
                bg='#34495e',
                selectcolor='#3498db',
                command=lambda: self.engine.settings.update({'difficulty': difficulty_var.get()})
            ).pack(anchor='w', padx=10, pady=2)
    
    def show_achievements(self):
        achievements_window = tk.Toplevel(self.root)
        achievements_window.title("Logros")
        achievements_window.geometry("600x500")
        achievements_window.configure(bg='#2c3e50')
        
        canvas = tk.Canvas(achievements_window, bg='#2c3e50')
        scrollbar = tk.Scrollbar(achievements_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c3e50')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for achievement in self.engine.achievements:
            achievement_frame = tk.Frame(
                scrollable_frame,
                bg='#34495e' if achievement.unlocked else '#2c3e50',
                relief='raised',
                bd=2
            )
            achievement_frame.pack(fill='x', padx=10, pady=5)
            
            status_icon = "*" if achievement.unlocked else "-"
            title_color = "#f1c40f" if achievement.unlocked else "#7f8c8d"
            
            tk.Label(
                achievement_frame,
                text=f"{status_icon} {achievement.name}",
                font=('Arial', 14, 'bold'),
                fg=title_color,
                bg='#34495e' if achievement.unlocked else '#2c3e50'
            ).pack(anchor='w', padx=10, pady=5)
            
            tk.Label(
                achievement_frame,
                text=achievement.description,
                font=('Arial', 10),
                fg='#bdc3c7',
                bg='#34495e' if achievement.unlocked else '#2c3e50'
            ).pack(anchor='w', padx=10, pady=2)
            
            tk.Label(
                achievement_frame,
                text=f"Recompensa: ${achievement.reward}",
                font=('Arial', 10, 'bold'),
                fg='#27ae60',
                bg='#34495e' if achievement.unlocked else '#2c3e50'
            ).pack(anchor='w', padx=10, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def clear_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def on_closing(self):
        if self.engine.state == GameState.PLAYING:
            if messagebox.askyesno("Salir", "Â¿Quieres guardar antes de salir?"):
                self.save_game()
        
        self.running = False
        self.root.quit()
    
    def run(self):
        self.root.mainloop()

# ========== MAIN ==========
if __name__ == "__main__":
    print("Iniciando Truck Tycoon Simulator...")
    print("Cargando motor del juego...")
    
    try:
        game = TruckTycoonGame()
        print("Juego cargado exitosamente")
        print("Â¡Disfruta del juego!")
        game.run()
    except Exception as e:
        print(f"Error al iniciar el juego: {e}")
        import traceback
        traceback.print_exc()
