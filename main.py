import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from CTkColorPicker import AskColor
from PIL import Image, ImageTk
import os
import sys
import subprocess
import numpy as np
import threading

def native_askopenfilename(**kwargs):
    if sys.platform.startswith("linux"):
        try:
            cmd = ['zenity', '--file-selection']
            if 'title' in kwargs:
                cmd.append(f'--title={kwargs["title"]}')
            if 'filetypes' in kwargs:
                for name, exts in kwargs['filetypes']:
                    cmd.append(f'--file-filter={name} | {exts}')
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            return output.decode('utf-8').strip('\n')
        except subprocess.CalledProcessError:
            return "" # Cancelled
        except FileNotFoundError:
            pass # fallback
    return filedialog.askopenfilename(**kwargs)

def native_asksaveasfilename(**kwargs):
    if sys.platform.startswith("linux"):
        try:
            cmd = ['zenity', '--file-selection', '--save', '--confirm-overwrite']
            if 'title' in kwargs:
                cmd.append(f'--title={kwargs["title"]}')
            if 'filetypes' in kwargs:
                for name, exts in kwargs['filetypes']:
                    cmd.append(f'--file-filter={name} | {exts}')
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            filename = output.decode('utf-8').strip('\n')
            if not filename:
                return ""
            if 'defaultextension' in kwargs:
                ext = kwargs['defaultextension']
                if not filename.endswith(ext) and '.' not in filename.split('/')[-1]:
                    filename += ext
            return filename
        except subprocess.CalledProcessError:
            return "" # Cancelled
        except FileNotFoundError:
            pass # fallback
    return filedialog.asksaveasfilename(**kwargs)

def native_messagebox(msg_type, title, message):
    if sys.platform.startswith("linux"):
        try:
            # message type mapping to zenity flags
            ztype = "--info"
            if msg_type == "error": ztype = "--error"
            elif msg_type == "warning": ztype = "--warning"
            
            cmd = ['zenity', ztype, f'--title={title}', f'--text={message}']
            subprocess.run(cmd, stderr=subprocess.DEVNULL)
            return
        except FileNotFoundError:
            pass # fallback
    
    if msg_type == "error":
        messagebox.showerror(title, message)
    elif msg_type == "warning":
        messagebox.showwarning(title, message)
    else:
        messagebox.showinfo(title, message)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class KnitImgApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KnitImg - Machine Knitting Image Assistant")
        self.geometry("1000x780")
        
        # Configure grid layout (3 columns)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.original_image_path = None
        self.original_image = None
        self.processed_image = None
        
        self.setup_left_panel()
        self.setup_middle_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        self.import_btn = ctk.CTkButton(self.left_frame, text="Import Image", command=self.import_image)
        self.import_btn.grid(row=0, column=0, padx=10, pady=20)
        
        self.original_label = ctk.CTkLabel(self.left_frame, text="Original Image", fg_color="gray30", corner_radius=6)
        self.original_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def setup_middle_panel(self):
        self.mid_frame = ctk.CTkFrame(self)
        self.mid_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.mid_frame.grid_columnconfigure(0, weight=1)
        
        row_idx = 0
        
        ctk.CTkLabel(self.mid_frame, text="Functions", font=ctk.CTkFont(size=20, weight="bold")).grid(row=row_idx, column=0, pady=20)
        row_idx += 1
        
        # 1. Rotate
        self.rotate_var = ctk.BooleanVar(value=False)
        self.rotate_cb = ctk.CTkCheckBox(self.mid_frame, text="1. Rotate Image", variable=self.rotate_var, font=ctk.CTkFont(weight="bold"))
        self.rotate_cb.grid(row=row_idx, column=0, padx=20, pady=10, sticky="w")
        row_idx += 1
        
        self.rotate_option = ctk.CTkOptionMenu(self.mid_frame, values=["90", "180", "270"])
        self.rotate_option.grid(row=row_idx, column=0, padx=50, pady=(0, 10), sticky="w")
        row_idx += 1
        
        # 2. Mirror
        self.mirror_var = ctk.BooleanVar(value=False)
        self.mirror_cb = ctk.CTkCheckBox(self.mid_frame, text="2. Mirror Image", variable=self.mirror_var, font=ctk.CTkFont(weight="bold"))
        self.mirror_cb.grid(row=row_idx, column=0, padx=20, pady=10, sticky="w")
        row_idx += 1
        
        self.mirror_option = ctk.CTkOptionMenu(self.mid_frame, values=["Left-Right", "Top-Bottom"])
        self.mirror_option.set("Left-Right")
        self.mirror_option.grid(row=row_idx, column=0, padx=50, pady=(0, 10), sticky="w")
        row_idx += 1
        
        # 3. Scale
        self.scale_var = ctk.BooleanVar(value=False)
        self.scale_cb = ctk.CTkCheckBox(self.mid_frame, text="3. Scale Image", variable=self.scale_var, font=ctk.CTkFont(weight="bold"))
        self.scale_cb.grid(row=row_idx, column=0, padx=20, pady=(15, 10), sticky="w")
        row_idx += 1
        
        scale_param_frame = ctk.CTkFrame(self.mid_frame, fg_color="transparent")
        scale_param_frame.grid(row=row_idx, column=0, padx=50, sticky="w")
        row_idx += 1
        
        ctk.CTkLabel(scale_param_frame, text="Max Width (px):").grid(row=0, column=0, pady=5, sticky="w")
        self.scale_width_entry = ctk.CTkEntry(scale_param_frame, width=80)
        self.scale_width_entry.insert(0, "200")
        self.scale_width_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.shrink_var = ctk.BooleanVar(value=False)
        self.shrink_cb = ctk.CTkCheckBox(scale_param_frame, text="Shrink Vertically?", variable=self.shrink_var)
        self.shrink_cb.grid(row=1, column=0, columnspan=2, pady=(10, 5), sticky="w")
        
        ctk.CTkLabel(scale_param_frame, text="Vertical Factor:").grid(row=2, column=0, pady=5, sticky="w")
        self.shrink_factor_entry = ctk.CTkEntry(scale_param_frame, width=80)
        self.shrink_factor_entry.insert(0, "1.5")
        self.shrink_factor_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # 4. Reduce Colors
        self.reduce_var = ctk.BooleanVar(value=False)
        self.reduce_cb = ctk.CTkCheckBox(self.mid_frame, text="4. Reduce Colors", variable=self.reduce_var, font=ctk.CTkFont(weight="bold"))
        self.reduce_cb.grid(row=row_idx, column=0, padx=20, pady=(25, 10), sticky="w")
        row_idx += 1
        
        reduce_param_frame = ctk.CTkFrame(self.mid_frame, fg_color="transparent")
        reduce_param_frame.grid(row=row_idx, column=0, padx=40, sticky="w")
        row_idx += 1
        
        ctk.CTkLabel(reduce_param_frame, text="Dithering:").grid(row=0, column=0, pady=(0, 10), sticky="w")
        dither_options = [
            "Floyd-Steinberg", "Atkinson", "Ordered (Bayer 4x4)", 
            "Stucki", "Jarvis-Judice-Ninke", "Sierra", "Sierra Lite", "None"
        ]
        self.reduce_dither_option = ctk.CTkOptionMenu(reduce_param_frame, values=dither_options)
        self.reduce_dither_option.set("Floyd-Steinberg")
        self.reduce_dither_option.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w")
        
        # Color palette setup
        self.color_vars = []
        self.color_buttons = []
        self.color_values = [] # Store RGB tuples
        
        # Default 6 colors: Black, White, Red, Green, Blue, Yellow
        default_colors = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        for i in range(6):
            # First two are checked by default
            var = ctk.BooleanVar(value=(i < 2))
            rgb = default_colors[i]
            hex_color = '#%02x%02x%02x' % rgb
            self.color_vars.append(var)
            self.color_values.append(rgb)
            
            row_f = ctk.CTkFrame(reduce_param_frame, fg_color="transparent")
            row_f.grid(row=i+1, column=0, columnspan=2, sticky="w", pady=2)
            
            cb = ctk.CTkCheckBox(row_f, text=f"Color {i+1}", variable=var, width=80)
            cb.grid(row=0, column=0, sticky="w")
            
            # Color swatch button with edit label so users know it's clickable
            btn = ctk.CTkButton(row_f, text="✎ Edit", width=70, height=22, fg_color=hex_color, hover_color=hex_color, corner_radius=4, border_width=1, border_color="gray", text_color="white" if rgb == (0,0,0) else "black", command=lambda idx=i: self.choose_color(idx))
            btn.grid(row=0, column=1, padx=10)
            self.color_buttons.append(btn)
        
        # Spacer
        self.mid_frame.grid_rowconfigure(row_idx, weight=1)
        row_idx += 1
        
        self.apply_btn = ctk.CTkButton(self.mid_frame, text="Apply Functions", command=self.apply_functions, height=40, font=ctk.CTkFont(weight="bold"))
        self.apply_btn.grid(row=row_idx, column=0, padx=20, pady=20, sticky="ew")
        
    def setup_right_panel(self):
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        self.export_btn = ctk.CTkButton(self.right_frame, text="Export to PNG", command=self.export_image, state="disabled", fg_color="forestgreen", hover_color="darkgreen")
        self.export_btn.grid(row=0, column=0, padx=10, pady=20)
        
        self.result_label = ctk.CTkLabel(self.right_frame, text="Result Image", fg_color="gray30", corner_radius=6)
        self.result_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Loading overlay (initially hidden)
        self.loading_overlay = ctk.CTkFrame(self.right_frame, fg_color="black", corner_radius=6)
        # We'll use place to overlay it precisely on top of the result_label when needed
        ctk.CTkLabel(self.loading_overlay, text="Computing... Please wait", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    def choose_color(self, idx):
        # Initial color for chooser
        initial_color = '#%02x%02x%02x' % self.color_values[idx]
        color_picker = AskColor(title=f"Choose Color {idx+1}", initial_color=initial_color)
        color_code = color_picker.get() # Returns hex color string e.g., '#ff0000' or None
        if color_code:
            # Convert hex to RGB tuple
            h = color_code.lstrip('#')
            rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            self.color_values[idx] = rgb
            # Ensure '✎ Edit' text stays readable on any background
            brightness = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
            text_color = "white" if brightness < 128 else "black"
            self.color_buttons[idx].configure(fg_color=color_code, hover_color=color_code, text_color=text_color)

    def import_image(self):
        file_path = native_askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
        )
        if file_path:
            try:
                self.original_image_path = file_path
                self.original_image = Image.open(file_path).convert("RGBA")
                self.display_image(self.original_image, self.original_label, "Original Image")
                # Reset processed image
                self.processed_image = None
                self.result_label.configure(image="", text="Result Image")
                self.export_btn.configure(state="disabled")
            except Exception as e:
                native_messagebox("error", "Error", f"Failed to open image:\n{e}")

    def display_image(self, img, label_widget, default_text=""):
        if img is None:
            label_widget.configure(image="", text=default_text)
            return

        display_size = (300, 400) # Fixed bounding box for thumbnail
        img_copy = img.copy()
        
        # For '1' mode (B&W or Palette), convert back to RGB to display properly in tk/ctk
        if img_copy.mode != 'RGB' and img_copy.mode != 'RGBA':
            img_copy = img_copy.convert('RGBA')
            
        img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img

    def apply_functions(self):
        if self.original_image is None:
            native_messagebox("warning", "Warning", "Please import an image first.")
            return

        # Show loading indicator and disable buttons
        self.apply_btn.configure(state="disabled", text="Processing...")
        self.import_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        
        # Overlay the loading frame
        self.loading_overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.4)
        self.loading_overlay.lift()

        # Run processing in a background thread
        thread = threading.Thread(target=self._process_image_worker, daemon=True)
        thread.start()

    def _process_image_worker(self):
        """Heavy lifting done here in background thread."""
        try:
            img = self.original_image.copy()
            
            # 1. Rotate
            if self.rotate_var.get():
                angle_str = self.rotate_option.get()
                if angle_str == "90":
                    img = img.transpose(Image.Transpose.ROTATE_270) # 90 degrees clockwise
                elif angle_str == "180":
                    img = img.transpose(Image.Transpose.ROTATE_180) # 180 degrees
                elif angle_str == "270":
                    img = img.transpose(Image.Transpose.ROTATE_90)  # 270 degrees clockwise = 90 deg CCW

            # 2. Mirror
            if self.mirror_var.get():
                mirror_str = self.mirror_option.get()
                if mirror_str == "Left-Right":
                    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif mirror_str == "Top-Bottom":
                    img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            # 3. Scale
            if self.scale_var.get():
                try:
                    max_width = int(self.scale_width_entry.get())
                    if max_width <= 0: raise ValueError
                except ValueError:
                    self.after(0, lambda: native_messagebox("error", "Error", "Max width must be a positive integer."))
                    self.after(0, self._reset_ui_after_processing)
                    return
                    
                original_width, original_height = img.size
                if original_width != max_width or self.shrink_var.get(): 
                    ratio = max_width / float(original_width)
                    new_height = int(float(original_height) * float(ratio))
                    
                    if self.shrink_var.get():
                        try:
                            factor = float(self.shrink_factor_entry.get())
                            if factor <= 0: raise ValueError
                        except ValueError:
                            self.after(0, lambda: native_messagebox("error", "Error", "Vertical shrink factor must be a positive number."))
                            self.after(0, self._reset_ui_after_processing)
                            return
                        new_height = int(new_height / factor)
                        
                    new_height = max(1, new_height)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # 4. Reduce Colors
            if self.reduce_var.get():
                dither_mode_str = self.reduce_dither_option.get()
                
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    alpha = img.split()[3]
                    background.paste(img, mask=alpha)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                active_colors = []
                for i in range(6):
                    if self.color_vars[i].get():
                        active_colors.append(self.color_values[i])
                        
                if not active_colors:
                    self.after(0, lambda: native_messagebox("warning", "Warning", "Reduce Colors enabled but no colors selected."))
                else:
                    base_p = Image.new("P", (1, 1))
                    palette_data = []
                    for color in active_colors:
                        palette_data.extend(color)
                    while len(palette_data) < 768:
                        palette_data.extend(active_colors[0])
                    base_p.putpalette(palette_data)
                    
                    if dither_mode_str in ["Floyd-Steinberg", "None"]:
                        dither_flag = Image.Dither.FLOYDSTEINBERG if dither_mode_str == "Floyd-Steinberg" else Image.Dither.NONE
                        img = img.quantize(palette=base_p, dither=dither_flag)
                    else:
                        img = self.run_custom_dithering(img, active_colors, dither_mode_str)
                    
                    img = img.convert("RGB")

            # Finalize on main thread
            self.after(0, lambda: self._finalize_processing(img))
            
        except Exception as e:
            self.after(0, lambda err=e: native_messagebox("error", "Error", f"Processing failed:\n{err}"))
            self.after(0, self._reset_ui_after_processing)

    def _finalize_processing(self, img):
        self.processed_image = img
        self.display_image(self.processed_image, self.result_label, "Result Image")
        self._reset_ui_after_processing()

    def _reset_ui_after_processing(self):
        self.loading_overlay.place_forget()
        self.apply_btn.configure(state="normal", text="Apply Functions")
        self.import_btn.configure(state="normal")
        if self.processed_image is not None:
            self.export_btn.configure(state="normal")

    def run_custom_dithering(self, img, palette, mode):
        """Custom error diffusion dithering implementation using NumPy."""
        # Convert image to float32 NumPy array for error calculations
        arr = np.array(img, dtype=np.float32)
        h, w, c = arr.shape
        palette = np.array(palette, dtype=np.float32)
        
        if "Ordered" in mode:
            # Bayer 4x4 Matrix
            bayer_matrix = np.array([
                [ 0,  8,  2, 10],
                [12,  4, 14,  6],
                [ 3, 11,  1,  9],
                [15,  7, 13,  5]
            ], dtype=np.float32) / 16.0 - 0.5 # Center at 0
            
            # Tile the pattern across the image
            # Ordered dithering effect: slightly perturb the color before choosing closest to create pattern
            # Increase spread for more visibility (scaled by intensity)
            spread = 64.0 
            for y in range(h):
                for x in range(w):
                    perturb = bayer_matrix[y % 4, x % 4] * spread
                    old_pixel = arr[y, x] + perturb
                    dist = np.sum((palette - old_pixel)**2, axis=1)
                    arr[y, x] = palette[np.argmin(dist)]
            return Image.fromarray(arr.astype(np.uint8))

        # Error diffusion setups
        # kernels: (dy, dx, weight)
        if mode == "Atkinson":
            # Atkinson: 1/8 each to (x+1,y), (x+2,y), (x-1,y+1), (x,y+1), (x+1,y+1), (x,y+2)
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

        # Diffusion loop
        for y in range(h):
            for x in range(w):
                old_pixel = arr[y, x].copy()
                # Closest color in palette
                dist = np.sum((palette - old_pixel)**2, axis=1)
                new_pixel = palette[np.argmin(dist)]
                arr[y, x] = new_pixel
                
                # Calculate error
                error = old_pixel - new_pixel
                
                # Diffuse
                for dy, dx, weight in kernel:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        arr[ny, nx] += error * weight
                        
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    def export_image(self):
        if self.processed_image is None:
            return
            
        file_path = native_asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Export Image"
        )
        if file_path:
            try:
                # If image is mode '1' and we save as PNG, it's efficiently a 1-bit PNG.
                self.processed_image.save(file_path)
                native_messagebox("info", "Success", "Image exported successfully!")
            except Exception as e:
                native_messagebox("error", "Error", f"Failed to save image:\n{e}")

if __name__ == "__main__":
    app = KnitImgApp()
    app.mainloop()
