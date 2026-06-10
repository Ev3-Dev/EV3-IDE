from PIL import Image

# Ziel-Farbe (#D4D4D4)
NEW_COLOR = (212, 212, 212)

# Wie tolerant soll "fast schwarz" sein?
TOLERANCE = 40  # höher = mehr Pixel werden ersetzt

img = Image.open("../images/code.png").convert("RGBA")
pixels = img.load()

width, height = img.size

for x in range(width):
    for y in range(height):
        r, g, b, a = pixels[x, y]

        # Nur sichtbare Pixel prüfen
        if a != 0:
            # Prüfen ob Pixel schwarz oder fast schwarz ist
            if r < TOLERANCE and g < TOLERANCE and b < TOLERANCE:
                pixels[x, y] = (*NEW_COLOR, a)

img.save("execute_code.png")
