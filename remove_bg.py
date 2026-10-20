
from PIL import Image
import sys

def remove_background(image_path, output_path=None, tolerance=30):
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        width, height = img.size
        
        # Get background color from top-left pixel
        bg_pixel = img.getpixel((0, 0))
        
        # Tolerance check function
        def is_similar(p1, p2, tol):
            return all(abs(p1[i] - p2[i]) <= tol for i in range(3))
            
        # BFS for flood fill
        from collections import deque
        queue = deque([(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)])
        seen = set(queue)
        
        pixels = img.load()
        
        # Only process if corners match bg_pixel roughly
        if not is_similar(pixels[0,0], bg_pixel, tolerance):
             print(f"Warning: Top-left pixel {pixels[0,0]} differs from assumed bg {bg_pixel}")
             
        while queue:
            x, y = queue.popleft()
            current_color = pixels[x, y]
            
            if is_similar(current_color, bg_pixel, tolerance):
                pixels[x, y] = (0, 0, 0, 0) # Make transparent
                
                # Check neighbors
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen:
                         # Check if neighbor is similar to BG (not the already transparent one)
                         if is_similar(pixels[nx, ny], bg_pixel, tolerance):
                            seen.add((nx, ny))
                            queue.append((nx, ny))

        if output_path:
            img.save(output_path, "PNG")
            print(f"Saved to {output_path}")
        else:
            img.save(image_path, "PNG")
            print(f"Overwrote {image_path}")
            
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_bg.py <image_path> [tolerance]")
    else:
        path = sys.argv[1]
        tolerance = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        remove_background(path, tolerance=tolerance)
