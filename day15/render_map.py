from PIL import Image, ImageDraw

if __name__ == "__main__":
    with open("day15_output.txt") as file:
        grid_map = file.read()

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (220, 50, 50)
    GREEN = (60, 180, 75)

    colour_map = {
        "#": BLACK,  # wall
        ".": WHITE,  # empty
        "o": RED,  # start
        "x": GREEN  # end
    }

    rows = [line.split(" ") for line in grid_map.strip().splitlines()]
    map_height, map_width = len(rows), len(rows[0])
    cell_size = 20
    pad = max(2, cell_size // 5)
    line_width = max(2, cell_size // 6)

    img = Image.new("RGB", (map_width * cell_size, map_height * cell_size), WHITE)
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            x0, y0 = x * cell_size, y * cell_size
            x1, y1 = x0 + cell_size - 1, y0 + cell_size - 1
            colour = colour_map[char]
            match char:
                case '#':
                    draw.rectangle([x0, y0, x1, y1], fill=colour)
                case 'o':
                    draw.ellipse([x0 + pad, y0 + pad, x1 - pad, y1 - pad], outline=colour, width=line_width)
                case 'x':
                    draw.line([x0 + pad, y0 + pad, x1 - pad, y1 - pad], fill=colour, width=line_width)
                    draw.line([x0 + pad, y1 - pad, x1 - pad, y0 + pad], fill=colour, width=line_width)

    img.save("day15_output.png")