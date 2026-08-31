# EPUB to Markdown (`epub_to_md`)

Herramienta ligera en Python optimizada con **[uv](https://docs.astral.sh/uv/)** para convertir libros electrónicos (`.epub`) en capítulos individuales en formato **Markdown (`.md`)**, limpios, numerados y listos para usar en Obsidian, Logseq, lectores Markdown o procesamiento con LLMs.

---

## 📋 Requisitos Previos (macOS)

Antes de empezar, valida que tengas instalados **Python 3.10+** y **uv**.

### 1. Validar Python
Abre tu terminal y ejecuta:
```bash
python3 --version
```
> Si no lo tienes instalado, puedes instalarlo con Homebrew: `brew install python` o descargarlo desde [python.org](https://www.python.org/).

### 2. Validar `uv`
Verifica si tienes `uv` instalado:
```bash
uv --version
```
Si no lo tienes instalado en tu Mac, instálalo con cualquiera de estos comandos:
```bash
# Mediante el instalador oficial de Astral:
curl -LsSf https://astral.sh/uv/install.sh | sh

# O mediante Homebrew:
brew install uv
```

---

## 🚀 Configuración del Proyecto desde Cero

Sigue estos pasos en tu terminal:

### 1. Entrar a la carpeta del proyecto
```bash
cd epub_to_md
```

### 2. Crear el entorno virtual con `uv`
```bash
uv venv
```
*(Esto creará la carpeta aislada `.venv/` en segundos).*

### 3. Activar el entorno virtual
```bash
source .venv/bin/activate
```

### 4. Instalar las dependencias
Instala las librerías necesarias con `uv pip`:
```bash
uv pip install ebooklib beautifulsoup4 markdownify
```

---

## 📂 Flujo de Trabajo y Carpetas

El proyecto cuenta con un flujo automatizado de directorios:

```text
epub_to_md/
├── entrada/                         # 📥 Coloca aquí tus archivos .epub a convertir
│   └── procesados/                  # 📦 Los .epub se mueven aquí automáticamente
├── salida/
│   └── <nombre_del_libro>/          # 📄 Capítulos generados en Markdown (.md)
├── epub_to_md.py                    # ⚙️ Script de conversión
├── .gitignore
└── README.md
```

1. **Colocar los libros**: Copia tus archivos `.epub` dentro de la carpeta `entrada/`.
2. **Procesamiento**: El script detectará todos los libros en `entrada/` (ignorando subcarpetas).
3. **Resultados**: Creará una subcarpeta dentro de `salida/` para cada libro con sus capítulos numerados (`01_introduccion.md`, `02_capitulo_1.md`, etc.).
4. **Archivo completado**: Al finalizar cada libro, moverá el `.epub` original a `entrada/procesados/`.

---

## ▶️ Ejecución

Para procesar todos los libros disponibles en `entrada/`:

```bash
uv run epub_to_md.py
```

*(O si ya tienes el entorno virtual activado con `source .venv/bin/activate`)*:
```bash
python epub_to_md.py
```

---

## ✨ Características del Convertidor

- **Línea 1 limpia**: Elimina automáticamente declaraciones residuales XML/DOCTYPE para que el encabezado del capítulo quede siempre en la primera línea.
- **Orden de lectura real (Spine)**: Extrae el contenido respetando el orden original definido por el editor del libro.
- **Formato Markdown ATX**: Encabezados limpios estilo `# Título` y `## Subtítulo`.
- **Numeración secuencial**: Nombres de archivo con prefijo de 2 dígitos (`01_...`, `02_...`) para mantener el orden exacto en cualquier gestor de archivos.
