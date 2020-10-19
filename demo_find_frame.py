from PIL import Image


def get_right(x, y):
    while orig_pix_map[x, y] == color:
        x += 1
    return x


def get_bottom(y):
    while orig_pix_map[x, y] == color:
        y += 1
    return y


filename = './screenshots/test_precip_p01_fhr_id_106.png'
orig_image = Image.open(filename).convert('RGB')
orig_pix_map = orig_image.load()
width, height = orig_image.size

box = []
color = (102, 102, 102)
done = False

for y in range(height):
    for x in range(width):
        if orig_pix_map[x, y] == color:
            print(x, y)
            box.append(x)
            box.append(y)
            box.append(get_right(x, y))
            box.append(get_bottom(y))
            done = True
            break
    if done:
        break

print(box)
image_box = orig_image.crop(box)
image_box.save('./screenshots/test_precip_p01_fhr_id_106_box.png')




