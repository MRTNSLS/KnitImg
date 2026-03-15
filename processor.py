from PIL import Image
import numpy as np

class ImageProcessor:
    @staticmethod
    def process(img, rotate_enabled=False, rotate_angle="90", 
                mirror_enabled=False, mirror_mode="Left-Right",
                scale_enabled=False, max_width=200, shrink_enabled=False, shrink_factor=1.5,
                reduce_enabled=False, dither_mode="Floyd-Steinberg", active_colors=None):
        """
        Core image processing engine.
        Args:
            img (PIL.Image): The input image.
            ... individual params matching UI options ...
        Returns:
            PIL.Image: The processed image.
        """
        processed = img.copy()

        # 1. Rotate
        if rotate_enabled:
            if rotate_angle == "90":
                processed = processed.transpose(Image.Transpose.ROTATE_270)
            elif rotate_angle == "180":
                processed = processed.transpose(Image.Transpose.ROTATE_180)
            elif rotate_angle == "270":
                processed = processed.transpose(Image.Transpose.ROTATE_90)

        # 2. Mirror
        if mirror_enabled:
            if mirror_mode == "Left-Right":
                processed = processed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif mirror_mode == "Top-Bottom":
                processed = processed.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        # 3. Scale
        if scale_enabled:
            original_width, original_height = processed.size
            if original_width != max_width or shrink_enabled:
                ratio = max_width / float(original_width)
                new_height = int(float(original_height) * float(ratio))
                
                if shrink_enabled:
                    new_height = int(new_height / shrink_factor)
                
                new_height = max(1, new_height)
                processed = processed.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 4. Reduce Colors
        if reduce_enabled and active_colors:
            if processed.mode == 'RGBA':
                background = Image.new('RGB', processed.size, (255, 255, 255))
                alpha = processed.split()[3]
                background.paste(processed, mask=alpha)
                processed = background
            elif processed.mode != 'RGB':
                processed = processed.convert('RGB')
            
            base_p = Image.new("P", (1, 1))
            palette_data = []
            for color in active_colors:
                palette_data.extend(color)
            while len(palette_data) < 768:
                palette_data.extend(active_colors[0])
            base_p.putpalette(palette_data)
            
            if dither_mode in ["Floyd-Steinberg", "None"]:
                dither_flag = Image.Dither.FLOYDSTEINBERG if dither_mode == "Floyd-Steinberg" else Image.Dither.NONE
                processed = processed.quantize(palette=base_p, dither=dither_flag)
                processed = processed.convert("RGB")
            else:
                processed = ImageProcessor.run_custom_dithering(processed, active_colors, dither_mode)
                
        return processed

    @staticmethod
    def run_custom_dithering(img, palette, mode):
        """Custom error diffusion dithering implementation using NumPy."""
        arr = np.array(img, dtype=np.float32)
        h, w, c = arr.shape
        palette = np.array(palette, dtype=np.float32)
        
        if "Ordered" in mode:
            bayer_matrix = np.array([
                [ 0,  8,  2, 10],
                [12,  4, 14,  6],
                [ 3, 11,  1,  9],
                [15,  7, 13,  5]
            ], dtype=np.float32) / 16.0 - 0.5
            
            spread = 64.0 
            for y in range(h):
                for x in range(w):
                    perturb = bayer_matrix[y % 4, x % 4] * spread
                    old_pixel = arr[y, x] + perturb
                    dist = np.sum((palette - old_pixel)**2, axis=1)
                    arr[y, x] = palette[np.argmin(dist)]
            return Image.fromarray(arr.astype(np.uint8))

        if mode == "Atkinson":
            kernel = [(0, 1, 1/8), (0, 2, 1/8), (1, -1, 1/8), (1, 0, 1/8), (1, 1, 1/8), (2, 0, 1/8)]
        elif mode == "Stucki":
            kernel = [(0, 1, 8/42), (0, 2, 4/42),
                      (1, -2, 2/42), (1, -1, 4/42), (1, 0, 8/42), (1, 1, 4/42), (1, 2, 2/42),
                      (2, -2, 1/42), (2, -1, 2/42), (2, 0, 4/42), (2, 1, 2/42), (2, 2, 1/42)]
        elif mode == "Jarvis-Judice-Ninke":
            kernel = [(0, 1, 7/48), (0, 2, 5/48),
                      (1, -2, 3/48), (1, -1, 5/48), (1, 0, 7/48), (1, 1, 5/48), (1, 2, 3/48),
                      (2, -2, 1/48), (2, -1, 3/48), (2, 0, 5/48), (2, 1, 3/48), (2, 2, 1/48)]
        elif mode == "Sierra":
            kernel = [(0, 1, 5/32), (0, 2, 3/32),
                      (1, -2, 2/32), (1, -1, 4/32), (1, 0, 5/32), (1, 1, 4/32), (1, 2, 2/32),
                      (2, -1, 2/32), (2, 0, 3/32), (2, 1, 2/32)]
        elif mode == "Sierra Lite":
            kernel = [(0, 1, 2/4), (1, -1, 1/4), (1, 0, 1/4)]
        else:
            return Image.fromarray(arr.astype(np.uint8))

        for y in range(h):
            for x in range(w):
                old_pixel = arr[y, x].copy()
                dist = np.sum((palette - old_pixel)**2, axis=1)
                new_pixel = palette[np.argmin(dist)]
                arr[y, x] = new_pixel
                error = old_pixel - new_pixel
                for dy, dx, weight in kernel:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        arr[ny, nx] += error * weight
                        
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
