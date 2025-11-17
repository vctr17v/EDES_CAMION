# 🚛 Sistema de Gestión de Camiones

## Descripción
Este proyecto contiene dos ejercicios que implementan un sistema de gestión de camiones y cajas usando Python.

## Ejercicios

### Ejercicio 1 (ej6_1.py)
Programa de consola que implementa las clases `Camión` y `Caja` con todas las funcionalidades requeridas:

#### Clase Caja
- **Atributos:** codigo, peso_kg, descripcion_carga, largo, ancho, altura
- **Métodos:** constructor, \_\_str\_\_

#### Clase Camión
- **Atributos:** matricula, conductor, capacidad_kg, descripcion_carga, rumbo, velocidad, cajas
- **Métodos:** 
  - `peso_total()` - calcula peso total de cajas
  - `add_caja(caja)` - añade caja si no excede capacidad
  - `setVelocidad(velocidad)` - modifica velocidad
  - `setRumbo(rumbo)` - modifica rumbo (1-359°)
  - `claxon()` - emite sonido "piiiiiii"
  - `__str__()` - información completa del camión

#### Funcionalidad
- Crea 2 camiones con 3 cajas cada uno
- Muestra información inicial
- Añade cajas adicionales (2 al primero, 3 al segundo)
- Modifica velocidades y rumbos
- Toca claxón del segundo camión
- Muestra información final

### Ejercicio 2 (ej6_2.py) - ⭐ VERSIÓN AVANZADA ⭐
Interfaz gráfica revolucionaria usando Tkinter que permite:

#### 🚛 Características principales:
- **🛣️ Sistema de carreteras realista:** Red compleja de carreteras con intersecciones y curvas
- **⌨️ Controles de teclado:** WASD/Flechas para manejar con física realista
- **🚛 Gráficos realistas:** Camiones con cabina, remolque y 6 ruedas
- **📦 Sistema de entregas:** Mecánica completa de recogida/entrega de paquetes
- **🏭 Edificios interactivos:** Almacenes y puntos de entrega
- **🔊 Audio avanzado:** Múltiples efectos de sonido (claxón, recogida, entrega)
- **🎮 Física realista:** Aceleración, inercia, fricción, giros naturales

#### 🎮 Controles avanzados:
- **W/↑:** Acelerar
- **S/↓:** Frenar/Reversa
- **A/←:** Girar izquierda
- **D/→:** Girar derecha  
- **SPACE:** Claxón/Freno
- **R:** Recoger/Entregar paquetes
- **Clic izquierdo:** Seleccionar camión
- **Clic derecho:** Ver información

#### 📦 Mecánica de juego:
- Recoge paquetes en almacenes (edificios azules 🏭)
- Entrega en puntos de destino (edificios verdes 🏪)
- Gestiona múltiples camiones en tu flota
- Optimiza rutas para máxima eficiencia
- Sistema de capacidad de carga realista

## Instalación y Ejecución

### Requisitos
```bash
pip install pygame
```

### Ejecutar Ejercicio 1
```bash
python ej6_1.py
```

### Ejecutar Ejercicio 2
```bash
python ej6_2.py
```

## Características Destacadas

### Validaciones
- Rumbo entre 1-359 grados
- Capacidad máxima de carga
- Entrada de datos en GUI

### Interfaz Gráfica
- Movimiento fluido de camiones
- Indicador visual de dirección
- Cambio de color para camión activo
- Rebote en bordes del mapa
- Lista actualizable de camiones

### Audio
- Sonido de claxón generado programáticamente
- Compatible con pygame
- Manejo de errores si pygame no está disponible

## Estructura del Proyecto
```
EJ5_CAMIONES/
├── ej6_1.py              # Ejercicio 1 - Programa de consola
├── ej6_2.py              # Ejercicio 2 - Simulador avanzado con carreteras
├── README.md             # Este archivo
├── ADVANCED_FEATURES.md  # Documentación detallada del simulador
└── GITHUB_INSTRUCTIONS.md # Instrucciones para GitHub
```

## Funcionalidades Avanzadas del Ejercicio 2

### 🛣️ Sistema de Carreteras
- Red compleja de carreteras principales y secundarias
- Líneas centrales discontinuas para realismo
- Intersecciones naturales entre calles
- Carreteras curvas simuladas

### 🚛 Física y Gráficos Realistas  
- Camiones con cabina y remolque separados
- 6 ruedas distribuidas correctamente
- Física de aceleración e inercia
- Movimiento natural con fricción

### 📦 Sistema de Entregas Completo
- Almacenes donde recoger paquetes
- Puntos de entrega donde dejarlos  
- Estados de paquetes: almacén → tránsito → entregado
- Validación de capacidad de carga

### 🎮 Experiencia de Juego
- Controles de teclado intuitivos (WASD/Flechas)
- Múltiples efectos de sonido
- Interfaz informativa en tiempo real
- Gestión de flota de múltiples camiones

## Autor
Fecha: 17 de Noviembre de 2025

---
*Proyecto desarrollado como parte del curso de programación en Python*