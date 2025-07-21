"""
Main Application Entry Point
Punto de entrada principal con arquitectura MVC
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Verificar dependencias primero
from src.utils.dependency_checker import DependencyChecker

def check_dependencies():
    """Verificar dependencias antes de iniciar"""
    checker = DependencyChecker()
    can_run, report = checker.check_and_show_report()
    
    print(report)
    
    if not can_run:
        # Crear ventana temporal para mostrar error
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        messagebox.showerror(
            "Dependencias Faltantes",
            "No se pueden ejecutar la aplicación.\n\n"
            "Faltan dependencias requeridas.\n"
            "Consulta la consola para más detalles."
        )
        
        root.destroy()
        return False
    
    return True

def main():
    """Función principal de la aplicación"""
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Importar componentes MVC modulares
    from src.controllers.modular_app_controller import ModularAppController
    from src.views.modular_main_view import ModularMainView
    
    # Crear ventana principal
    root = tk.Tk()
    
    try:
        # Crear vista y controlador modulares
        view = ModularMainView(root)
        controller = ModularAppController()
        
        # Conectar vista y controlador
        view.set_controller(controller)
        controller.set_view(view)
        
        # Configurar ventana
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, controller))
        
        # Mostrar aplicación
        print("✅ Aplicación modular iniciada correctamente!")
        print("🎯 3 módulos disponibles: Conversión, Unión PDFs, Ambos")
        print("�️ Arrastra y suelta archivos para cambiar orden")
        print("👁️ Click en vista previa para ver archivos")
        
        # Aplicar configuraciones guardadas
        settings = controller.get_settings()
        if settings.get("window_geometry"):
            root.geometry(settings["window_geometry"])
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error iniciando la aplicación:\n{str(e)}")
        print(f"❌ Error: {e}")
        sys.exit(1)

def on_closing(root, controller):
    """Manejar cierre de aplicación"""
    try:
        # Guardar configuraciones
        geometry = root.geometry()
        controller.update_setting("window_geometry", geometry)
        
        # Verificar si hay procesos en curso
        if controller.is_processing():
            if messagebox.askquestion(
                "Cerrando aplicación",
                "Hay una conversión en progreso.\n¿Estás seguro de que quieres cerrar?"
            ) != "yes":
                return
        
        root.destroy()
        
    except Exception as e:
        print(f"Error al cerrar: {e}")
        root.destroy()

if __name__ == "__main__":
    main()
