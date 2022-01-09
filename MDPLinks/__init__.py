"""Top-level package for MDPLinks"""
# mdplinks/__init__.py

__app_name__ = "mdplinks"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    TAG_ERROR
) = range(8)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "Error al leer la BD",
    DB_WRITE_ERROR: "Error al escribir en la BD",
    ID_ERROR: "Link no encontrado con el URL especificado",
    TAG_ERROR: "Etiquetas contienen uno o más signos de puntuación o espacios"
}