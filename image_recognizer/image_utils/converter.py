from PIL import Image

def convert(img):
    img = Image.open(img)
    return img.convert('RGB') 