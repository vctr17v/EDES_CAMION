"""
DEMO: Simulador Avanzado de Camiones - Guía de Características
================================================================

Ejecuta este archivo para ver una demostración interactiva de las nuevas características.
"""

import sys
import os

# Asegurar que podamos importar nuestros módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ej6_2 import *

def print_banner():
    """Muestra el banner de bienvenida"""
    print("="*60)
    print("🚛 SIMULADOR AVANZADO DE CAMIONES - DEMO")
    print("="*60)
    print()
    print("✨ NUEVAS CARACTERÍSTICAS DESTACADAS:")
    print("🛣️  Sistema de carreteras realista")
    print("⌨️  Controles de teclado (WASD/Flechas)")  
    print("🚛 Gráficos realistas de camiones")
    print("📦 Sistema completo de entregas")
    print("🔊 Efectos de sonido múltiples")
    print("🎮 Física de movimiento realista")
    print()

def print_controls():
    """Muestra los controles"""
    print("🎮 CONTROLES:")
    print("  W/↑ : Acelerar")
    print("  S/↓ : Frenar/Reversa")
    print("  A/← : Girar izquierda")
    print("  D/→ : Girar derecha")
    print("  SPACE : Claxón/Freno")
    print("  R : Recoger/Entregar paquetes")
    print("  Clic izq : Seleccionar camión")
    print("  Clic der : Ver información")
    print()

def print_gameplay():
    """Explica la mecánica de juego"""
    print("📦 CÓMO JUGAR:")
    print("1. Selecciona un camión (clic izquierdo)")
    print("2. Maneja con WASD o flechas")
    print("3. Ve a almacenes (🏭) y presiona R para recoger paquetes")
    print("4. Lleva los paquetes a tiendas (🏪) y presiona R para entregar")
    print("5. Gestiona tu flota y optimiza rutas")
    print()

def show_building_types():
    """Muestra los tipos de edificios"""
    print("🏢 EDIFICIOS EN EL MAPA:")
    print("🏭 Almacenes (azules):")
    print("   • Almacén Central")
    print("   • Almacén Norte") 
    print("   • Almacén Sur")
    print()
    print("🏪 Puntos de entrega (verdes):")
    print("   • Tienda 1")
    print("   • Tienda 2") 
    print("   • Oficina A")
    print("   • Centro Comercial")
    print()

def show_technical_info():
    """Muestra información técnica"""
    print("⚙️ INFORMACIÓN TÉCNICA:")
    print(f"✓ Pygame disponible: {SOUND_AVAILABLE}")
    print("✓ Física realista: Aceleración, inercia, fricción")
    print("✓ Renderizado: 20 FPS para movimiento suave")  
    print("✓ Audio: 3 efectos de sonido generados proceduralmente")
    print("✓ Interfaz: 3 paneles con información en tiempo real")
    print()

def demo_package_system():
    """Demuestra el sistema de paquetes"""
    print("📦 SISTEMA DE PAQUETES:")
    
    # Crear algunos paquetes de ejemplo
    warehouse_pos = Point(80, 80)
    delivery_pos = Point(720, 520)
    
    sample_package = Package(
        id="DEMO001",
        pickup_point=warehouse_pos,
        delivery_point=delivery_pos,
        weight=75.5,
        state=PackageState.WAREHOUSE
    )
    
    print(f"   ID: {sample_package.id}")
    print(f"   Peso: {sample_package.weight:.1f} kg")
    print(f"   Estado: {sample_package.state.value}")
    print(f"   Origen: ({sample_package.pickup_point.x}, {sample_package.pickup_point.y})")
    print(f"   Destino: ({sample_package.delivery_point.x}, {sample_package.delivery_point.y})")
    print()

def launch_demo():
    """Lanza el simulador con mensaje de demostración"""
    print("🚀 INICIANDO SIMULADOR...")
    print("   (Cierra la ventana cuando termines)")
    print()
    
    try:
        simulator = AdvancedTruckSimulator()
        simulator.run()
        
        print("✓ Demo completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la demo: {e}")
        return False
    
    return True

def main():
    """Función principal de la demo"""
    print_banner()
    print_controls()
    print_gameplay()
    show_building_types()
    demo_package_system()
    show_technical_info()
    
    print("¿Deseas iniciar la demostración? (s/n): ", end="")
    
    try:
        response = input().lower().strip()
        
        if response in ['s', 'si', 'yes', 'y', '']:
            success = launch_demo()
            
            if success:
                print()
                print("🎉 ¡Gracias por probar el simulador avanzado!")
                print("💡 Características implementadas según solicitud:")
                print("   ✓ Carreteras realistas")
                print("   ✓ Controles de teclado") 
                print("   ✓ Camiones que parecen camiones")
                print("   ✓ Mecánica de entregas")
                print("   ✓ Y mucho más...")
            else:
                print("⚠️ La demo no pudo completarse correctamente")
        else:
            print("👋 ¡Demo cancelada! Puedes ejecutar ej6_2.py directamente.")
            
    except KeyboardInterrupt:
        print()
        print("👋 Demo interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()