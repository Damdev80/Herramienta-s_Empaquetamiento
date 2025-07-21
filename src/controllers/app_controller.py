"""
Controller: Main Application Controller
Coordina la comunicación entre modelo y vista
"""
import os
from typing import List, Optional, Dict, Any
from ..models.file_manager import FileManager
from ..models.converter_operations import ConverterOperations

class AppController:
    def __init__(self):
        self.file_manager = FileManager()
        self.converter = ConverterOperations()
        self.view = None  # Se asignará desde la vista
        
        # Configurar callbacks del converter
        self.converter.set_callbacks(
            progress_callback=self.on_conversion_progress,
            completion_callback=self.on_conversion_completed
        )
    
    def set_view(self, view):
        """Establecer referencia a la vista"""
        self.view = view
    
    # ==================== GESTIÓN DE ARCHIVOS ====================
    
    def select_files(self, file_paths: List[str], clear_existing: bool = True) -> int:
        """Seleccionar archivos"""
        new_count = self.file_manager.add_files(file_paths, clear_existing)
        if self.view:
            self.view.update_file_list()
            self.view.update_status()
        return new_count
    
    def add_files(self, file_paths: List[str]) -> int:
        """Agregar más archivos"""
        return self.select_files(file_paths, clear_existing=False)
    
    def remove_file(self, index: int) -> bool:
        """Remover archivo por índice"""
        success = self.file_manager.remove_file(index)
        if success and self.view:
            self.view.update_file_list()
            self.view.update_status()
        return success
    
    def clear_files(self):
        """Limpiar lista de archivos"""
        self.file_manager.clear_files()
        if self.view:
            self.view.update_file_list()
            self.view.update_status()
    
    def set_output_directory(self, directory: str) -> bool:
        """Establecer directorio de salida"""
        success = self.file_manager.set_output_directory(directory)
        if success and self.view:
            self.view.update_output_directory_display()
        return success
    
    def get_file_info(self, index: int) -> Optional[Dict[str, Any]]:
        """Obtener información de archivo por índice"""
        if 0 <= index < len(self.file_manager.selected_files):
            file_path = self.file_manager.selected_files[index]
            return self.file_manager.get_file_info(file_path)
        return None
    
    # ==================== OPERACIONES DE CONVERSIÓN ====================
    
    def validate_conversion(self, operation_type: str = "convert") -> Dict[str, Any]:
        """Validar si se puede realizar una conversión"""
        return self.file_manager.validate_operation(operation_type)
    
    def start_color_conversion(self, conversion_type: str = "bw"):
        """Iniciar conversión de color"""
        validation = self.validate_conversion()
        if not validation["valid"]:
            if self.view:
                self.view.show_warning("Validación", validation["message"])
            return
        
        # Confirmar operación
        count = len(self.file_manager.selected_files)
        type_name = "blanco y negro" if conversion_type == "bw" else "sepia"
        
        if self.view and not self.view.confirm_operation(
            f"¿Convertir {count} archivo(s) a {type_name}?",
            f"Se guardarán en: {self.file_manager.output_directory}"
        ):
            return
        
        # Iniciar conversión
        self.converter.convert_files_async(
            self.file_manager.selected_files,
            self.file_manager.output_directory,
            conversion_type
        )
    
    def start_pdf_merge(self, order_option: str = "orden_seleccion", 
                       custom_order: Optional[List[str]] = None):
        """Iniciar unión de PDFs"""
        validation = self.file_manager.validate_operation("merge_pdf")
        if not validation["valid"]:
            if self.view:
                self.view.show_warning("Validación", validation["message"])
            return
        
        pdf_files = self.file_manager.get_pdf_files()
        
        # Ordenar archivos según opción
        if order_option == "alfabetico":
            pdf_files.sort(key=lambda x: os.path.basename(x).lower())
        elif order_option == "personalizado" and custom_order:
            pdf_files = custom_order
        
        # Obtener nombre de archivo de salida
        if self.view:
            output_name = self.view.get_output_filename("PDF_Unido")
            if not output_name:
                return
        else:
            output_name = "PDF_Unido"
        
        output_path = os.path.join(
            self.file_manager.output_directory, 
            f"{output_name}.pdf"
        )
        
        # Confirmar operación
        if self.view and not self.view.confirm_operation(
            f"¿Unir {len(pdf_files)} PDFs?",
            f"Se guardará como: {output_name}.pdf"
        ):
            return
        
        # Ejecutar unión
        success, message = self.converter.merge_pdfs(pdf_files, output_path)
        
        if self.view:
            if success:
                self.view.show_success("Completado", message)
            else:
                self.view.show_error("Error", message)
    
    # ==================== CALLBACKS ====================
    
    def on_conversion_progress(self, progress: float, status: str):
        """Callback para progreso de conversión"""
        if self.view:
            self.view.update_progress(progress, status)
    
    def on_conversion_completed(self, successful: int, total: int, failed_files: List[str]):
        """Callback para finalización de conversión"""
        if self.view:
            self.view.on_conversion_completed(successful, total, failed_files)
    
    # ==================== CONFIGURACIONES ====================
    
    def get_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones"""
        return self.file_manager.settings
    
    def update_setting(self, key: str, value: Any):
        """Actualizar configuración"""
        self.file_manager.settings[key] = value
        self.file_manager.save_settings()
    
    def get_available_tools(self) -> Dict[str, bool]:
        """Obtener herramientas disponibles"""
        return self.converter.get_available_tools()
    
    # ==================== DATOS PARA LA VISTA ====================
    
    def get_selected_files(self) -> List[str]:
        """Obtener archivos seleccionados"""
        return self.file_manager.selected_files.copy()
    
    def get_output_directory(self) -> str:
        """Obtener directorio de salida"""
        return self.file_manager.output_directory
    
    def get_file_counts(self) -> Dict[str, int]:
        """Obtener conteos de archivos"""
        return self.file_manager.get_file_counts()
    
    def get_pdf_files(self) -> List[str]:
        """Obtener solo archivos PDF"""
        return self.file_manager.get_pdf_files()
    
    def is_processing(self) -> bool:
        """Verificar si se está procesando"""
        return self.converter.is_processing
