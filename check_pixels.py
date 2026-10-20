from PIL import Image
try:
    img = Image.open("public/assets/icon_music_spotify_raw.png")
    rgb_img = img.convert("RGB")
    print(f"Top-left pixel: {rgb_img.getpixel((0,0))}")
    print(f"Top-right pixel: {rgb_img.getpixel((img.width-1, 0))}")
except Exception as e:
    print(e)
