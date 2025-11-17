# 📝 Instrucciones para subir a GitHub

## Pasos para crear el repositorio en GitHub:

### 1. Crear repositorio en GitHub
1. Ve a [GitHub.com](https://github.com)
2. Haz clic en "New repository" (botón verde)
3. Nombre del repositorio: `ej6_camiones`
4. Descripción: "Sistema de gestión de camiones - Ejercicios 6.1 y 6.2"
5. Marca como "Public" 
6. **NO** marques "Initialize with README" (ya tenemos uno)
7. Haz clic en "Create repository"

### 2. Comandos para subir desde terminal (en esta carpeta):

```powershell
# Inicializar repositorio Git
git init

# Añadir archivos
git add .

# Hacer commit inicial
git commit -m "Ejercicios 6.1 y 6.2: Sistema de gestión de camiones con GUI"

# Configurar rama principal
git branch -M main

# Conectar con GitHub (reemplaza TU_USUARIO por tu nombre de usuario)
git remote add origin https://github.com/TU_USUARIO/ej6_camiones.git

# Subir archivos
git push -u origin main
```

### 3. Alternativa: Usar GitHub Desktop
1. Abre GitHub Desktop
2. File → Add Local Repository
3. Selecciona esta carpeta
4. Publica el repositorio con el nombre "ej6_camiones"

## Contenido del repositorio

El repositorio contiene:
- `ej6_1.py` - Ejercicio 1 (programa de consola)
- `ej6_2.py` - Ejercicio 2 (interfaz gráfica Tkinter)
- `README.md` - Documentación completa
- `GITHUB_INSTRUCTIONS.md` - Este archivo

## Enlace para el documento
Una vez subido, el enlace será:
`https://github.com/TU_USUARIO/ej6_camiones`

## Verificación
Para verificar que todo funciona:
1. Clona el repositorio en otra carpeta
2. Ejecuta `python ej6_1.py` 
3. Ejecuta `python ej6_2.py` (requiere pygame)

¡Listo para entregar! 🚀