import random
from PIL import Image
from data.config import X, Y

perfect_map = Image.open("utils/perfect_map.png")
current_map = Image.open("utils/map.png")
pixels = {}

async def coordinates_to_position(x, y, width=1000):
    return y * width + x + 1


async def position_to_coordinates(position, width = 1000):
    x = (position - 1) % width
    y = (position - 1) // width
    return x, y


async def get_need_pixels():
    pixels = {}
    for x in X:
        for y in Y:
            need_pixel = perfect_map.getpixel((x, y))
            current_pixel = current_map.getpixel((x, y))
            if current_pixel != need_pixel:
                hex_color = '#{:02x}{:02x}{:02x}'.format(need_pixel[0], need_pixel[1], need_pixel[2]).upper()
                pixels[await coordinates_to_position(x,y)] = hex_color

    return pixels
