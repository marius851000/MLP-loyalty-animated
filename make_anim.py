from PIL import Image, ImageOps
from math import floor, sqrt
import os
import sys

arg = sys.argv
if len(arg) != 6:
    print("format: make_anim.py <frame rate> <source folder> <out folder> <x size> <y size>")

frame_rate = int(sys.argv[1])
source_folder = sys.argv[2]
out_folder = sys.argv[3]
resolution = (int(sys.argv[4]), int(sys.argv[5]))

def apply_radient(img, center, center_color, extern_color, radius):
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            dist_from_center = sqrt((center[0]-x) ** 2 + (center[1]-y) ** 2)
            progress = dist_from_center / radius

            r = center_color[0] + (extern_color[0] - center_color[0]) * progress
            g = center_color[1] + (extern_color[1] - center_color[1]) * progress
            b = center_color[2] + (extern_color[2] - center_color[2]) * progress

            img.putpixel((x, y), (int(r), int(g), int(b)))

class MLPWallpaperAnim:
    def __init__(self, images, resolution= (1000, 1000), fps = 120, fall_per_element = 100, second_per_element=1, scale=1, out_dir="tmp"):
        self.fps = fps
        self.spf = 1/fps
        self.fall_per_element = fall_per_element * scale
        self.element_per_second = 1/second_per_element
        self.fall_per_second = self.fall_per_element * self.element_per_second
        self.fall_per_frame = self.fall_per_second/fps
        self.second_per_element = second_per_element
        self.images = []
        self.resolution = resolution
        self.out_dir = out_dir
        page_center = self.resolution[0]/2
        for image_path in images:
            img = Image.open(image_path)
            if img == None:
                print("failed to load {}".format(image_path))
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    actual_pixel = img.getpixel((x, y))
                    if actual_pixel[3] < 20:
                        img.putpixel((x, y), (0, 0, 0, 0))
            image_center = img.width/2*scale
            self.images.append([ImageOps.scale(img, scale), int(page_center-image_center)])

        self.base_image = Image.new('RGBA', self.resolution, color="black")
        apply_radient(self.base_image, (self.resolution[0]/2, self.resolution[1]*1.5), (47, 0, 15), (0, 10, 39), self.resolution[0]*1.5)


    def render_frame(self, frame_id):
        final = self.base_image.copy()
        time_spend = self.spf*frame_id
        image_count = floor(time_spend*self.element_per_second)

        second_since_last_element = time_spend-image_count * self.second_per_element
        for image_id in range(20, -1, -1):
            element_passed = image_id + second_since_last_element/self.second_per_element

            image = self.get_image(image_count-image_id)
            y_change = int(self.fall_per_element * floor(element_passed)) + int(self.fall_per_element * (element_passed%1))

            color = (int(216+8*element_passed), int(23+36*element_passed), int(86+27*element_passed))
            coloured_image = Image.new('RGB', image[0].size, color = color)

            final.paste(coloured_image, (image[1], y_change), image[0])

        first_image = self.get_image(image_count)

        final.paste(first_image[0], (image[1], 0), first_image[0])

        final.save(os.path.join(self.out_dir, "{0:05d}.png".format(frame_id)))


    def get_image(self, image_nb):
        return self.images[image_nb % len(self.images)]


    def loop_lenght(self):
        pass

images = []
image_base = os.listdir(source_folder)
image_base.sort()
for image in image_base:
    images.append(os.path.join(source_folder, image))

a = MLPWallpaperAnim(images, scale=resolution[1]/768*0.42, fps=frame_rate, resolution=resolution, out_dir=out_folder)

for loop in range(int(frame_rate*8)):
    a.render_frame(loop)


# color used in source:
#216, 23, 86
#226, 59, 113
#233, 96, 140
