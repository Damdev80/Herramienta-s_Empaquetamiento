"""
Model: File Manager
Maneja la lógica de archivos y configuraciones
"""
import os
import json
from typing import List, Dict, Any, Optional

class FileManager:
    def __init__(self):
        self.selected_files: List[str] = []
        self.output_directory: str = ""
        self.settings: Dict[str, Any] = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Cargar configuraciones desde archivo"""
        settings_file = "settings.json"
        default_settings = {
            "last_output_directory": "",
            "theme": "default",
            "color_conversion_quality": "high",
            "merge_default_option": "orden_seleccion",
            "window_geometry": "900x700"
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge con configuraciones por defecto
                    default_settings.update(loaded_settings)
            return default_settings
        except Exception as e:
            print(f"Error cargando configuraciones: {e}")
            return default_settings
    
    def save_settings(self):
        """Guardar configuraciones a archivo"""
        try:
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuraciones: {e}")
    
    def add_files(self, files: List[str], clear_existing: bool = False) -> int:
        """Agregar archivos a la lista"""
        if clear_existing:
            self.selected_files.clear()
        
        new_files_count = 0
        for file_path in files:
            if file_path not in self.selected_files and os.path.exists(file_path):
                self.selected_files.append(file_path)
                new_files_count += 1
        
        return new_files_count
    
    def remove_file(self, index: int) -> bool:
        """Remover archivo por índice"""
        try:
            if 0 <= index < len(self.selected_files):
                self.selected_files.pop(index)
                return True
        except Exception:
            pass
        return False
    
    def clear_files(self):
        """Limpiar lista de archivos"""
        self.selected_files.clear()
    
    def set_output_directory(self, directory: str):
        """Establecer directorio de salida"""
        if os.path.exists(directory):
            self.output_directory = directory
            self.settings["last_output_directory"] = directory
            self.save_settings()
            return True
        return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Obtener información detallada de un archivo"""
        try:
            if not os.path.exists(file_path):
                return {"error": "Archivo no encontrado"}
            
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Formatear tamaño
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024*1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            
            info = {
                "name": file_name,
                "path": file_path,
                "size": file_size,
                "size_str": size_str,
                "extension": file_ext,
                "type": self._get_file_type(file_ext)
            }
            
            # Información específica por tipo
            if file_ext == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        info["pages"] = len(pdf_reader.pages)
                except:
                    info["pages"] = "No se pudo leer"
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
                try:
                    from PIL import Image
                    with Image.open(file_path) as img:
                        info["dimensions"] = f"{img.size[0]} x {img.size[1]} píxeles"
                        info["mode"] = img.mode
                except:
                    info["dimensions"] = "No se pudo leer"
                    info["mode"] = "Desconocido"
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_file_type(self, extension: str) -> str:
        """Determinar tipo de archivo"""
        if extension == '.pdf':
            return "PDF"
        elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            return "Imagen"
        else:
            return "Desconocido"
    
    def get_pdf_files(self) -> List[str]:
        """Obtener solo archivos PDF"""
        return [f for f in self.selected_files if f.lower().endswith('.pdf')]
    
    def get_image_files(self) -> List[str]:
        """Obtener solo archivos de imagen"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        return [f for f in self.selected_files if os.path.splitext(f)[1].lower() in image_extensions]
    
    def get_file_counts(self) -> Dict[str, int]:
        """Obtener conteos de archivos por tipo"""
        pdf_count = len(self.get_pdf_files())
        image_count = len(self.get_image_files())
        return {
            "total": len(self.selected_files),
            "pdf": pdf_count,
            "image": image_count
        }
    
    def validate_operation(self, operation_type: str) -> Dict[str, Any]:
        """Validar si una operación puede ejecutarse"""
        result = {"valid": False, "message": ""}
        
        if not self.selected_files:
            result["message"] = "No hay archivos seleccionados"
            return result
        
        if not self.output_directory:
            result["message"] = "No se ha seleccionado directorio de salida"
            return result
        
        if operation_type == "merge_pdf":
            pdf_files = self.get_pdf_files()
            if len(pdf_files) < 2:
                result["message"] = "Se necesitan al menos 2 archivos PDF para unir"
                return result
        
        result["valid"] = True
        result["message"] = "Operación válida"
        return result
    
    def get_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones actuales"""
        return self.settings.copy()
    
    def update_setting(self, key: str, value: Any):
        """Actualizar una configuración específica"""
        self.settings[key] = value
        self.save_settings()
    
    def set_output_directory(self, directory: str):
        """Establecer directorio de salida y guardarlo en configuraciones"""
        self.output_directory = directory
        self.update_setting("last_output_directory", directory)
