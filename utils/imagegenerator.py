from PIL import Image, ImageDraw, ImageFont
import math
import string
import random
import os 

class ImageGenerator():
    def __init__(self):
        pass

    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def get_random_color_pair(self):
        color_pairs = [
            ((255, 204, 204), (204, 102, 102)),  # Light Red to Dark Red
            ((204, 255, 204), (102, 204, 102)),  # Light Green to Dark Green
            ((204, 204, 255), (102, 102, 204)),  # Light Blue to Dark Blue
            ((255, 255, 204), (204, 204, 102)),  # Light Yellow to Dark Yellow
            ((255, 204, 255), (204, 102, 204)),  # Light Magenta to Dark Magenta
            ((204, 255, 255), (102, 204, 204)),  # Light Cyan to Dark Cyan
            ((255, 240, 204), (204, 180, 102)),  # Light Cream to Dark Cream
            ((255, 223, 204), (204, 153, 102)),  # Light Peach to Dark Peach
            ((240, 255, 204), (180, 204, 102)),  # Light Lime to Dark Lime
            ((204, 204, 180), (102, 102, 90)),    # Light Olive to Dark Olive
            ((255, 219, 204), (204, 146, 102)),  # Light Salmon to Dark Salmon
            ((204, 220, 255), (102, 110, 204)),  # Light Sky Blue to Dark Sky Blue
            ((255, 228, 204), (204, 143, 102)),  # Light Coral to Dark Coral
            ((255, 228, 228), (204, 143, 143)),  # Light Pink to Dark Pink
            ((204, 240, 204), (102, 204, 102)),  # Light Mint to Dark Mint
            ((204, 204, 204), (102, 102, 102)),  # Light Gray to Dark Gray
            ((204, 255, 204), (102, 204, 153)),  # Light Grass to Dark Grass
            ((255, 204, 230), (204, 102, 204)),  # Light Lavender to Dark Lavender
            ((204, 204, 255), (153, 153, 204)),  # Light Periwinkle to Dark Periwinkle
            ((255, 245, 204), (204, 204, 153))   # Light Butter to Dark Butter
        ]
        return random.choice(color_pairs)

    def generate_radial_gradient_square_with_text(self, gradient1, gradient2, text, text_color, text_font_path, size=500):
        img = Image.new("RGB", (size, size))

        center_x = size // 2
        center_y = size // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)

        for y in range(size):
            for x in range(size):
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                f = distance / max_distance
                r = int(gradient1[0] * (1 - f) + gradient2[0] * f)
                g = int(gradient1[1] * (1 - f) + gradient2[1] * f)
                b = int(gradient1[2] * (1 - f) + gradient2[2] * f)
                img.putpixel((x, y), (r, g, b))

        draw = ImageDraw.Draw(img)

        lines = text.split('\n')

        font_size = 1
        font = ImageFont.truetype(text_font_path, font_size)
        longest_line_width = max(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] for line in lines)

        while longest_line_width < size * 0.9 and font_size < size // 10:
            font_size += 1
            font = ImageFont.truetype(text_font_path, font_size)
            longest_line_width = max(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] for line in lines)

        total_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
        
        position_y = (size - total_height) // 2

        for line in lines:
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            position_x = (size - text_width) // 2
            draw.text((position_x, position_y), line, fill=text_color, font=font)
            position_y += text_bbox[3] - text_bbox[1]

        random_filename = self.generate_random_string() + "_text_image.png"
        img.save(random_filename)
        return random_filename

    def generate_facebook_text_post(self, text):
        random_color_pair = self.get_random_color_pair()
        file = self.generate_radial_gradient_square_with_text(
            random_color_pair[0], 
            random_color_pair[1], 
            text, 
            "black", 
            "Roboto-Black.ttf"
        )
        return file

imgen = ImageGenerator()