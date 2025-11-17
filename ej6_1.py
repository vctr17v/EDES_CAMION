"""
Ejercicio 1: Sistema de Gestión de Camiones y Cajas
Autor: [Tu nombre]
Fecha: 17 de Noviembre de 2025
"""


class Caja:
    """Clase que representa una caja con sus dimensiones y características"""
    
    def __init__(self, codigo: str, peso_kg: float, descripcion_carga: str, 
                 largo: float, ancho: float, altura: float):
        self.codigo = codigo
        self.peso_kg = peso_kg
        self.descripcion_carga = descripcion_carga
        self.largo = largo
        self.ancho = ancho
        self.altura = altura
    
    def __str__(self) -> str:
        """Representación en cadena de la caja"""
        volumen = self.largo * self.ancho * self.altura
        return (f"Caja {self.codigo}: {self.descripcion_carga}\n"
                f"  Peso: {self.peso_kg} kg\n"
                f"  Dimensiones: {self.largo}x{self.ancho}x{self.altura} cm\n"
                f"  Volumen: {volumen:.2f} cm³")


class Camion:
    """Clase que representa un camión con capacidad de carga"""
    
    def __init__(self, matricula: str, conductor: str, capacidad_kg: float, 
                 descripcion_carga: str, rumbo: int, velocidad: int):
        self.matricula = matricula
        self.conductor = conductor
        self.capacidad_kg = capacidad_kg
        self.descripcion_carga = descripcion_carga
        
        # Validar rumbo (1-359 grados)
        if 1 <= rumbo <= 359:
            self.rumbo = rumbo
        else:
            raise ValueError("El rumbo debe estar entre 1 y 359 grados")
        
        self.velocidad = velocidad
        self.cajas = []  # Lista de objetos Caja
    
    def peso_total(self) -> float:
        """Calcula la suma de pesos de todas las cajas cargadas"""
        return sum(caja.peso_kg for caja in self.cajas)
    
    def add_caja(self, caja):
        """Añade una caja si no supera la capacidad máxima"""
        peso_actual = self.peso_total()
        if peso_actual + caja.peso_kg <= self.capacidad_kg:
            self.cajas.append(caja)
            print(f"✓ Caja {caja.codigo} añadida al camión {self.matricula}")
        else:
            peso_exceso = (peso_actual + caja.peso_kg) - self.capacidad_kg
            print(f"⚠️ ERROR: No se puede añadir la caja {caja.codigo}")
            print(f"   Excedería la capacidad en {peso_exceso:.2f} kg")
            print(f"   Capacidad: {self.capacidad_kg} kg")
            print(f"   Peso actual: {peso_actual:.2f} kg")
            print(f"   Peso de la caja: {caja.peso_kg} kg")
    
    def setVelocidad(self, nueva_velocidad: int):
        """Establece una nueva velocidad"""
        self.velocidad = nueva_velocidad
        print(f"🚛 Camión {self.matricula} ahora va a {nueva_velocidad} km/h")
    
    def setRumbo(self, nuevo_rumbo: int):
        """Establece un nuevo rumbo"""
        if 1 <= nuevo_rumbo <= 359:
            self.rumbo = nuevo_rumbo
            print(f"🧭 Camión {self.matricula} ahora va con rumbo {nuevo_rumbo}°")
        else:
            print("⚠️ ERROR: El rumbo debe estar entre 1 y 359 grados")
    
    def claxon(self):
        """Toca el claxón del camión"""
        print(f"🔊 {self.matricula}: ¡¡¡PIIIIIII!!!")
    
    def __str__(self) -> str:
        """Representación completa del camión"""
        peso_total = self.peso_total()
        porcentaje_carga = (peso_total / self.capacidad_kg) * 100 if self.capacidad_kg > 0 else 0
        
        info = f"\n{'='*50}\n"
        info += f"🚛 CAMIÓN {self.matricula}\n"
        info += f"{'='*50}\n"
        info += f"Conductor: {self.conductor}\n"
        info += f"Descripción de carga: {self.descripcion_carga}\n"
        info += f"Rumbo: {self.rumbo}° | Velocidad: {self.velocidad} km/h\n"
        info += f"Capacidad máxima: {self.capacidad_kg} kg\n"
        info += f"Peso total cargado: {peso_total:.2f} kg ({porcentaje_carga:.1f}%)\n"
        info += f"Número de cajas: {len(self.cajas)}\n"
        
        if self.cajas:
            info += f"\n📦 CAJAS CARGADAS:\n"
            info += f"{'-'*30}\n"
            for i, caja in enumerate(self.cajas, 1):
                info += f"{i}. {caja}\n\n"
        else:
            info += "\n📦 No hay cajas cargadas\n"
        
        info += f"{'='*50}\n"
        return info


def main():
    """Función principal que ejecuta el programa"""
    print("🚛 SISTEMA DE GESTIÓN DE CAMIONES 🚛")
    print("="*50)
    
    # Crear dos camiones
    print("\n📝 Creando camiones...")
    camion1 = Camion("ABC123", "Juan Pérez", 5000.0, "Mercancía general", 45, 60)
    camion2 = Camion("XYZ789", "María García", 7000.0, "Productos electrónicos", 180, 80)
    
    # Crear cajas para el primer camión
    print("\n📦 Creando cajas para el primer camión...")
    cajas_camion1 = [
        Caja("C001", 500.0, "Electrodomésticos", 100, 80, 60),
        Caja("C002", 750.0, "Muebles", 120, 100, 80),
        Caja("C003", 300.0, "Ropa", 80, 60, 40)
    ]
    
    # Crear cajas para el segundo camión
    print("📦 Creando cajas para el segundo camión...")
    cajas_camion2 = [
        Caja("C004", 400.0, "Ordenadores", 60, 40, 30),
        Caja("C005", 600.0, "Televisores", 90, 70, 50),
        Caja("C006", 250.0, "Móviles", 40, 30, 20)
    ]
    
    # Cargar cajas en los camiones
    print("\n🚛 Cargando cajas en los camiones...")
    for caja in cajas_camion1:
        camion1.add_caja(caja)
    
    for caja in cajas_camion2:
        camion2.add_caja(caja)
    
    # Mostrar información inicial
    print("\n📊 INFORMACIÓN INICIAL DE LOS CAMIONES:")
    print(camion1)
    print(camion2)
    
    # Crear cajas adicionales
    print("\n📦 Creando cajas adicionales...")
    cajas_adicionales_c1 = [
        Caja("C007", 800.0, "Herramientas", 70, 50, 40),
        Caja("C008", 1200.0, "Maquinaria", 150, 100, 90)
    ]
    
    cajas_adicionales_c2 = [
        Caja("C009", 900.0, "Componentes PC", 80, 60, 50),
        Caja("C010", 1100.0, "Servidores", 100, 80, 70),
        Caja("C011", 350.0, "Accesorios", 50, 40, 30)
    ]
    
    # Añadir cajas adicionales
    print("\n🚛 Añadiendo cajas adicionales...")
    print("--- Al camión 1 (2 cajas adicionales) ---")
    for caja in cajas_adicionales_c1:
        camion1.add_caja(caja)
    
    print("\n--- Al camión 2 (3 cajas adicionales) ---")
    for caja in cajas_adicionales_c2:
        camion2.add_caja(caja)
    
    # Cambiar velocidades y rumbos
    print("\n🔧 Modificando velocidades y rumbos...")
    camion1.setVelocidad(90)
    camion1.setRumbo(120)
    camion2.setVelocidad(75)
    camion2.setRumbo(270)
    
    # El segundo camión toca el claxón
    print("\n🔊 El segundo camión toca el claxón:")
    camion2.claxon()
    
    # Mostrar información final
    print("\n📊 INFORMACIÓN FINAL DE LOS CAMIONES:")
    print(camion1)
    print(camion2)
    
    print("🎉 Programa terminado exitosamente!")


if __name__ == "__main__":
    main()