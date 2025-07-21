"""
Widget personalizado para arrastrar y soltar con vista previa
Drag and Drop Widget with Preview functionality
"""
import tkinter as tk
from tkinter import ttk
import os
from typing import List, Callable, Optional
from PIL import Image, ImageTk
import fitz  # PyMuPDF para vista previa de PDF

class DragDropListbox(tk.Frame):
    def __init__(self, parent, on_order_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_order_change = on_order_change
        self.files = []  # Lista de archivos
        self.previews = {}  # Cache de vistas previas
        
        # Variables para drag & drop mejorado
        self.drag_data = {"item": None, "start_y": 0, "current_y": 0, "widget": None, "is_dragging": False}
        self.placeholder_frame = None  # Frame visual para mostrar dónde se va a insertar
        self.drag_threshold = 5  # Píxeles mínimos para considerar drag
        
        self.setup_widgets()
        
    def setup_widgets(self):
        """Configurar widgets del drag & drop"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de instrucciones mejorado
        instructions = ttk.Label(main_frame, 
                                text="🎯 DRAG & DROP: Arrastra archivos para cambiar orden • Vista previa disponible",
                                font=("Arial", 10, "bold"), foreground="#2E86AB")
        instructions.pack(pady=(0, 10))
        
        # Sub-instrucciones
        sub_instructions = ttk.Label(main_frame, 
                                   text="✨ Tip: Verás una línea roja donde se va a insertar el archivo",
                                   font=("Arial", 8), foreground="gray")
        sub_instructions.pack(pady=(0, 5))
        
        # Frame para la lista con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        self.canvas = tk.Canvas(list_frame, bg="white", highlightthickness=1, 
                               highlightcolor="gray", relief="sunken")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variables para drag & drop
        self.drag_data = {"item": None, "start_y": 0, "current_y": 0, "widget": None, "is_dragging": False}
        self.placeholder_frame = None
        self.drag_threshold = 5
        
        # Bind events para mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Manejar scroll con rueda del mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def add_files(self, file_paths: List[str]):
        """Agregar archivos a la lista"""
        for file_path in file_paths:
            if file_path not in [f["path"] for f in self.files]:
                self.files.append({
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "type": self._get_file_type(file_path)
                })
        
        self.refresh_display()
        
    def _get_file_type(self, file_path: str) -> str:
        """Determinar tipo de archivo"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return 'PDF'
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            return 'IMAGE'
        return 'UNKNOWN'
        
    def remove_file(self, index: int):
        """Remover archivo por índice"""
        if 0 <= index < len(self.files):
            file_path = self.files[index]["path"]
            # Limpiar cache de preview
            if file_path in self.previews:
                del self.previews[file_path]
            
            self.files.pop(index)
            self.refresh_display()
            
    def clear_files(self):
        """Limpiar todos los archivos"""
        self.files.clear()
        self.previews.clear()
        
        # Remover placeholder si existe
        self.remove_placeholder()
        
        # Limpiar widgets existentes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Resetear scroll region para eliminar espacio vacío
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        self.canvas.yview_moveto(0)  # Mover scroll al inicio
        
        # Actualizar display vacío
        self.refresh_display()
        
    def create_placeholder(self):
        """Crear placeholder visual mejorado para mostrar dónde se va a insertar"""
        if self.placeholder_frame:
            self.placeholder_frame.destroy()
            
        # Crear frame con mejor estilo visual
        self.placeholder_frame = tk.Frame(self.scrollable_frame, height=4, bg="#FF6B6B")
        
        # Agregar label indicativo
        placeholder_label = tk.Label(self.placeholder_frame, 
                                   text="📍 Insertar aquí", 
                                   bg="#FF6B6B", fg="white", 
                                   font=("Arial", 8, "bold"))
        placeholder_label.pack(pady=1)
        
    def remove_placeholder(self):
        """Eliminar placeholder visual"""
        if self.placeholder_frame:
            self.placeholder_frame.destroy()
            self.placeholder_frame = None
            
    def get_drop_position(self, y_position):
        """Calcular posición donde insertar basado en coordenada Y"""
        widgets = self.scrollable_frame.winfo_children()
        
        # Filtrar solo widgets de archivos válidos (excluir placeholder y otros)
        file_widgets = []
        for w in widgets:
            if (hasattr(w, 'index') and w != self.placeholder_frame and 
                w != self.drag_data.get("widget")):
                file_widgets.append(w)
        
        if not file_widgets:
            return 0
            
        # Ordenar widgets por su posición Y actual
        file_widgets.sort(key=lambda w: w.winfo_y())
        
        # Calcular posición basada en punto medio de cada widget
        for i, widget in enumerate(file_widgets):
            try:
                widget_top = widget.winfo_y()
                widget_height = widget.winfo_height()
                widget_bottom = widget_top + widget_height
                widget_middle = widget_top + (widget_height // 2)
                
                # Si estamos en la mitad superior del primer widget, insertar al inicio
                if i == 0 and y_position < widget_middle:
                    return 0
                
                # Si estamos entre la mitad de este widget y el siguiente
                if y_position < widget_middle:
                    return i
                    
                # Si es el último widget y estamos en su mitad inferior
                if i == len(file_widgets) - 1 and y_position >= widget_middle:
                    return len(self.files)
                    
            except Exception as e:
                print(f"Error calculando posición: {e}")
                continue
                
        # Por defecto, insertar al final
        return len(self.files)
        
    def show_placeholder_at_position(self, position):
        """Mostrar placeholder en una posición específica de manera más estable"""
        try:
            self.remove_placeholder()
            self.create_placeholder()
            
            widgets = self.scrollable_frame.winfo_children()
            
            # Filtrar widgets de archivos válidos (excluyendo placeholder y widget siendo arrastrado)
            file_widgets = []
            for w in widgets:
                if (w != self.placeholder_frame and 
                    w != self.drag_data.get("widget") and 
                    hasattr(w, 'index')):
                    file_widgets.append(w)
            
            # Ordenar por posición Y
            file_widgets.sort(key=lambda w: w.winfo_y())
            
            if position <= 0:
                # Insertar al principio
                if file_widgets:
                    self.placeholder_frame.pack(before=file_widgets[0], fill=tk.X, padx=2, pady=1)
                else:
                    self.placeholder_frame.pack(fill=tk.X, padx=2, pady=1)
            elif position >= len(file_widgets):
                # Insertar al final
                self.placeholder_frame.pack(fill=tk.X, padx=2, pady=1)
            else:
                # Insertar en posición específica
                if position < len(file_widgets):
                    self.placeholder_frame.pack(before=file_widgets[position], fill=tk.X, padx=2, pady=1)
                else:
                    self.placeholder_frame.pack(fill=tk.X, padx=2, pady=1)
                    
        except Exception as e:
            print(f"Error mostrando placeholder: {e}")
            self.remove_placeholder()
                                      
    def get_file_paths(self) -> List[str]:
        """Obtener lista ordenada de rutas de archivos"""
        file_paths = [f["path"] for f in self.files]
        print(f"📋 Orden de archivos solicitado: {[os.path.basename(path) for path in file_paths]}")
        return file_paths
        
    def refresh_display(self):
        """Actualizar la visualización de la lista con mejor UX"""
        # Remover placeholder si existe
        self.remove_placeholder()
        
        # Limpiar widgets existentes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Crear items para cada archivo o mostrar mensaje vacío
        if self.files:
            for i, file_info in enumerate(self.files):
                self.create_file_item(i, file_info)
        else:
            # Mostrar mensaje cuando no hay archivos
            self.create_empty_state()
            
        # Actualizar scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def create_empty_state(self):
        """Crear estado vacío con instrucciones"""
        empty_frame = tk.Frame(self.scrollable_frame, bg="white", relief="groove", borderwidth=2)
        empty_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icono y mensaje principal
        icon_label = tk.Label(empty_frame, text="📁", font=("Arial", 48), bg="white", fg="#DDD")
        icon_label.pack(pady=(20, 10))
        
        message_label = tk.Label(empty_frame, 
                               text="No hay archivos seleccionados", 
                               font=("Arial", 14, "bold"), bg="white", fg="#666")
        message_label.pack(pady=(0, 5))
        
        instruction_label = tk.Label(empty_frame, 
                                   text="Haz click en 'Agregar Archivos' para comenzar\nLuego podrás arrastrarlos para cambiar el orden", 
                                   font=("Arial", 10), bg="white", fg="#888", justify=tk.CENTER)
        instruction_label.pack(pady=(0, 20))
        
    def create_file_item(self, index: int, file_info: dict):
        """Crear widget para un archivo individual con mejor UX"""
        # Frame principal del item con mejor estilo
        item_frame = tk.Frame(self.scrollable_frame, relief="groove", borderwidth=1, bg="#F8F9FA")
        item_frame.pack(fill=tk.X, padx=4, pady=3)
        
        # Frame interno con mejor padding
        inner_frame = tk.Frame(item_frame, bg="#F8F9FA", padx=12, pady=8)
        inner_frame.pack(fill=tk.X)
        
        # Frame izquierdo para contenido principal
        left_frame = tk.Frame(inner_frame, bg="#F8F9FA")
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Header con número de posición y drag indicator
        header_frame = tk.Frame(left_frame, bg="#F8F9FA")
        header_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Número de posición
        position_label = tk.Label(header_frame, 
                                text=f"#{index + 1}", 
                                bg="#4CAF50", fg="white", 
                                font=("Arial", 8, "bold"),
                                padx=6, pady=2)
        position_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Indicador de drag
        drag_indicator = tk.Label(header_frame, 
                                text="⋮⋮ ARRASTRA PARA MOVER", 
                                bg="#F8F9FA", fg="#2196F3", 
                                font=("Arial", 8, "bold"))
        drag_indicator.pack(side=tk.LEFT)
        
        # Icono y nombre del archivo
        file_frame = tk.Frame(left_frame, bg="#F8F9FA")
        file_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Icono según tipo de archivo
        icon = "📄" if file_info["type"] == "PDF" else "🖼️"
        
        # Label principal con información del archivo
        info_text = f"{icon} {file_info['name']}"
        main_label = tk.Label(file_frame, text=info_text, 
                            bg="#F8F9FA", fg="#333", 
                            font=("Arial", 11, "bold"), anchor="w")
        main_label.pack(fill=tk.X)
        
        # Información adicional mejorada
        size_text = self._get_file_size_text(file_info["path"])
        detail_text = f"📊 {file_info['type']} • 💾 {size_text} • 📁 ...{file_info['path'][-30:]}"
        detail_label = tk.Label(file_frame, text=detail_text, 
                              bg="#F8F9FA", fg="#666", 
                              font=("Arial", 8), anchor="w")
        detail_label.pack(fill=tk.X)
        
        # Frame derecho para botones mejorados
        right_frame = tk.Frame(inner_frame, bg="#F8F9FA")
        right_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botón de vista previa mejorado
        preview_btn = tk.Button(right_frame, text="👁️ Ver", 
                              command=lambda: self.show_preview(file_info["path"]),
                              bg="#2196F3", fg="white", font=("Arial", 8, "bold"),
                              relief="flat", padx=8, pady=4, cursor="hand2")
        preview_btn.pack(pady=(0, 4))
        
        # Botón de eliminar mejorado
        remove_btn = tk.Button(right_frame, text="🗑️ Quitar", 
                             command=lambda: self.remove_file(index),
                             bg="#F44336", fg="white", font=("Arial", 8, "bold"),
                             relief="flat", padx=8, pady=4, cursor="hand2")
        remove_btn.pack()
        
        # Configurar drag & drop
        self.setup_drag_drop(item_frame, index)
        
        # Almacenar índice para referencia
        item_frame.index = index
        
    def _get_file_size_text(self, file_path: str) -> str:
        """Obtener texto de tamaño de archivo"""
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "? KB"
            
    def setup_drag_drop(self, widget, index):
        """Configurar eventos de drag & drop SOLO en áreas de drag"""
        
        # Función para aplicar drag SOLO a elementos que no son botones
        def bind_to_draggable_area(w):
            # Solo aplicar a widgets que NO sean botones y que NO tengan comando
            widget_class = w.__class__.__name__
            is_button = isinstance(w, (tk.Button, ttk.Button)) or 'Button' in widget_class
            
            if not is_button:
                w.bind("<Button-1>", lambda e: self.start_drag(e, index), add=True)
                w.bind("<B1-Motion>", lambda e: self.on_drag(e), add=True)
                w.bind("<ButtonRelease-1>", lambda e: self.end_drag(e), add=True)
                
                # Cambiar cursor para indicar que es draggable
                w.bind("<Enter>", lambda e: w.config(cursor="fleur"), add=True)
                w.bind("<Leave>", lambda e: w.config(cursor=""), add=True)
                
                # Aplicar recursivamente a hijos que no sean botones
                for child in w.winfo_children():
                    bind_to_draggable_area(child)
        
        bind_to_draggable_area(widget)
        widget.index = index
        
    def start_drag(self, event, index):
        """Iniciar potencial drag - NO activar hasta que se mueva suficiente"""
        self.drag_data["item"] = index
        self.drag_data["start_y"] = event.y_root
        self.drag_data["current_y"] = event.y_root
        self.drag_data["is_dragging"] = False  # NO está arrastrando todavía
        
        # Obtener el widget específico que corresponde al índice
        widgets = self.scrollable_frame.winfo_children()
        file_widgets = [w for w in widgets if hasattr(w, 'index')]
        
        # Buscar el widget con el índice correcto
        target_widget = None
        for widget in file_widgets:
            if hasattr(widget, 'index') and widget.index == index:
                target_widget = widget
                break
        
        if target_widget:
            self.drag_data["widget"] = target_widget
        else:
            # Fallback: usar posición en la lista
            if index < len(file_widgets):
                self.drag_data["widget"] = file_widgets[index]
        
        # NO aplicar efectos visuales ni print hasta que realmente se arrastre
                
    def _apply_drag_style(self, widget):
        """Aplicar estilo de drag recursivamente"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(bg="#E3F2FD")
            
            # Aplicar a hijos
            for child in widget.winfo_children():
                self._apply_drag_style(child)
        except:
            pass
        
    def on_drag(self, event):
        """Durante el movimiento - solo activar drag si se mueve lo suficiente"""
        if self.drag_data["item"] is not None:
            self.drag_data["current_y"] = event.y_root
            
            # Calcular cuánto se ha movido
            distance_moved = abs(self.drag_data["current_y"] - self.drag_data["start_y"])
            
            # Solo activar drag si se mueve más del threshold
            if not self.drag_data["is_dragging"] and distance_moved > self.drag_threshold:
                # AHORA SÍ empezar el drag real
                self.drag_data["is_dragging"] = True
                print(f"🖱️ DRAG ACTIVADO para archivo #{self.drag_data['item'] + 1}")
                
                # Aplicar efectos visuales AHORA
                if self.drag_data["widget"]:
                    try:
                        self.drag_data["widget"].configure(relief="raised", borderwidth=3, bg="#E3F2FD")
                        for child in self.drag_data["widget"].winfo_children():
                            self._apply_drag_style(child)
                    except Exception as e:
                        print(f"Error aplicando estilo drag: {e}")
            
            # Solo procesar movimiento si realmente está arrastrando
            if self.drag_data["is_dragging"]:
                try:
                    # Calcular posición relativa dentro del canvas
                    canvas_y = event.y - self.canvas.winfo_rooty() + self.canvas.canvasy(0)
                    
                    # Determinar nueva posición basada en coordenadas mejoradas
                    drop_position = self.get_drop_position(canvas_y)
                    
                    # Solo mostrar placeholder si es diferente al item actual
                    current_index = self.drag_data["item"]
                    
                    # Ajustar posición si el drop position es después del item actual
                    adjusted_position = drop_position
                    if drop_position > current_index:
                        adjusted_position = drop_position - 1
                    
                    # Mostrar placeholder solo si la posición cambió significativamente
                    if abs(adjusted_position - current_index) > 0:
                        self.show_placeholder_at_position(drop_position)
                    else:
                        self.remove_placeholder()
                        
                except Exception as e:
                    print(f"Error durante drag: {e}")
                    self.remove_placeholder()
            
    def end_drag(self, event):
        """Finalizar drag - solo procesar si realmente se arrastraba"""
        if self.drag_data["item"] is not None:
            drag_index = self.drag_data["item"]
            was_dragging = self.drag_data["is_dragging"]
            
            # Si NO estaba realmente arrastrando, solo limpiar y salir
            if not was_dragging:
                print(f"👆 Simple click en archivo #{drag_index + 1} - sin movimiento")
                # Reset drag data
                self.drag_data = {"item": None, "start_y": 0, "current_y": 0, "widget": None, "is_dragging": False}
                return
            
            print(f"🏁 Finalizando drag desde posición #{drag_index + 1}")
            
            # Restaurar estilo visual del item arrastrado
            if self.drag_data["widget"]:
                try:
                    self.drag_data["widget"].configure(relief="groove", borderwidth=1, bg="#F8F9FA")
                    
                    # Restaurar estilo de hijos
                    for child in self.drag_data["widget"].winfo_children():
                        self._restore_normal_style(child)
                        
                except Exception as e:
                    print(f"Error restaurando estilo: {e}")
            
            # Calcular posición final de manera más precisa
            try:
                canvas_y = event.y - self.canvas.winfo_rooty() + self.canvas.canvasy(0)
                drop_position = self.get_drop_position(canvas_y)
                
                print(f"📐 Posición calculada para drop: #{drop_position + 1} (desde #{drag_index + 1})")
                
                # Remover placeholder
                self.remove_placeholder()
                
                # Determinar la posición final correcta
                final_position = drop_position
                
                # Si estamos moviendo hacia abajo, ajustar
                if drop_position > drag_index:
                    final_position = drop_position - 1
                
                # Solo mover si la posición realmente cambió
                if final_position != drag_index and 0 <= final_position < len(self.files):
                    self.move_item(drag_index, final_position)
                    print(f"🔄 ¡Archivo movido! #{drag_index + 1} → #{final_position + 1}")
                    
                    # Crear lista de orden para mostrar
                    order_list = []
                    for i, f in enumerate(self.files):
                        order_list.append(f"#{i+1} {os.path.basename(f['path'])}")
                    print(f"📋 Nuevo orden: {order_list}")
                    
                    # Mostrar mensaje visual de éxito
                    self._show_move_success(drag_index, final_position)
                else:
                    print(f"❌ Sin movimiento: se mantiene en posición #{drag_index + 1}")
                    
            except Exception as e:
                print(f"Error en end_drag: {e}")
                self.remove_placeholder()
            
        # Reset drag data
        self.drag_data = {"item": None, "start_y": 0, "current_y": 0, "widget": None, "is_dragging": False}
        
    def _restore_normal_style(self, widget):
        """Restaurar estilo normal recursivamente"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(bg="#F8F9FA")
            
            # Restaurar hijos
            for child in widget.winfo_children():
                self._restore_normal_style(child)
        except:
            pass
            
    def _show_move_success(self, from_pos, to_pos):
        """Mostrar feedback visual de movimiento exitoso"""
        try:
            # Crear mensaje temporal
            success_label = tk.Label(self.scrollable_frame, 
                                   text=f"✅ Movido: #{from_pos + 1} → #{to_pos + 1}", 
                                   bg="#4CAF50", fg="white", 
                                   font=("Arial", 9, "bold"),
                                   padx=10, pady=5)
            success_label.pack(pady=5)
            
            # Remover después de 2 segundos
            self.after(2000, success_label.destroy)
        except:
            pass
        
    def move_item(self, from_index: int, to_index: int):
        """Mover item de una posición a otra"""
        if 0 <= from_index < len(self.files) and 0 <= to_index < len(self.files):
            # Mover el item
            item = self.files.pop(from_index)
            self.files.insert(to_index, item)
            
            # Refrescar display
            self.refresh_display()
            
            # Notificar cambio de orden
            if self.on_order_change:
                self.on_order_change(self.get_file_paths())
                
    def show_preview(self, file_path: str):
        """Mostrar vista previa del archivo"""
        try:
            # Crear ventana de preview
            preview_window = tk.Toplevel(self)
            preview_window.title(f"Vista Previa - {os.path.basename(file_path)}")
            preview_window.geometry("600x700")
            preview_window.resizable(True, True)
            
            # Frame principal
            main_frame = ttk.Frame(preview_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Información del archivo
            info_text = f"📄 {os.path.basename(file_path)}\n📁 {os.path.dirname(file_path)}"
            info_label = ttk.Label(main_frame, text=info_text, font=("Arial", 10))
            info_label.pack(pady=(0, 10))
            
            # Canvas para la imagen
            canvas = tk.Canvas(main_frame, bg="white", relief="sunken", borderwidth=2)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Generar y mostrar preview
            self.generate_preview(file_path, canvas)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo mostrar la vista previa:\n{str(e)}")
            
    def generate_preview(self, file_path: str, canvas: tk.Canvas):
        """Generar vista previa de archivo"""
        try:
            # Verificar si ya está en cache
            if file_path in self.previews:
                self.display_preview_image(canvas, self.previews[file_path])
                return
                
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                # Vista previa de PDF (primera página)
                doc = fitz.open(file_path)
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # 150% zoom
                img_data = pix.tobytes("ppm")
                
                # Convertir a PIL Image
                from io import BytesIO
                img = Image.open(BytesIO(img_data))
                doc.close()
                
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
                # Vista previa de imagen
                img = Image.open(file_path)
                
            else:
                # Tipo no soportado
                canvas.create_text(300, 300, text="Vista previa no disponible", 
                                 font=("Arial", 14), fill="gray")
                return
                
            # Redimensionar imagen para ajustar al canvas
            canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 500
            canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 400
            
            img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Guardar en cache
            self.previews[file_path] = photo
            
            # Mostrar en canvas
            self.display_preview_image(canvas, photo)
            
        except Exception as e:
            canvas.create_text(300, 300, text=f"Error al generar vista previa:\n{str(e)}", 
                             font=("Arial", 12), fill="red")
            
    def display_preview_image(self, canvas: tk.Canvas, photo: ImageTk.PhotoImage):
        """Mostrar imagen en canvas"""
        canvas.delete("all")
        
        # Calcular posición centrada
        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 500
        canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 400
        
        x = canvas_width // 2
        y = canvas_height // 2
        
        canvas.create_image(x, y, image=photo)
        
        # Mantener referencia para evitar garbage collection
        canvas.image = photo
