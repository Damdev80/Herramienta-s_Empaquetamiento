"""
Modular App Controller
Controlador para la aplicación con módulos separados
"""
import os
import threading
import tempfile
import shutil
from typing import List, Optional, Dict, Any
from ..models.file_manager import FileManager
from ..models.converter_operations import ConverterOperations

class ModularAppController:
    def __init__(self):
        self.file_manager = FileManager()
        self.converter = ConverterOperations()
        self.view = None
        
        # Estado de procesamiento
        self.is_processing_flag = False
        self.current_process_thread = None
        
        # Configurar callbacks del converter
        self.converter.set_callbacks(
            progress_callback=self.on_progress,
            completion_callback=self.on_completion
        )
        
    def set_view(self, view):
        """Establecer referencia a la vista"""
        self.view = view
        
    def is_processing(self) -> bool:
        """Verificar si hay un proceso en curso"""
        return self.is_processing_flag
        
    # ==================== MÓDULO DE CONVERSIÓN DE COLORES ====================
    
    def start_color_conversion_module(self, params: Dict[str, Any]):
        """Iniciar proceso de conversión de colores"""
        if self.is_processing_flag:
            if self.view:
                self.view.show_completion_message("Procesando", "Ya hay un proceso en curso", True)
            return
            
        # Validar parámetros
        if not params.get("files"):
            if self.view:
                self.view.show_completion_message("Error", "No hay archivos seleccionados", True)
            return
            
        if not params.get("output_dir"):
            if self.view:
                self.view.show_completion_message("Error", "No se ha seleccionado directorio de salida", True)
            return
            
        # Iniciar en hilo separado
        self.current_process_thread = threading.Thread(
            target=self._process_color_conversion,
            args=(params,),
            daemon=True
        )
        self.current_process_thread.start()
        
    def _process_color_conversion(self, params: Dict[str, Any]):
        """Procesar conversión de colores en hilo separado"""
        try:
            self.is_processing_flag = True
            
            files = params["files"]
            output_dir = params["output_dir"]
            conversion_type = params.get("conversion_type", "bw")
            delete_originals = params.get("delete_originals", False)
            open_output = params.get("open_output", True)
            
            total_files = len(files)
            processed_files = []
            
            for i, file_path in enumerate(files):
                if self.view:
                    progress = (i / total_files) * 100
                    self.view.update_progress(progress, f"Procesando: {os.path.basename(file_path)}")
                
                try:
                    # Generar path de salida
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    if ext == '.pdf':
                        # Para PDFs, usar método específico
                        if conversion_type == "sepia":
                            output_path = os.path.join(output_dir, f"{base_name}_sepia.pdf")
                            success, message = self.converter.convert_pdf_to_sepia(file_path, output_path)
                        else:  # bw
                            output_path = os.path.join(output_dir, f"{base_name}_bw.pdf")
                            success, message = self.converter.convert_pdf_to_bw(file_path, output_path)
                    else:
                        # Para imágenes
                        if conversion_type == "sepia":
                            output_path = os.path.join(output_dir, f"{base_name}_sepia{ext}")
                            success, message = self.converter.convert_image_to_sepia(file_path, output_path)
                        else:  # bw
                            output_path = os.path.join(output_dir, f"{base_name}_bw{ext}")
                            success, message = self.converter.convert_image_to_bw(file_path, output_path)
                    
                    if success:
                        processed_files.append(output_path)
                        
                        # Eliminar original si se solicita
                        if delete_originals:
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                print(f"No se pudo eliminar {file_path}: {e}")
                    else:
                        print(f"Error procesando {file_path}: {message}")
                                
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
                    
            # Proceso completado
            if self.view:
                self.view.update_progress(100, "Conversión completada")
                
                success_count = len(processed_files)
                message = f"✅ Conversión completada\\n\\n"
                message += f"Archivos procesados: {success_count}/{total_files}\\n"
                message += f"Guardados en: {output_dir}"
                
                if delete_originals and success_count > 0:
                    message += f"\\n\\n🗑️ Archivos originales eliminados: {success_count}"
                
                self.view.show_completion_message("Conversión Completada", message)
                
                # Abrir carpeta de salida
                if open_output and success_count > 0:
                    self._open_folder(output_dir)
                    
        except Exception as e:
            if self.view:
                self.view.show_completion_message("Error", f"Error durante la conversión:\\n{str(e)}", True)
        finally:
            self.is_processing_flag = False
            
    # ==================== MÓDULO DE UNIÓN DE PDFs ====================
    
    def start_pdf_merge_module(self, params: Dict[str, Any]):
        """Iniciar proceso de unión de PDFs"""
        if self.is_processing_flag:
            if self.view:
                self.view.show_completion_message("Procesando", "Ya hay un proceso en curso", True)
            return
            
        # Validar parámetros
        if not params.get("files"):
            if self.view:
                self.view.show_completion_message("Error", "No hay PDFs seleccionados", True)
            return
            
        if not params.get("output_dir"):
            if self.view:
                self.view.show_completion_message("Error", "No se ha seleccionado directorio de salida", True)
            return
            
        # Validar que sean PDFs
        pdf_files = [f for f in params["files"] if f.lower().endswith('.pdf')]
        if len(pdf_files) != len(params["files"]):
            if self.view:
                self.view.show_completion_message("Error", "Solo se pueden unir archivos PDF", True)
            return
            
        if len(pdf_files) < 2:
            if self.view:
                self.view.show_completion_message("Error", "Se necesitan al menos 2 PDFs para unir", True)
            return
            
        # Iniciar en hilo separado
        self.current_process_thread = threading.Thread(
            target=self._process_pdf_merge,
            args=(params,),
            daemon=True
        )
        self.current_process_thread.start()
        
    def _process_pdf_merge(self, params: Dict[str, Any]):
        """Procesar unión de PDFs en hilo separado"""
        try:
            self.is_processing_flag = True
            
            files = params["files"]
            output_dir = params["output_dir"]
            output_name = params.get("output_name", "merged_document.pdf")
            delete_originals = params.get("delete_originals", False)
            open_output = params.get("open_output", True)
            
            if self.view:
                self.view.update_progress(20, "Iniciando unión de PDFs...")
            
            # Crear archivo de salida
            output_path = os.path.join(output_dir, output_name)
            
            # Unir PDFs
            success = self.converter.merge_pdfs(files, output_path)
            
            if success:
                if self.view:
                    self.view.update_progress(80, "Unión completada, limpiando...")
                
                # Eliminar originales si se solicita
                deleted_count = 0
                if delete_originals:
                    for file_path in files:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            print(f"No se pudo eliminar {file_path}: {e}")
                
                if self.view:
                    self.view.update_progress(100, "Proceso completado")
                    
                    message = f"✅ PDFs unidos exitosamente\\n\\n"
                    message += f"Archivos unidos: {len(files)}\\n"
                    message += f"Archivo creado: {output_name}\\n"
                    message += f"Ubicación: {output_dir}"
                    
                    if delete_originals and deleted_count > 0:
                        message += f"\\n\\n🗑️ Archivos originales eliminados: {deleted_count}"
                    
                    self.view.show_completion_message("Unión Completada", message)
                    
                    # Abrir carpeta de salida
                    if open_output:
                        self._open_folder(output_dir)
            else:
                if self.view:
                    self.view.show_completion_message("Error", "No se pudieron unir los PDFs", True)
                    
        except Exception as e:
            if self.view:
                self.view.show_completion_message("Error", f"Error durante la unión:\\n{str(e)}", True)
        finally:
            self.is_processing_flag = False
            
    # ==================== MÓDULO COMBINADO ====================
    
    def start_both_process_module(self, params: Dict[str, Any]):
        """Iniciar proceso combinado (conversión + unión)"""
        if self.is_processing_flag:
            if self.view:
                self.view.show_completion_message("Procesando", "Ya hay un proceso en curso", True)
            return
            
        # Validar parámetros
        if not params.get("files"):
            if self.view:
                self.view.show_completion_message("Error", "No hay archivos seleccionados", True)
            return
            
        if not params.get("output_dir"):
            if self.view:
                self.view.show_completion_message("Error", "No se ha seleccionado directorio de salida", True)
            return
            
        # Iniciar en hilo separado
        self.current_process_thread = threading.Thread(
            target=self._process_both_operations,
            args=(params,),
            daemon=True
        )
        self.current_process_thread.start()
        
    def _process_both_operations(self, params: Dict[str, Any]):
        """Procesar conversión + unión en hilo separado"""
        temp_dir = None
        try:
            self.is_processing_flag = True
            
            files = params["files"]
            output_dir = params["output_dir"]
            output_name = params.get("output_name", "converted_merged.pdf")
            conversion_type = params.get("conversion_type", "bw")
            delete_originals = params.get("delete_originals", False)
            delete_intermediates = params.get("delete_intermediates", True)
            open_output = params.get("open_output", True)
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp(prefix="pdf_converter_")
            
            if self.view:
                self.view.update_progress(5, "Iniciando proceso combinado...")
            
            # FASE 1: Convertir todos los archivos
            converted_files = []
            total_files = len(files)
            
            for i, file_path in enumerate(files):
                base_progress = 10 + (i / total_files) * 60  # 10% a 70%
                
                if self.view:
                    self.view.update_progress(base_progress, f"Convirtiendo: {os.path.basename(file_path)}")
                
                try:
                    ext = os.path.splitext(file_path)[1].lower()
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    
                    if ext == '.pdf':
                        # Convertir PDF
                        if conversion_type == "sepia":
                            output_path = os.path.join(temp_dir, f"{base_name}_sepia.pdf")
                            success, message = self.converter.convert_pdf_to_sepia(file_path, output_path)
                        else:
                            output_path = os.path.join(temp_dir, f"{base_name}_bw.pdf")
                            success, message = self.converter.convert_pdf_to_bw(file_path, output_path)
                            
                        if success:
                            converted_files.append(output_path)
                        else:
                            print(f"Error convirtiendo PDF {file_path}: {message}")
                            # Usar original si falla la conversión
                            converted_files.append(file_path)
                            
                    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
                        # Convertir imagen
                        if conversion_type == "sepia":
                            img_output = os.path.join(temp_dir, f"{base_name}_sepia{ext}")
                            success, message = self.converter.convert_image_to_sepia(file_path, img_output)
                        else:
                            img_output = os.path.join(temp_dir, f"{base_name}_bw{ext}")
                            success, message = self.converter.convert_image_to_bw(file_path, img_output)
                            
                        if success:
                            # Convertir imagen a PDF
                            pdf_path = os.path.join(temp_dir, f"{base_name}_converted.pdf")
                            if self._create_pdf_from_image(img_output, pdf_path):
                                converted_files.append(pdf_path)
                            else:
                                print(f"Error creando PDF de imagen {file_path}")
                        else:
                            print(f"Error convirtiendo imagen {file_path}: {message}")
                            # Intentar crear PDF con imagen original
                            pdf_path = os.path.join(temp_dir, f"{base_name}_original.pdf")
                            if self._create_pdf_from_image(file_path, pdf_path):
                                converted_files.append(pdf_path)
                    else:
                        print(f"Tipo de archivo no soportado: {file_path}")
                        
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
                    
            if self.view:
                self.view.update_progress(75, "Uniendo archivos convertidos...")
            
            # FASE 2: Unir todos los PDFs convertidos
            if converted_files:
                output_path = os.path.join(output_dir, output_name)
                success = self.converter.merge_pdfs(converted_files, output_path)
                
                if success:
                    if self.view:
                        self.view.update_progress(90, "Limpiando archivos...")
                    
                    # Eliminar originales si se solicita
                    deleted_originals = 0
                    if delete_originals:
                        for file_path in files:
                            try:
                                os.remove(file_path)
                                deleted_originals += 1
                            except Exception as e:
                                print(f"No se pudo eliminar {file_path}: {e}")
                    
                    if self.view:
                        self.view.update_progress(100, "Proceso completado")
                        
                        message = f"✅ Proceso combinado completado\\n\\n"
                        message += f"Archivos procesados: {len(files)}\\n"
                        message += f"Archivos convertidos: {len(converted_files)}\\n"
                        message += f"PDF final: {output_name}\\n"
                        message += f"Ubicación: {output_dir}"
                        
                        if delete_originals and deleted_originals > 0:
                            message += f"\\n\\n🗑️ Archivos originales eliminados: {deleted_originals}"
                        
                        if delete_intermediates:
                            message += f"\\n🗂️ Archivos temporales limpiados"
                        
                        self.view.show_completion_message("Proceso Completado", message)
                        
                        # Abrir carpeta de salida
                        if open_output:
                            self._open_folder(output_dir)
                else:
                    if self.view:
                        self.view.show_completion_message("Error", "No se pudo crear el PDF final", True)
            else:
                if self.view:
                    self.view.show_completion_message("Error", "No se pudieron procesar los archivos", True)
                    
        except Exception as e:
            if self.view:
                self.view.show_completion_message("Error", f"Error durante el proceso:\\n{str(e)}", True)
        finally:
            # Limpiar directorio temporal
            if temp_dir and delete_intermediates and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"No se pudo limpiar directorio temporal: {e}")
                    
            self.is_processing_flag = False
            
    def _create_pdf_from_image(self, image_path: str, pdf_path: str) -> bool:
        """Crear PDF desde imagen usando PIL"""
        try:
            from PIL import Image
            
            img = Image.open(image_path)
            
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            img.save(pdf_path, "PDF", resolution=100.0)
            return True
            
        except Exception as e:
            print(f"Error creando PDF desde imagen: {e}")
            return False
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def _open_folder(self, folder_path: str):
        """Abrir carpeta en el explorador"""
        try:
            import subprocess
            import platform
            
            # Verificar que la carpeta existe
            if not os.path.exists(folder_path):
                print(f"La carpeta no existe: {folder_path}")
                return
            
            # Normalizar la ruta
            folder_path = os.path.abspath(folder_path)
            
            if platform.system() == "Windows":
                # Usar explorer con la ruta absoluta
                subprocess.run(["explorer", folder_path], check=False)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path], check=False)
            else:  # Linux
                subprocess.run(["xdg-open", folder_path], check=False)
                
            print(f"✅ Abriendo carpeta: {folder_path}")
            
        except Exception as e:
            print(f"No se pudo abrir la carpeta {folder_path}: {e}")
            # Intentar abrir la carpeta padre si falla
            try:
                parent_dir = os.path.dirname(folder_path)
                if os.path.exists(parent_dir):
                    subprocess.run(["explorer", parent_dir], check=False)
                    print(f"📁 Abriendo carpeta padre: {parent_dir}")
            except:
                print(f"❌ No se pudo abrir ninguna carpeta relacionada")
            
    def on_progress(self, progress: float, message: str = ""):
        """Callback de progreso del converter"""
        if self.view:
            self.view.update_progress(progress, message)
            
    def on_completion(self, success: bool, message: str = ""):
        """Callback de completación del converter"""
        # Este callback se usa por el converter interno
        # Los mensajes principales se manejan en los métodos de proceso
        pass
        
    # ==================== GESTIÓN DE CONFIGURACIÓN ====================
    
    def get_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones guardadas"""
        return self.file_manager.get_settings()
        
    def update_setting(self, key: str, value: Any):
        """Actualizar configuración"""
        self.file_manager.update_setting(key, value)
        
    def set_output_directory(self, directory: str):
        """Establecer directorio de salida"""
        self.file_manager.set_output_directory(directory)
