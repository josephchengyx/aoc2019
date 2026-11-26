from PIL import Image, ImageDraw, ImageFont

if __name__ == "__main__":
    with open("day18_input.txt") as file:
        grid_map = list(map(lambda row: list(row.strip()), file.readlines()))

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (220, 50, 50)
    GREEN = (60, 180, 75)

    def colour_map(char: str) -> tuple[int, int, int]:
        if char == '.':
            return WHITE  # open
        elif char == '@' or char.islower():
            return GREEN  # key or entrance
        elif char.isupper():
            return RED    # door
        else:
            return BLACK  # wall

    map_height, map_width = len(grid_map), len(grid_map[0])
    cell_size = 20
    pad = max(2, cell_size // 5)
    line_width = max(2, cell_size // 6)
    font = ImageFont.load_default(int(cell_size * 0.8))

    img = Image.new("RGB", (map_width * cell_size, map_height * cell_size), WHITE)
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(grid_map):
        for x, char in enumerate(row):
            x0, y0 = x * cell_size, y * cell_size
            x1, y1 = x0 + cell_size - 1, y0 + cell_size - 1
            colour = colour_map(char)
            draw.rectangle([x0, y0, x1, y1], fill=colour)
            if char.islower() or char.isupper() or char == '@':
                draw.text(((x0 + x1) / 2, (y0 + y1) / 2), char, font=font, fill=WHITE, anchor="mm")

    img.save("day18_input.png")