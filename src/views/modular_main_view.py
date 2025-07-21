"""
New Main View with 3 separate modules
Vista principal nueva con 3 módulos separados
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import List, Optional, Dict, Any, Callable

from .drag_drop_widget import DragDropListbox

class ModularMainView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.controller = None
        
        # Variables para cada módulo
        self.current_module = "color"  # "color", "pdf", "both"
        self.files_widgets = {}  # Widget de archivos para cada módulo
        self.output_dirs = {}   # Directorios de salida para cada módulo
        
        # Variables de progreso
        self.progress_var = None
        self.progress_bar = None
        self.status_label = None
        
        self.setup_window()
        self.create_widgets()
        
    def set_controller(self, controller):
        """Establecer referencia al controlador"""
        self.controller = controller
        
    def setup_window(self):
        """Configurar ventana principal"""
        self.root.title("🎨 Convertidor PDF/Imagen - Módulos Separados")
        self.root.geometry("1100x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos para drag & drop
        style.configure("Dragging.TFrame", background="#e6f3ff", relief="raised", borderwidth=2)
        style.configure("Placeholder.TFrame", background="#ffcccc", relief="solid", borderwidth=2)
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear header
        self.create_header(main_frame)
        
        # Crear selector de módulos
        self.create_module_selector(main_frame)
        
        # Frame para contenido del módulo actual
        self.module_content_frame = ttk.Frame(main_frame)
        self.module_content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Crear progress bar global
        self.create_progress_section(main_frame)
        
        # Mostrar módulo inicial
        self.show_module("color")
        
    def create_header(self, parent):
        """Crear encabezado de la aplicación"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título principal
        title_label = ttk.Label(header_frame, 
                               text="🎨 Convertidor PDF/Imagen", 
                               font=("Arial", 20, "bold"))
        title_label.pack()
        
        # Subtítulo
        subtitle_label = ttk.Label(header_frame, 
                                  text="3 Módulos Separados • Arrastrar y Soltar • Vista Previa", 
                                  font=("Arial", 11), foreground="gray")
        subtitle_label.pack()
        
    def create_module_selector(self, parent):
        """Crear selector de módulos"""
        selector_frame = ttk.LabelFrame(parent, text="🎯 Seleccionar Módulo", padding="15")
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para botones
        buttons_frame = ttk.Frame(selector_frame)
        buttons_frame.pack()
        
        # Botones de módulos
        modules = [
            ("color", "🎨 Conversión de Colores", "Convertir imágenes y PDFs a blanco y negro o sepia"),
            ("pdf", "📄 Unir PDFs", "Unir múltiples PDFs con orden personalizable"),
            ("both", "🔄 Conversión + Unión", "Convertir colores Y unir PDFs en un solo proceso")
        ]
        
        self.module_buttons = {}
        
        for i, (module_id, title, description) in enumerate(modules):
            # Frame para cada módulo
            module_frame = ttk.Frame(buttons_frame)
            module_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
            
            # Botón principal
            btn = ttk.Button(module_frame, text=title, width=25,
                           command=lambda m=module_id: self.show_module(m))
            btn.pack(pady=(0, 5))
            
            # Descripción
            desc_label = ttk.Label(module_frame, text=description, 
                                  font=("Arial", 9), foreground="gray",
                                  wraplength=180, justify=tk.CENTER)
            desc_label.pack()
            
            self.module_buttons[module_id] = btn
            
    def create_progress_section(self, parent):
        """Crear sección de progreso global"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progreso", padding="10")
        progress_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(pady=(0, 5))
        
        # Label de estado
        self.status_label = ttk.Label(progress_frame, text="Listo para procesar archivos", 
                                     font=("Arial", 10))
        self.status_label.pack()
        
    def show_module(self, module_id: str):
        """Mostrar módulo específico"""
        self.current_module = module_id
        
        # Actualizar botones
        for btn_id, btn in self.module_buttons.items():
            if btn_id == module_id:
                btn.configure(style="Accent.TButton")
            else:
                btn.configure(style="TButton")
                
        # Limpiar contenido anterior
        for widget in self.module_content_frame.winfo_children():
            widget.destroy()
            
        # Crear contenido del módulo
        if module_id == "color":
            self.create_color_module()
        elif module_id == "pdf":
            self.create_pdf_module()
        elif module_id == "both":
            self.create_both_module()
            
    def create_color_module(self):
        """Crear módulo de conversión de colores"""
        # Frame principal del módulo
        module_frame = ttk.Frame(self.module_content_frame)
        module_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título del módulo
        title_label = ttk.Label(module_frame, 
                               text="🎨 Módulo: Conversión de Colores", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Frame principal horizontal
        main_horizontal = ttk.Frame(module_frame)
        main_horizontal.pack(fill=tk.BOTH, expand=True)
        
        # Lado izquierdo - Selección de archivos
        left_frame = ttk.LabelFrame(main_horizontal, text="📁 Archivos a Convertir", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Botones de archivo
        file_buttons_frame = ttk.Frame(left_frame)
        file_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_buttons_frame, text="➕ Agregar Archivos", 
                  command=lambda: self.add_files_to_module("color")).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_buttons_frame, text="🗑️ Limpiar", 
                  command=lambda: self.clear_files_module("color")).pack(side=tk.LEFT)
        
        # Widget drag & drop para archivos
        self.files_widgets["color"] = DragDropListbox(left_frame, 
                                                     on_order_change=self.on_files_order_change)
        self.files_widgets["color"].pack(fill=tk.BOTH, expand=True)
        
        # Lado derecho - Configuración (optimizado)
        right_frame = ttk.LabelFrame(main_horizontal, text="⚙️ Configuración", padding="8")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Selección de tipo de conversión (compacto)
        conversion_frame = ttk.LabelFrame(right_frame, text="Tipo de Conversión", padding="5")
        conversion_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.color_conversion_type = tk.StringVar(value="bw")
        
        ttk.Radiobutton(conversion_frame, text="⚫ Blanco y Negro", 
                       variable=self.color_conversion_type, value="bw").pack(anchor=tk.W)
        ttk.Radiobutton(conversion_frame, text="🟤 Sepia", 
                       variable=self.color_conversion_type, value="sepia").pack(anchor=tk.W)
        
        # Directorio de salida (compacto)
        output_frame = ttk.LabelFrame(right_frame, text="Directorio de Salida", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.color_output_label = ttk.Label(output_frame, text="No seleccionado", 
                                           foreground="gray", wraplength=140, font=("Arial", 8))
        self.color_output_label.pack(pady=(0, 3))
        
        ttk.Button(output_frame, text="📂 Seleccionar", 
                  command=lambda: self.select_output_dir("color")).pack(fill=tk.X)
        
        # Opciones adicionales (compacto)
        options_frame = ttk.LabelFrame(right_frame, text="Opciones", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.color_delete_originals = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="🗑️ Eliminar originales", 
                       variable=self.color_delete_originals).pack(anchor=tk.W)
        
        self.color_open_output = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📂 Abrir resultado", 
                       variable=self.color_open_output).pack(anchor=tk.W)
        
        # Botón de procesamiento (prominente)
        process_frame = ttk.Frame(right_frame)
        process_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(process_frame, text="🚀 CONVERTIR COLORES", 
                  command=self.start_color_conversion,
                  style="Accent.TButton").pack(fill=tk.X, ipady=8)
        
    def create_pdf_module(self):
        """Crear módulo de unión de PDFs"""
        # Frame principal del módulo
        module_frame = ttk.Frame(self.module_content_frame)
        module_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título del módulo
        title_label = ttk.Label(module_frame, 
                               text="📄 Módulo: Unir PDFs", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Frame principal horizontal
        main_horizontal = ttk.Frame(module_frame)
        main_horizontal.pack(fill=tk.BOTH, expand=True)
        
        # Lado izquierdo - PDFs a unir (con drag & drop)
        left_frame = ttk.LabelFrame(main_horizontal, text="📄 PDFs a Unir (Arrastra para ordenar)", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Botones de archivo
        file_buttons_frame = ttk.Frame(left_frame)
        file_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_buttons_frame, text="➕ Agregar PDFs", 
                  command=lambda: self.add_files_to_module("pdf")).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_buttons_frame, text="🗑️ Limpiar", 
                  command=lambda: self.clear_files_module("pdf")).pack(side=tk.LEFT)
        
        # Widget drag & drop para PDFs
        self.files_widgets["pdf"] = DragDropListbox(left_frame, 
                                                   on_order_change=self.on_files_order_change)
        self.files_widgets["pdf"].pack(fill=tk.BOTH, expand=True)
        
        # Lado derecho - Configuración (optimizado)
        right_frame = ttk.LabelFrame(main_horizontal, text="⚙️ Configuración", padding="8")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Configuración de salida (compacto)
        output_frame = ttk.LabelFrame(right_frame, text="Archivo de Salida", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Nombre del archivo de salida
        ttk.Label(output_frame, text="Nombre:", font=("Arial", 9)).pack(anchor=tk.W)
        self.pdf_output_name = tk.StringVar(value="merged_document.pdf")
        ttk.Entry(output_frame, textvariable=self.pdf_output_name, width=18).pack(fill=tk.X, pady=(2, 3))
        
        # Directorio de salida
        self.pdf_output_label = ttk.Label(output_frame, text="No seleccionado", 
                                         foreground="gray", wraplength=140, font=("Arial", 8))
        self.pdf_output_label.pack(pady=(0, 3))
        
        ttk.Button(output_frame, text="📂 Directorio", 
                  command=lambda: self.select_output_dir("pdf")).pack(fill=tk.X)
        
        # Opciones adicionales (compacto)
        options_frame = ttk.LabelFrame(right_frame, text="Opciones", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.pdf_delete_originals = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="🗑️ Eliminar originales", 
                       variable=self.pdf_delete_originals).pack(anchor=tk.W)
        
        self.pdf_open_output = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📂 Abrir resultado", 
                       variable=self.pdf_open_output).pack(anchor=tk.W)
        
        # Información de orden (compacto)
        info_frame = ttk.LabelFrame(right_frame, text="ℹ️ Info", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 8))
        
        info_text = "Arrastra para cambiar orden de unión"
        ttk.Label(info_frame, text=info_text, wraplength=140, 
                 font=("Arial", 8), foreground="blue").pack()
        
        # Botón de procesamiento (prominente)
        process_frame = ttk.Frame(right_frame)
        process_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(process_frame, text="🔗 UNIR PDFs", 
                  command=self.start_pdf_merge,
                  style="Accent.TButton").pack(fill=tk.X, ipady=8)
        
    def create_both_module(self):
        """Crear módulo combinado (conversión + unión)"""
        # Frame principal del módulo
        module_frame = ttk.Frame(self.module_content_frame)
        module_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título del módulo
        title_label = ttk.Label(module_frame, 
                               text="🔄 Módulo: Conversión + Unión", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Frame principal horizontal
        main_horizontal = ttk.Frame(module_frame)
        main_horizontal.pack(fill=tk.BOTH, expand=True)
        
        # Lado izquierdo - Archivos
        left_frame = ttk.LabelFrame(main_horizontal, text="📁 Archivos (Imágenes y PDFs)", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Botones de archivo
        file_buttons_frame = ttk.Frame(left_frame)
        file_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_buttons_frame, text="➕ Agregar Archivos", 
                  command=lambda: self.add_files_to_module("both")).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_buttons_frame, text="🗑️ Limpiar", 
                  command=lambda: self.clear_files_module("both")).pack(side=tk.LEFT)
        
        # Widget drag & drop
        self.files_widgets["both"] = DragDropListbox(left_frame, 
                                                    on_order_change=self.on_files_order_change)
        self.files_widgets["both"].pack(fill=tk.BOTH, expand=True)
        
        # Lado derecho - Configuración (más compacto)
        right_frame = ttk.LabelFrame(main_horizontal, text="⚙️ Configuración", padding="8")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Configuración de conversión (más compacto)
        conversion_frame = ttk.LabelFrame(right_frame, text="Conversión", padding="5")
        conversion_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.both_conversion_type = tk.StringVar(value="bw")
        ttk.Radiobutton(conversion_frame, text="⚫ B&N", 
                       variable=self.both_conversion_type, value="bw").pack(anchor=tk.W)
        ttk.Radiobutton(conversion_frame, text="🟤 Sepia", 
                       variable=self.both_conversion_type, value="sepia").pack(anchor=tk.W)
        
        # Configuración de salida (más compacto)
        output_frame = ttk.LabelFrame(right_frame, text="Salida", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(output_frame, text="Nombre:", font=("Arial", 9)).pack(anchor=tk.W)
        self.both_output_name = tk.StringVar(value="converted_merged.pdf")
        ttk.Entry(output_frame, textvariable=self.both_output_name, width=18).pack(fill=tk.X, pady=(2, 3))
        
        self.both_output_label = ttk.Label(output_frame, text="No seleccionado", 
                                          foreground="gray", wraplength=140, font=("Arial", 8))
        self.both_output_label.pack(pady=(0, 3))
        
        ttk.Button(output_frame, text="📂 Directorio", 
                  command=lambda: self.select_output_dir("both")).pack(fill=tk.X)
        
        # Opciones (más compacto)
        options_frame = ttk.LabelFrame(right_frame, text="Opciones", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.both_delete_originals = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="🗑️ Eliminar originales", 
                       variable=self.both_delete_originals).pack(anchor=tk.W)
        
        self.both_delete_intermediates = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🗂️ Limpiar temporales", 
                       variable=self.both_delete_intermediates).pack(anchor=tk.W)
        
        self.both_open_output = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📂 Abrir resultado", 
                       variable=self.both_open_output).pack(anchor=tk.W)
        
        # Botón de procesamiento (MÁS PROMINENTE)
        process_frame = ttk.Frame(right_frame)
        process_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(process_frame, text="🚀 CONVERTIR + UNIR", 
                  command=self.start_both_process,
                  style="Accent.TButton").pack(fill=tk.X, ipady=8)
    
    # Métodos de manejo de archivos
    def add_files_to_module(self, module_id: str):
        """Agregar archivos a un módulo específico"""
        if module_id == "pdf":
            # Solo PDFs
            file_types = [("PDF files", "*.pdf")]
            title = "Seleccionar PDFs"
        elif module_id == "color":
            # Imágenes y PDFs
            file_types = [
                ("All supported", "*.pdf;*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif")
            ]
            title = "Seleccionar Archivos"
        else:  # both
            # Todos los tipos
            file_types = [
                ("All supported", "*.pdf;*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif")
            ]
            title = "Seleccionar Archivos"
            
        file_paths = filedialog.askopenfilenames(
            title=title,
            filetypes=file_types
        )
        
        if file_paths and module_id in self.files_widgets:
            self.files_widgets[module_id].add_files(list(file_paths))
            
    def clear_files_module(self, module_id: str):
        """Limpiar archivos de un módulo"""
        if module_id in self.files_widgets:
            self.files_widgets[module_id].clear_files()
            
    def select_output_dir(self, module_id: str):
        """Seleccionar directorio de salida para un módulo"""
        directory = filedialog.askdirectory(title="Seleccionar Directorio de Salida")
        
        if directory:
            self.output_dirs[module_id] = directory
            
            # Actualizar label correspondiente
            if module_id == "color":
                self.color_output_label.config(text=os.path.basename(directory), foreground="black")
            elif module_id == "pdf":
                self.pdf_output_label.config(text=os.path.basename(directory), foreground="black")
            elif module_id == "both":
                self.both_output_label.config(text=os.path.basename(directory), foreground="black")
                
    def on_files_order_change(self, new_order: List[str]):
        """Callback cuando cambia el orden de archivos"""
        # Aquí se puede notificar al controlador si es necesario
        pass
        
    # Métodos de procesamiento
    def start_color_conversion(self):
        """Iniciar conversión de colores"""
        if not self.files_widgets.get("color"):
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados")
            return
            
        files = self.files_widgets["color"].get_file_paths()
        if not files:
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados")
            return
            
        if "color" not in self.output_dirs:
            messagebox.showwarning("Advertencia", "Selecciona un directorio de salida")
            return
            
        # Configurar parámetros
        params = {
            "files": files,
            "output_dir": self.output_dirs["color"],
            "conversion_type": self.color_conversion_type.get(),
            "delete_originals": self.color_delete_originals.get(),
            "open_output": self.color_open_output.get()
        }
        
        if self.controller:
            self.controller.start_color_conversion_module(params)
            
    def start_pdf_merge(self):
        """Iniciar unión de PDFs"""
        if not self.files_widgets.get("pdf"):
            messagebox.showwarning("Advertencia", "No hay PDFs seleccionados")
            return
            
        files = self.files_widgets["pdf"].get_file_paths()
        if not files:
            messagebox.showwarning("Advertencia", "No hay PDFs seleccionados")
            return
            
        if "pdf" not in self.output_dirs:
            messagebox.showwarning("Advertencia", "Selecciona un directorio de salida")
            return
            
        # Validar que sean PDFs
        non_pdf_files = [f for f in files if not f.lower().endswith('.pdf')]
        if non_pdf_files:
            messagebox.showerror("Error", "Solo se pueden unir archivos PDF")
            return
            
        # Configurar parámetros
        params = {
            "files": files,
            "output_dir": self.output_dirs["pdf"],
            "output_name": self.pdf_output_name.get() or "merged_document.pdf",
            "delete_originals": self.pdf_delete_originals.get(),
            "open_output": self.pdf_open_output.get()
        }
        
        if self.controller:
            self.controller.start_pdf_merge_module(params)
            
    def start_both_process(self):
        """Iniciar proceso combinado"""
        if not self.files_widgets.get("both"):
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados")
            return
            
        files = self.files_widgets["both"].get_file_paths()
        if not files:
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados")
            return
            
        if "both" not in self.output_dirs:
            messagebox.showwarning("Advertencia", "Selecciona un directorio de salida")
            return
            
        # Configurar parámetros
        params = {
            "files": files,
            "output_dir": self.output_dirs["both"],
            "output_name": self.both_output_name.get() or "converted_merged.pdf",
            "conversion_type": self.both_conversion_type.get(),
            "delete_originals": self.both_delete_originals.get(),
            "delete_intermediates": self.both_delete_intermediates.get(),
            "open_output": self.both_open_output.get()
        }
        
        if self.controller:
            self.controller.start_both_process_module(params)
    
    # Métodos de progreso
    def update_progress(self, progress: float, status: str = ""):
        """Actualizar barra de progreso"""
        if self.progress_var:
            self.progress_var.set(progress)
        if status and self.status_label:
            self.status_label.config(text=status)
        self.root.update_idletasks()
        
    def reset_progress(self):
        """Resetear progreso"""
        if self.progress_var:
            self.progress_var.set(0)
        if self.status_label:
            self.status_label.config(text="Listo para procesar archivos")
            
    def show_completion_message(self, title: str, message: str, is_error: bool = False):
        """Mostrar mensaje de completación"""
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        
        self.reset_progress()
