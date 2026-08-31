import os
import re
import shutil
import warnings
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, Comment, ProcessingInstruction, Declaration, Doctype
from markdownify import markdownify as md

# Ignorar advertencias menores de ebooklib
warnings.filterwarnings('ignore')

CARPETA_ENTRADA = "entrada"
CARPETA_PROCESADOS = os.path.join(CARPETA_ENTRADA, "procesados")
CARPETA_SALIDA = "salida"

def limpiar_nombre(texto, max_chars=45):
    """Limpia el texto para usarlo como nombre de archivo o carpeta seguro."""
    texto = re.sub(r'[^\w\s-]', '', texto).strip().lower()
    texto = re.sub(r'[-\s]+', '_', texto)
    return texto[:max_chars] if texto else "seccion"

def limpiar_html_y_convertir_a_md(contenido_html):
    """Limpia elementos innecesarios (XML, doctype, scripts) y convierte a Markdown."""
    # Eliminar declaraciones XML iniciales directas en texto si las hay
    contenido_html = re.sub(r'^\s*<\?xml[^>]*\?>', '', contenido_html, flags=re.IGNORECASE)
    
    soup = BeautifulSoup(contenido_html, 'html.parser')

    # Eliminar scripts, estilos, comentarios, doctypes e instrucciones de procesamiento
    for element in soup.find_all(['script', 'style']):
        element.decompose()

    for item in soup.find_all(text=lambda text: isinstance(text, (Comment, ProcessingInstruction, Declaration, Doctype))):
        item.extract()

    # Si existe la etiqueta <body>, trabajar sobre su contenido directamente
    contenido_a_procesar = soup.body if soup.body else soup

    # Convertir a Markdown con encabezados ATX (# Titulo)
    texto_md = md(str(contenido_a_procesar), heading_style="atx")

    # Limpiar cualquier resto de 'xml version=...' o doctype residual al inicio
    texto_md = re.sub(r'^(?:<\?xml[^\n]*\?>|xml\s+version=[^\n]*\??)\s*', '', texto_md, flags=re.IGNORECASE)

    # Limpiar saltos de línea múltiples repetitivos
    texto_md = re.sub(r'\n{3,}', '\n\n', texto_md).strip()

    return texto_md

def convertir_epub_a_md(ruta_epub, carpeta_salida):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida, exist_ok=True)

    print(f"\n📖 Abriendo: {os.path.basename(ruta_epub)}...")
    libro = epub.read_epub(ruta_epub)

    # 1. Obtener el orden de lectura real (spine)
    spine_ids = [item_id for item_id, linear in libro.spine if linear != 'no']
    
    # 2. Mapear documentos por su ID
    documentos = {item.id: item for item in libro.get_items_of_type(ebooklib.ITEM_DOCUMENT)}

    numero_capitulo = 1

    for item_id in spine_ids:
        item = documentos.get(item_id)
        if not item:
            continue

        contenido_html = item.get_content().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(contenido_html, 'html.parser')

        # Omitir archivos sin texto suficiente (portadas solo imagen o saltos vacíos)
        texto_plano = soup.get_text().strip()
        if not texto_plano or len(texto_plano) < 80:
            continue

        # Intentar detectar el título del capítulo (del primer h1, h2, h3 o title)
        titulo = None
        for tag in ['h1', 'h2', 'h3', 'title']:
            encabezado = soup.find(tag)
            if encabezado and encabezado.get_text().strip():
                titulo = encabezado.get_text().strip()
                break

        if not titulo:
            titulo = f"capitulo_{numero_capitulo:02d}"

        # 3. Limpiar y convertir a Markdown asegurando inicio en línea 1
        texto_md = limpiar_html_y_convertir_a_md(contenido_html)

        # 4. Guardar archivo con numeración para preservar orden
        nombre_archivo = f"{numero_capitulo:02d}_{limpiar_nombre(titulo)}.md"
        ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)

        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(texto_md + '\n')

        print(f"  ✓ Generado: {nombre_archivo}")
        numero_capitulo += 1

    total_capitulos = numero_capitulo - 1
    print(f"✅ Conversión completa: {total_capitulos} capítulos guardados en '{carpeta_salida}/'")
    return total_capitulos

def procesar_carpeta_entrada():
    # Crear estructura de carpetas si no existen
    os.makedirs(CARPETA_ENTRADA, exist_ok=True)
    os.makedirs(CARPETA_PROCESADOS, exist_ok=True)
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    # Buscar archivos .epub directamente en 'entrada/' (omitiendo subcarpetas como 'procesados/')
    archivos_epub = [
        f for f in os.listdir(CARPETA_ENTRADA)
        if os.path.isfile(os.path.join(CARPETA_ENTRADA, f)) and f.lower().endswith('.epub')
    ]

    if not archivos_epub:
        print(f"ℹ️  No hay archivos .epub en la carpeta '{CARPETA_ENTRADA}/'.")
        print(f"👉 Coloca tus archivos .epub en '{CARPETA_ENTRADA}/' y vuelve a ejecutar el script.")
        return

    print(f"🚀 Se encontraron {len(archivos_epub)} libro(s) para procesar en '{CARPETA_ENTRADA}/'.")

    for archivo in archivos_epub:
        ruta_origen = os.path.join(CARPETA_ENTRADA, archivo)
        nombre_base, _ = os.path.splitext(archivo)
        
        # Crear subcarpeta en salida para este libro
        carpeta_destino_libro = os.path.join(CARPETA_SALIDA, limpiar_nombre(nombre_base, max_chars=60))
        
        try:
            convertir_epub_a_md(ruta_origen, carpeta_destino_libro)
            
            # Mover archivo a 'entrada/procesados/'
            ruta_destino_procesado = os.path.join(CARPETA_PROCESADOS, archivo)
            
            # Si ya existe en procesados, reemplazarlo o renombrarlo
            if os.path.exists(ruta_destino_procesado):
                os.remove(ruta_destino_procesado)
                
            shutil.move(ruta_origen, ruta_destino_procesado)
            print(f"📦 Archivo movido a: {ruta_destino_procesado}\n")
        except Exception as e:
            print(f"❌ Error al procesar '{archivo}': {e}\n")

if __name__ == "__main__":
    procesar_carpeta_entrada()