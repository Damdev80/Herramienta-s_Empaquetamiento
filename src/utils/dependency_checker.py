"""
Utilities: Dependency Checker
Verifica las dependencias disponibles del sistema
"""
import sys
import importlib
from typing import Dict, List, Tuple

class DependencyChecker:
    def __init__(self):
        self.dependencies = {
            "tkinter": {"required": True, "description": "Interfaz gráfica"},
            "PIL": {"required": True, "description": "Procesamiento de imágenes", "package": "Pillow"},
            "PyPDF2": {"required": True, "description": "Manipulación de PDFs"},
            "reportlab": {"required": True, "description": "Generación de PDFs"},
            "pdf2image": {"required": False, "description": "Conversión PDF a imagen"},
            "fitz": {"required": False, "description": "PyMuPDF - Conversión PDF avanzada", "package": "PyMuPDF"},
            "threading": {"required": True, "description": "Multihilo (built-in)"}
        }
    
    def check_all_dependencies(self) -> Dict[str, Dict]:
        """Verificar todas las dependencias"""
        results = {}
        
        for module_name, info in self.dependencies.items():
            results[module_name] = self.check_dependency(module_name, info)
        
        return results
    
    def check_dependency(self, module_name: str, info: Dict) -> Dict:
        """Verificar una dependencia específica"""
        result = {
            "available": False,
            "version": None,
            "error": None,
            "required": info["required"],
            "description": info["description"],
            "package": info.get("package", module_name)
        }
        
        try:
            module = importlib.import_module(module_name)
            result["available"] = True
            
            # Intentar obtener versión
            if hasattr(module, "__version__"):
                result["version"] = module.__version__
            elif hasattr(module, "version"):
                result["version"] = module.version
            
        except ImportError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = f"Error inesperado: {str(e)}"
        
        return result
    
    def get_missing_required(self, results: Dict[str, Dict]) -> List[str]:
        """Obtener dependencias requeridas faltantes"""
        missing = []
        for module_name, result in results.items():
            if result["required"] and not result["available"]:
                missing.append(result["package"])
        return missing
    
    def get_missing_optional(self, results: Dict[str, Dict]) -> List[str]:
        """Obtener dependencias opcionales faltantes"""
        missing = []
        for module_name, result in results.items():
            if not result["required"] and not result["available"]:
                missing.append(result["package"])
        return missing
    
    def generate_report(self, results: Dict[str, Dict]) -> str:
        """Generar reporte de dependencias"""
        report = "🔍 REPORTE DE DEPENDENCIAS\n"
        report += "=" * 50 + "\n\n"
        
        # Dependencias requeridas
        report += "📋 DEPENDENCIAS REQUERIDAS:\n"
        for module_name, result in results.items():
            if result["required"]:
                status = "✅" if result["available"] else "❌"
                version = f" (v{result['version']})" if result["version"] else ""
                report += f"{status} {result['package']}{version} - {result['description']}\n"
                if result["error"]:
                    report += f"   Error: {result['error']}\n"
        
        report += "\n"
        
        # Dependencias opcionales
        report += "🔧 DEPENDENCIAS OPCIONALES:\n"
        for module_name, result in results.items():
            if not result["required"]:
                status = "✅" if result["available"] else "⚠️"
                version = f" (v{result['version']})" if result["version"] else ""
                report += f"{status} {result['package']}{version} - {result['description']}\n"
                if result["error"]:
                    report += f"   Error: {result['error']}\n"
        
        report += "\n"
        
        # Resumen
        missing_required = self.get_missing_required(results)
        missing_optional = self.get_missing_optional(results)
        
        if missing_required:
            report += "❌ DEPENDENCIAS REQUERIDAS FALTANTES:\n"
            for package in missing_required:
                report += f"   • {package}\n"
            report += "\n💡 Instala con: pip install " + " ".join(missing_required) + "\n\n"
        
        if missing_optional:
            report += "⚠️ DEPENDENCIAS OPCIONALES FALTANTES:\n"
            for package in missing_optional:
                report += f"   • {package}\n"
            report += "\n💡 Para mejor rendimiento: pip install " + " ".join(missing_optional) + "\n\n"
        
        if not missing_required and not missing_optional:
            report += "🎉 ¡Todas las dependencias están instaladas!\n\n"
        elif not missing_required:
            report += "✅ Todas las dependencias requeridas están disponibles.\n"
            report += "⚠️ Algunas funciones opcionales pueden no estar disponibles.\n\n"
        
        report += f"🐍 Python {sys.version}\n"
        report += f"💻 Plataforma: {sys.platform}\n"
        
        return report
    
    def check_and_show_report(self) -> Tuple[bool, str]:
        """Verificar dependencias y generar reporte"""
        results = self.check_all_dependencies()
        report = self.generate_report(results)
        
        missing_required = self.get_missing_required(results)
        can_run = len(missing_required) == 0
        
        return can_run, report
