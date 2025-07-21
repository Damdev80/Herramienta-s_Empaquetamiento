"""
View: Main Application Window
Interfaz gráfica principal de la aplicación
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from typing import List, Optional, Dict, Any, Callable

class MainView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.controller = None  # Se asignará después
        
        # Variables de interfaz
        self.files_listbox = None
        self.file_info_text = None
        self.output_label = None
        self.progress_var = None
        self.progress_bar = None
        self.status_label = None
        self.merge_option = None
        
        self.setup_window()
        self.create_widgets()
    
    def set_controller(self, controller):
        """Establecer referencia al controlador"""
        self.controller = controller
    
    def setup_window(self):
        """Configurar ventana principal"""
        self.root.title("🎨 Convertidor PDF/Imagen - MVC Edition")
        self.root.geometry("950x750")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal con scroll
        main_canvas = tk.Canvas(self.root, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear secciones
        self.create_header(main_frame)
        self.create_file_selection_section(main_frame)
        self.create_output_section(main_frame)
        self.create_color_operations_section(main_frame)
        self.create_pdf_operations_section(main_frame)
        self.create_progress_section(main_frame)
        
        # Configurar scrolling
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_header(self, parent):
        """Crear encabezado de la aplicación"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🎨 Convertidor PDF/Imagen", 
                               font=("Arial", 18, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Arquitectura MVC • Convierte colores • Une PDFs • Ejecutable", 
                                  font=("Arial", 10), foreground="gray")
        subtitle_label.pack()
    
    def create_file_selection_section(self, parent):
        """Crear sección de selección de archivos"""
        files_section = ttk.LabelFrame(parent, text="📁 Paso 1: Seleccionar Archivos", padding="15")
        files_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Botones de selección
        buttons_frame = ttk.Frame(files_section)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="📂 Seleccionar Archivos", 
                  command=self.select_files).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="➕ Agregar Más", 
                  command=self.add_more_files).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🗑️ Limpiar Lista", 
                  command=self.clear_files).pack(side=tk.LEFT)
        
        # Información de tipos soportados
        info_label = ttk.Label(files_section, 
                              text="💡 Tipos soportados: PDF, JPG, PNG, BMP, TIFF, GIF", 
                              font=("Arial", 9), foreground="blue")
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para lista y preview
        content_frame = ttk.Frame(files_section)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de archivos
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(list_frame, text="Archivos seleccionados:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.files_listbox = tk.Listbox(listbox_frame, height=8, font=("Arial", 9))
        list_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.files_listbox.yview)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Bind para mostrar información del archivo
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.files_listbox.bind('<Button-3>', self.show_file_context_menu)  # Click derecho
        
        # Panel de información del archivo
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Label(info_frame, text="Información del archivo:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.file_info_text = tk.Text(info_frame, width=30, height=8, font=("Arial", 9), 
                                     wrap=tk.WORD, state=tk.DISABLED)
        self.file_info_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    def create_output_section(self, parent):
        """Crear sección de directorio de salida"""
        output_section = ttk.LabelFrame(parent, text="📂 Paso 2: Directorio de Salida", padding="15")
        output_section.pack(fill=tk.X, pady=(0, 15))
        
        output_frame = ttk.Frame(output_section)
        output_frame.pack(fill=tk.X)
        
        ttk.Button(output_frame, text="📁 Seleccionar Carpeta de Salida", 
                  command=self.select_output_directory).pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_label = ttk.Label(output_frame, text="❌ No seleccionado", 
                                     foreground="red", font=("Arial", 9))
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_color_operations_section(self, parent):
        """Crear sección de operaciones de color"""
        color_section = ttk.LabelFrame(parent, text="🎨 Paso 3A: Operaciones de Color", padding="15")
        color_section.pack(fill=tk.X, pady=(0, 10))
        
        desc_label = ttk.Label(color_section, 
                              text="Convierte archivos a diferentes efectos de color", 
                              font=("Arial", 9), foreground="gray")
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Botones de conversión de color
        color_buttons_frame = ttk.Frame(color_section)
        color_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(color_buttons_frame, text="⚫ Convertir a Blanco y Negro", 
                  command=lambda: self.start_color_conversion("bw")).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(color_buttons_frame, text="🟤 Convertir a Sepia", 
                  command=lambda: self.start_color_conversion("sepia")).pack(side=tk.LEFT)
    
    def create_pdf_operations_section(self, parent):
        """Crear sección de operaciones PDF"""
        pdf_section = ttk.LabelFrame(parent, text="📄 Paso 3B: Operaciones de PDF", padding="15")
        pdf_section.pack(fill=tk.X, pady=(0, 15))
        
        desc_label = ttk.Label(pdf_section, 
                              text="Une múltiples archivos PDF en un solo documento", 
                              font=("Arial", 9), foreground="gray")
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Opciones de unión
        ttk.Label(pdf_section, text="Opciones de orden:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.merge_option = tk.StringVar(value="orden_seleccion")
        
        options_frame = ttk.Frame(pdf_section)
        options_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Radiobutton(options_frame, text="📋 Orden de selección", 
                       variable=self.merge_option, value="orden_seleccion").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="🔤 Orden alfabético", 
                       variable=self.merge_option, value="alfabetico").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="✏️ Orden personalizado", 
                       variable=self.merge_option, value="personalizado").pack(anchor=tk.W)
        
        ttk.Button(pdf_section, text="📄 Unir PDFs", 
                  command=self.start_pdf_merge).pack(anchor=tk.W)
    
    def create_progress_section(self, parent):
        """Crear sección de progreso"""
        progress_section = ttk.LabelFrame(parent, text="📊 Progreso", padding="15")
        progress_section.pack(fill=tk.X)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_section, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Etiqueta de estado
        self.status_label = ttk.Label(progress_section, text="✅ Listo para comenzar", 
                                     font=("Arial", 10), foreground="green")
        self.status_label.pack()
    
    # ==================== EVENT HANDLERS ====================
    
    def select_files(self):
        """Manejar selección de archivos"""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Todos los archivos soportados", "*.pdf *.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("Archivos PDF", "*.pdf"),
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if files and self.controller:
            self.controller.select_files(list(files))
    
    def add_more_files(self):
        """Manejar agregar más archivos"""
        files = filedialog.askopenfilenames(
            title="Agregar más archivos",
            filetypes=[
                ("Todos los archivos soportados", "*.pdf *.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("Archivos PDF", "*.pdf"),
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if files and self.controller:
            count = self.controller.add_files(list(files))
            if count > 0:
                messagebox.showinfo("Archivos agregados", f"Se agregaron {count} archivos nuevos.")
    
    def clear_files(self):
        """Manejar limpiar archivos"""
        if self.controller:
            self.controller.clear_files()
    
    def select_output_directory(self):
        """Manejar selección de directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory and self.controller:
            self.controller.set_output_directory(directory)
    
    def on_file_select(self, event):
        """Manejar selección de archivo en la lista"""
        selection = self.files_listbox.curselection()
        if selection and self.controller:
            idx = selection[0]
            file_info = self.controller.get_file_info(idx)
            self.show_file_info(file_info)
    
    def show_file_context_menu(self, event):
        """Mostrar menú contextual en archivo"""
        selection = self.files_listbox.curselection()
        if selection:
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="❌ Eliminar archivo", 
                                   command=lambda: self.remove_selected_file())
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def remove_selected_file(self):
        """Remover archivo seleccionado"""
        selection = self.files_listbox.curselection()
        if selection and self.controller:
            idx = selection[0]
            self.controller.remove_file(idx)
    
    def start_color_conversion(self, conversion_type: str):
        """Iniciar conversión de color"""
        if self.controller:
            self.controller.start_color_conversion(conversion_type)
    
    def start_pdf_merge(self):
        """Iniciar unión de PDFs"""
        if self.controller:
            option = self.merge_option.get()
            
            if option == "personalizado":
                # Mostrar ventana de ordenación personalizada
                from .pdf_order_view import PDFOrderView
                pdf_files = self.controller.get_pdf_files()
                
                order_view = PDFOrderView(self.root, pdf_files)
                custom_order = order_view.show()
                
                if custom_order:
                    self.controller.start_pdf_merge(option, custom_order)
            else:
                self.controller.start_pdf_merge(option)
    
    # ==================== UPDATE METHODS ====================
    
    def update_file_list(self):
        """Actualizar lista de archivos"""
        self.files_listbox.delete(0, tk.END)
        
        if self.controller:
            files = self.controller.get_selected_files()
            for file_path in files:
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
        
        # Limpiar información de archivo
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.insert(1.0, "Selecciona un archivo de la lista para ver su información")
        self.file_info_text.config(state=tk.DISABLED)
    
    def update_output_directory_display(self):
        """Actualizar visualización del directorio de salida"""
        if self.controller:
            directory = self.controller.get_output_directory()
            if directory:
                display_path = directory
                if len(display_path) > 50:
                    parts = display_path.split(os.sep)
                    display_path = "..." + os.sep + os.sep.join(parts[-3:])
                
                self.output_label.config(text=f"✅ {display_path}", foreground="green")
            else:
                self.output_label.config(text="❌ No seleccionado", foreground="red")
    
    def update_status(self):
        """Actualizar estado de la aplicación"""
        if self.controller:
            counts = self.controller.get_file_counts()
            total = counts["total"]
            
            if total == 0:
                self.status_label.config(text="📂 Selecciona archivos para comenzar", foreground="gray")
            else:
                pdf_count = counts["pdf"]
                img_count = counts["image"]
                self.status_label.config(
                    text=f"📊 {total} archivo(s): {pdf_count} PDF(s), {img_count} imagen(es)", 
                    foreground="blue"
                )
    
    def update_progress(self, value: float, status_text: str):
        """Actualizar barra de progreso"""
        self.progress_var.set(value)
        self.status_label.config(text=status_text, foreground="orange")
        self.root.update()
    
    def show_file_info(self, file_info: Optional[Dict[str, Any]]):
        """Mostrar información del archivo"""
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        
        if file_info and "error" not in file_info:
            info_text = f"📄 Nombre: {file_info['name']}\n\n"
            info_text += f"📁 Ruta: {file_info['path']}\n\n"
            info_text += f"📏 Tamaño: {file_info['size_str']}\n\n"
            info_text += f"🏷️ Tipo: {file_info['extension'].upper()}\n\n"
            
            if "pages" in file_info:
                info_text += f"📄 Páginas: {file_info['pages']}\n\n"
            elif "dimensions" in file_info:
                info_text += f"🖼️ Dimensiones: {file_info['dimensions']}\n\n"
                info_text += f"🎨 Modo: {file_info['mode']}\n\n"
            
            info_text += "✅ Listo para procesar"
        else:
            info_text = file_info.get("error", "No se pudo obtener información del archivo")
        
        self.file_info_text.insert(1.0, info_text)
        self.file_info_text.config(state=tk.DISABLED)
    
    # ==================== DIALOG METHODS ====================
    
    def show_warning(self, title: str, message: str):
        """Mostrar advertencia"""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str):
        """Mostrar error"""
        messagebox.showerror(title, message)
    
    def show_success(self, title: str, message: str):
        """Mostrar éxito"""
        messagebox.showinfo(title, message)
    
    def confirm_operation(self, title: str, message: str) -> bool:
        """Confirmar operación"""
        return messagebox.askyesno(title, message)
    
    def get_output_filename(self, default_name: str) -> Optional[str]:
        """Obtener nombre de archivo de salida"""
        return simpledialog.askstring(
            "Nombre del archivo", 
            "Nombre del archivo de salida (sin extensión):",
            initialvalue=default_name
        )
    
    def on_conversion_completed(self, successful: int, total: int, failed_files: List[str]):
        """Manejar finalización de conversión"""
        self.progress_var.set(100)
        self.status_label.config(text="✅ Conversión completada", foreground="green")
        
        # Mostrar resultado
        message = f"✅ Conversión completada!\n\n"
        message += f"📊 Estadísticas:\n"
        message += f"• Exitosos: {successful}/{total}\n"
        message += f"• Fallidos: {len(failed_files)}\n\n"
        
        if failed_files:
            message += "❌ Archivos con errores:\n"
            for failed in failed_files[:5]:
                message += f"• {failed}\n"
            if len(failed_files) > 5:
                message += f"• ... y {len(failed_files) - 5} más\n"
        
        if self.controller:
            output_dir = self.controller.get_output_directory()
            message += f"\n📁 Archivos guardados en:\n{output_dir}"
        
        if successful > 0:
            self.show_success("🎉 Completado", message)
        else:
            self.show_error("❌ Error", message)
