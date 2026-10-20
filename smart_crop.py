from PIL import Image, ImageOps, ImageDraw
import sys

def smart_crop_green(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        pixels = img.load()
        
        # 1. Find the bounding box of the GREEN pixels
        # Spotify green is approx RGB(29, 185, 84). 
        # We'll be generous: Green component should be dominant and high.
        
        min_x, min_y = width, height
        max_x, max_y = 0, 0
        found_green = False
        
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                # Simple "Is Green?" heuristic: Green > Red and Green > Blue and Green > 100
                if g > r + 20 and g > b + 20 and g > 100:
                    found_green = True
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        
        if not found_green:
            print("No green pixels found! Falling back to center crop.")
            # Fallback (shouldn't happen with Spotify logo)
            return

        print(f"Green Bounding Box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        
        # 2. Crop to the bounding box of the logo
        # Add a tiny padding? No, user wants to cut TO the green.
        # Let's make it square to ensure a perfect circle
        
        box_w = max_x - min_x
        box_h = max_y - min_y
        
        # Use the larger dimension to be safe? Or average?
        # The logo is a circle, so bounding box should be roughly square.
        # If it's not square, we center it.
        
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        # Determine radius based on the SMALLER dimension to ensure we are INSIDE the green
        # User said "cut until the green starts", implies we might have some white noise outside.
        # Actually checking the bounds of green pixels ensures we HAVE the green. 
        # But if there are anti-aliased pixels outside, we might want to shrink slightly.
        
        radius = min(box_w, box_h) // 2
        
        left = center_x - radius
        top = center_y - radius
        right = center_x + radius
        bottom = center_y + radius
        
        img_cropped = img.crop((left, top, right, bottom))
        
        # 3. Apply Circular Mask to the cropped square
        mask = Image.new("L", img_cropped.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img_cropped.size[0], img_cropped.size[1]), fill=255)
        
        output = ImageOps.fit(img_cropped, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        
        output.save(output_path, "PNG")
        print(f"Saved smart crop to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    smart_crop_green("public/assets/icon_music_spotify_raw.png", "public/assets/icon_music_spotify_v6.png")
