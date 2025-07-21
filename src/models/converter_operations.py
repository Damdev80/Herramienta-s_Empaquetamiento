"""
Model: Converter Operations
Maneja las operaciones de conversión de archivos
"""
import os
import tempfile
import threading
from typing import List, Tuple, Callable, Optional, Dict, Any
from PIL import Image
import PyPDF2

# Importaciones opcionales
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ConverterOperations:
    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
        self.is_processing = False
    
    def set_callbacks(self, progress_callback: Callable, completion_callback: Callable):
        """Establecer callbacks para progreso y finalización"""
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
    
    def get_available_tools(self) -> Dict[str, bool]:
        """Obtener herramientas disponibles para conversión"""
        return {
            "pymupdf": PYMUPDF_AVAILABLE,
            "pdf2image": PDF2IMAGE_AVAILABLE,
            "reportlab": REPORTLAB_AVAILABLE
        }
    
    def convert_image_to_bw(self, image_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir imagen a blanco y negro"""
        try:
            with Image.open(image_path) as image:
                # Convertir a escala de grises
                bw_image = image.convert('L')
                bw_image.save(output_path)
                return True, "Imagen convertida exitosamente"
        except Exception as e:
            return False, f"Error convirtiendo imagen: {str(e)}"
    
    def convert_image_to_sepia(self, image_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir imagen a sepia"""
        try:
            with Image.open(image_path) as image:
                # Convertir a RGB si no lo está
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Aplicar filtro sepia
                pixels = image.load()
                width, height = image.size
                
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        
                        # Fórmula sepia
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        
                        # Asegurar que los valores estén en el rango correcto
                        tr = min(255, tr)
                        tg = min(255, tg)
                        tb = min(255, tb)
                        
                        pixels[x, y] = (tr, tg, tb)
                
                image.save(output_path)
                return True, "Imagen convertida a sepia exitosamente"
        except Exception as e:
            return False, f"Error convirtiendo imagen a sepia: {str(e)}"
    
    def convert_pdf_to_bw(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir PDF a blanco y negro usando el mejor método disponible"""
        try:
            # Método 1: PyMuPDF (más confiable)
            if PYMUPDF_AVAILABLE:
                return self._convert_pdf_with_pymupdf(pdf_path, output_path)
            
            # Método 2: pdf2image
            elif PDF2IMAGE_AVAILABLE and REPORTLAB_AVAILABLE:
                return self._convert_pdf_with_pdf2image(pdf_path, output_path)
            
            # Método 3: Copia básica
            else:
                return self._copy_pdf_basic(pdf_path, output_path)
                
        except Exception as e:
            return False, f"Error convirtiendo PDF: {str(e)}"
    
    def _convert_pdf_with_pymupdf(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir PDF usando PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convertir a escala de grises con alta calidad
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
                
                # Crear nueva página
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                
                # Insertar imagen en escala de grises
                img_data = pix.tobytes("png")
                new_page.insert_image(new_page.rect, stream=img_data)
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return True, "PDF convertido con PyMuPDF (alta calidad)"
            
        except Exception as e:
            raise Exception(f"Error con PyMuPDF: {str(e)}")
    
    def _convert_pdf_with_pdf2image(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir PDF usando pdf2image + reportlab"""
        try:
            images = convert_from_path(pdf_path, dpi=200)
            c = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter
            
            for i, image in enumerate(images):
                bw_image = image.convert('L')
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    bw_image.save(temp_file.name, format='PNG')
                    
                    # Calcular dimensiones
                    img_width, img_height = bw_image.size
                    aspect_ratio = img_width / img_height
                    
                    if aspect_ratio > (page_width / page_height):
                        new_width = page_width - 40
                        new_height = new_width / aspect_ratio
                    else:
                        new_height = page_height - 40
                        new_width = new_height * aspect_ratio
                    
                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2
                    
                    c.drawImage(temp_file.name, x, y, width=new_width, height=new_height)
                    
                    if i < len(images) - 1:
                        c.showPage()
                    
                    os.unlink(temp_file.name)
            
            c.save()
            return True, "PDF convertido con pdf2image"
            
        except Exception as e:
            raise Exception(f"Error con pdf2image: {str(e)}")
    
    def _copy_pdf_basic(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Copia básica del PDF (sin conversión real)"""
        try:
            with open(pdf_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                pdf_writer = PyPDF2.PdfWriter()
                
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            return True, "PDF copiado (conversión limitada - instala PyMuPDF para mejor calidad)"
            
        except Exception as e:
            return False, f"Error copiando PDF: {str(e)}"
    
    def convert_pdf_to_sepia(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir PDF a sepia"""
        try:
            # Método 1: PyMuPDF (mejor calidad)
            if PYMUPDF_AVAILABLE:
                return self._convert_pdf_with_pymupdf_sepia(pdf_path, output_path)
            
            # Método 2: pdf2image + reportlab
            elif PDF2IMAGE_AVAILABLE and REPORTLAB_AVAILABLE:
                return self._convert_pdf_with_pdf2image_sepia(pdf_path, output_path)
            
            # Método 3: Copia básica (sin conversión real)
            else:
                return self._copy_pdf_basic(pdf_path, output_path)
                
        except Exception as e:
            return False, f"Error convirtiendo PDF a sepia: {str(e)}"
    
    def _convert_pdf_with_pymupdf_sepia(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir PDF a sepia usando PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convertir a imagen RGB con alta calidad
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                
                # Convertir a PIL para aplicar sepia
                from io import BytesIO
                img_data = pix.tobytes("ppm")
                img = Image.open(BytesIO(img_data))
                
                # Aplicar filtro sepia
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                pixels = img.load()
                width, height = img.size
                
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        
                        # Fórmula sepia
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        
                        pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
                
                # Convertir de vuelta a bytes
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Crear nueva página
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(new_page.rect, stream=img_bytes.getvalue())
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return True, "PDF convertido a sepia con PyMuPDF (alta calidad)"
            
        except Exception as e:
            raise Exception(f"Error con PyMuPDF sepia: {str(e)}")
    
    def _convert_pdf_with_pdf2image_sepia(self, pdf_path: str, output_path: str) -> Tuple[bool, str]:
        """Convertir PDF a sepia usando pdf2image + reportlab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            images = convert_from_path(pdf_path, dpi=200)
            c = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter
            
            for i, image in enumerate(images):
                # Convertir a sepia
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                pixels = image.load()
                width, height = image.size
                
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        
                        # Fórmula sepia
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        
                        pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
                
                # Ajustar tamaño de imagen a página
                img_width, img_height = image.size
                scale = min(page_width / img_width, page_height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Centrar imagen en página
                x_offset = (page_width - new_width) / 2
                y_offset = (page_height - new_height) / 2
                
                # Guardar imagen temporalmente
                temp_path = f"temp_sepia_{i}.png"
                image.save(temp_path)
                
                # Insertar en PDF
                c.drawImage(temp_path, x_offset, y_offset, new_width, new_height)
                
                # Limpiar archivo temporal
                os.remove(temp_path)
                
                if i < len(images) - 1:
                    c.showPage()
            
            c.save()
            return True, "PDF convertido a sepia con pdf2image + reportlab"
            
        except Exception as e:
            raise Exception(f"Error con pdf2image sepia: {str(e)}")
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> Tuple[bool, str]:
        """Unir múltiples PDFs"""
        try:
            merger = PyPDF2.PdfMerger()
            
            for i, pdf_file in enumerate(pdf_files):
                if self.progress_callback:
                    progress = (i / len(pdf_files)) * 100
                    self.progress_callback(progress, f"Procesando: {os.path.basename(pdf_file)}")
                
                merger.append(pdf_file)
            
            merger.write(output_path)
            merger.close()
            
            return True, f"PDFs unidos exitosamente en: {output_path}"
            
        except Exception as e:
            return False, f"Error uniendo PDFs: {str(e)}"
    
    def convert_files_async(self, files: List[str], output_directory: str, 
                          conversion_type: str = "bw"):
        """Convertir archivos de forma asíncrona"""
        if self.is_processing:
            return
        
        self.is_processing = True
        thread = threading.Thread(
            target=self._convert_files_worker,
            args=(files, output_directory, conversion_type)
        )
        thread.daemon = True
        thread.start()
    
    def _convert_files_worker(self, files: List[str], output_directory: str, 
                            conversion_type: str):
        """Worker para conversión de archivos"""
        total_files = len(files)
        successful_conversions = 0
        failed_files = []
        
        for i, file_path in enumerate(files):
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if self.progress_callback:
                progress = (i / total_files) * 100
                self.progress_callback(progress, f"🎨 Procesando: {file_name}")
            
            try:
                if file_ext == '.pdf':
                    suffix = "_BW" if conversion_type == "bw" else "_Sepia"
                    output_path = os.path.join(output_directory, f"{file_name_without_ext}{suffix}.pdf")
                    
                    if conversion_type == "bw":
                        success, message = self.convert_pdf_to_bw(file_path, output_path)
                    else:
                        # Para sepia en PDF, usamos el método de B&N por simplicidad
                        success, message = self.convert_pdf_to_bw(file_path, output_path)
                    
                    if success:
                        successful_conversions += 1
                    else:
                        failed_files.append(f"{file_name}: {message}")
                
                else:
                    # Es una imagen
                    suffix = "_BW" if conversion_type == "bw" else "_Sepia"
                    output_path = os.path.join(output_directory, f"{file_name_without_ext}{suffix}{file_ext}")
                    
                    if conversion_type == "bw":
                        success, message = self.convert_image_to_bw(file_path, output_path)
                    else:
                        success, message = self.convert_image_to_sepia(file_path, output_path)
                    
                    if success:
                        successful_conversions += 1
                    else:
                        failed_files.append(f"{file_name}: {message}")
                        
            except Exception as e:
                failed_files.append(f"{file_name}: {str(e)}")
        
        self.is_processing = False
        
        # Callback de finalización
        if self.completion_callback:
            self.completion_callback(successful_conversions, total_files, failed_files)
    
    def image_to_pdf(self, image_path: str, output_dir: str) -> Optional[str]:
        """Convertir imagen a PDF"""
        try:
            # Generar nombre de salida
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.pdf")
            
            # Abrir imagen
            img = Image.open(image_path)
            
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Guardar como PDF
            img.save(output_path, "PDF", resolution=100.0)
            
            return output_path
            
        except Exception as e:
            print(f"Error convirtiendo imagen a PDF: {e}")
            return None
