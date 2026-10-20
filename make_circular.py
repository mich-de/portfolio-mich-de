from PIL import Image, ImageOps, ImageDraw

def create_circular_icon(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGBA")
        
        # Create a circular mask
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw a white circle on the mask
        # We assume the logo is centered and roughly fills the square or we want to crop controls
        # Let's assume the image is a square or we want to fit a circle in the center.
        width, height = img.size
        min_dim = min(width, height)
        
        # Calculate bounding box for the circle
        # We leave a small margin or fit exactly?
        # Let's try to fit exactly to the smaller dimension centered.
        
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        
        # Ultra-aggressive crop to hit the green
        margin = 45 
        draw.ellipse((left + margin, top + margin, right - margin, bottom - margin), fill=255)
        
        # Apply mask
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        
        output.save(output_path, "PNG")
        print(f"Saved circular crop to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_circular_icon("public/assets/icon_music_spotify_raw.png", "public/assets/icon_music_spotify_v3.png")
