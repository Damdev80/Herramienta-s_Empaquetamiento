"""
View: PDF Order Dialog
Ventana para ordenar PDFs de forma personalizada
"""
import tkinter as tk
from tkinter import ttk
import os
from typing import List, Optional

class PDFOrderView:
    def __init__(self, parent: tk.Tk, pdf_files: List[str]):
        self.parent = parent
        self.pdf_files = pdf_files.copy()
        self.result = None
        self.window = None
        
        # Widgets
        self.listbox = None
        self.info_text = None
    
    def show(self) -> Optional[List[str]]:
        """Mostrar ventana de ordenación y retornar resultado"""
        self.create_window()
        self.window.wait_window()
        return self.result
    
    def create_window(self):
        """Crear ventana de ordenación"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📄 Ordenar PDFs")
        self.window.geometry("650x550")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.configure(bg='#f0f0f0')
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="📄 Ordenar PDFs", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Instrucciones
        instructions = ttk.Label(main_frame, 
                                text="Selecciona un archivo y usa los botones para cambiar su posición.\n"
                                     "El orden de arriba hacia abajo será el orden en el PDF final.",
                                font=("Arial", 9), foreground="gray")
        instructions.pack(pady=(0, 15))
        
        # Frame para contenido
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de archivos
        self.create_file_list(content_frame)
        
        # Panel de controles
        self.create_controls_panel(content_frame)
        
        # Botones finales
        self.create_action_buttons(main_frame)
        
        # Mostrar información del primer archivo
        if self.pdf_files:
            self.listbox.selection_set(0)
            self.show_file_info(None)
    
    def create_file_list(self, parent):
        """Crear lista de archivos"""
        list_frame = ttk.Frame(parent)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        ttk.Label(list_frame, text="📋 Orden actual:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(listbox_frame, height=18, font=("Arial", 9))
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # Llenar lista
        self.refresh_list()
        
        # Bind eventos
        self.listbox.bind('<<ListboxSelect>>', self.show_file_info)
    
    def create_controls_panel(self, parent):
        """Crear panel de controles"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(controls_frame, text="🔧 Controles:", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        # Botones de movimiento
        move_frame = ttk.LabelFrame(controls_frame, text="Mover archivo", padding="10")
        move_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(move_frame, text="⬆️ Subir", command=self.move_up).pack(fill=tk.X, pady=2)
        ttk.Button(move_frame, text="⬇️ Bajar", command=self.move_down).pack(fill=tk.X, pady=2)
        ttk.Button(move_frame, text="⤴️ Al inicio", command=self.move_to_top).pack(fill=tk.X, pady=2)
        ttk.Button(move_frame, text="⤵️ Al final", command=self.move_to_bottom).pack(fill=tk.X, pady=2)
        
        # Información del archivo
        info_frame = ttk.LabelFrame(controls_frame, text="Información", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.info_text = tk.Text(info_frame, width=28, height=12, font=("Arial", 8), 
                               wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="✅ Confirmar Orden", 
                  command=self.confirm_order).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self.cancel_order).pack(side=tk.RIGHT)
        
        # Contador de archivos
        count_label = ttk.Label(button_frame, text=f"Total: {len(self.pdf_files)} archivos", 
                               font=("Arial", 9), foreground="gray")
        count_label.pack(side=tk.LEFT)
    
    def refresh_list(self):
        """Refrescar lista de archivos"""
        self.listbox.delete(0, tk.END)
        for i, pdf_file in enumerate(self.pdf_files):
            self.listbox.insert(tk.END, f"{i+1}. {os.path.basename(pdf_file)}")
    
    def get_selected_index(self) -> Optional[int]:
        """Obtener índice seleccionado"""
        selection = self.listbox.curselection()
        return selection[0] if selection else None
    
    def move_up(self):
        """Mover archivo hacia arriba"""
        idx = self.get_selected_index()
        if idx is not None and idx > 0:
            # Intercambiar archivos
            self.pdf_files[idx], self.pdf_files[idx - 1] = self.pdf_files[idx - 1], self.pdf_files[idx]
            
            # Refrescar lista y mantener selección
            self.refresh_list()
            self.listbox.selection_set(idx - 1)
            self.show_file_info(None)
    
    def move_down(self):
        """Mover archivo hacia abajo"""
        idx = self.get_selected_index()
        if idx is not None and idx < len(self.pdf_files) - 1:
            # Intercambiar archivos
            self.pdf_files[idx], self.pdf_files[idx + 1] = self.pdf_files[idx + 1], self.pdf_files[idx]
            
            # Refrescar lista y mantener selección
            self.refresh_list()
            self.listbox.selection_set(idx + 1)
            self.show_file_info(None)
    
    def move_to_top(self):
        """Mover archivo al inicio"""
        idx = self.get_selected_index()
        if idx is not None and idx > 0:
            # Mover archivo al inicio
            file_to_move = self.pdf_files.pop(idx)
            self.pdf_files.insert(0, file_to_move)
            
            # Refrescar lista y mantener selección
            self.refresh_list()
            self.listbox.selection_set(0)
            self.show_file_info(None)
    
    def move_to_bottom(self):
        """Mover archivo al final"""
        idx = self.get_selected_index()
        if idx is not None and idx < len(self.pdf_files) - 1:
            # Mover archivo al final
            file_to_move = self.pdf_files.pop(idx)
            self.pdf_files.append(file_to_move)
            
            # Refrescar lista y mantener selección
            self.refresh_list()
            self.listbox.selection_set(len(self.pdf_files) - 1)
            self.show_file_info(None)
    
    def show_file_info(self, event):
        """Mostrar información del archivo seleccionado"""
        idx = self.get_selected_index()
        if idx is not None and idx < len(self.pdf_files):
            file_path = self.pdf_files[idx]
            file_name = os.path.basename(file_path)
            
            try:
                file_size = os.path.getsize(file_path)
                if file_size < 1024*1024:
                    size_str = f"{file_size/1024:.1f} KB"
                else:
                    size_str = f"{file_size/(1024*1024):.1f} MB"
                
                # Información del PDF
                pages_info = "Desconocido"
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        pages_info = str(len(pdf_reader.pages))
                except:
                    pass
                
                info_text = f"📄 Archivo:\n{file_name}\n\n"
                info_text += f"📏 Tamaño:\n{size_str}\n\n"
                info_text += f"📄 Páginas:\n{pages_info}\n\n"
                info_text += f"📍 Posición:\n{idx+1} de {len(self.pdf_files)}\n\n"
                info_text += f"📁 Ruta:\n{file_path}"
                
            except Exception as e:
                info_text = f"❌ Error al leer archivo:\n{str(e)}"
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)
    
    def confirm_order(self):
        """Confirmar orden actual"""
        self.result = self.pdf_files.copy()
        self.window.destroy()
    
    def cancel_order(self):
        """Cancelar ordenación"""
        self.result = None
        self.window.destroy()
