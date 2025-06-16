import pytesseract
from PIL import Image

# Ruta de la imagen de ejemplo
img_path = 'data/sample_cards/empleado_1.png'

try:
    img = Image.open(img_path)
    texto = pytesseract.image_to_string(img, lang='spa')
    print('Texto extraído:')
    print('-' * 40)
    print(texto)
    print('-' * 40)
except Exception as e:
    print(f'Error al ejecutar OCR: {e}') 