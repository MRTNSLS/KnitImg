import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys
import subprocess

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
        self.geometry("1000x650")
        
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
        
        # 2. Scale
        self.scale_var = ctk.BooleanVar(value=False)
        self.scale_cb = ctk.CTkCheckBox(self.mid_frame, text="2. Scale Image", variable=self.scale_var, font=ctk.CTkFont(weight="bold"))
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
        
        # 3. Black and White
        self.bw_var = ctk.BooleanVar(value=False)
        self.bw_cb = ctk.CTkCheckBox(self.mid_frame, text="3. Black and White", variable=self.bw_var, font=ctk.CTkFont(weight="bold"))
        self.bw_cb.grid(row=row_idx, column=0, padx=20, pady=(25, 10), sticky="w")
        row_idx += 1
        
        bw_param_frame = ctk.CTkFrame(self.mid_frame, fg_color="transparent")
        bw_param_frame.grid(row=row_idx, column=0, padx=50, sticky="w")
        row_idx += 1
        
        ctk.CTkLabel(bw_param_frame, text="Dithering:").grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.bw_dither_option = ctk.CTkOptionMenu(bw_param_frame, values=["Floyd-Steinberg", "None"])
        self.bw_dither_option.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w")
        
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

        # Always update to fit within a bounding box approximately the size of the label frame
        # Make a thumbnail so we do not distort AR but fit it into a box
        display_size = (300, 400) # Reasonable max display size for canvas
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

        # 2. Scale
        if self.scale_var.get():
            try:
                max_width = int(self.scale_width_entry.get())
                if max_width <= 0: raise ValueError
            except ValueError:
                native_messagebox("error", "Error", "Max width must be a positive integer.")
                return
                
            original_width, original_height = img.size
            if original_width != max_width or self.shrink_var.get(): # Always scale to the requested width
                ratio = max_width / float(original_width)
                new_height = int(float(original_height) * float(ratio))
                
                if self.shrink_var.get():
                    try:
                        factor = float(self.shrink_factor_entry.get())
                        if factor <= 0: raise ValueError
                    except ValueError:
                        native_messagebox("error", "Error", "Vertical shrink factor must be a positive number.")
                        return
                    new_height = int(new_height / factor)
                    
                # Prevent height from resolving to 0
                new_height = max(1, new_height)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 3. Black and White
        if self.bw_var.get():
            dither_mode = self.bw_dither_option.get()
            
            # Composite onto white background in case of transparent pixels
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                # using the alpha layer as the paste mask
                alpha = img.split()[3]
                background.paste(img, mask=alpha)
                img = background
            
            # Convert to Greyscale first to normalize
            img = img.convert("L")
            if dither_mode == "Floyd-Steinberg":
                img = img.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
            else:
                img = img.convert("1", dither=Image.Dither.NONE)

        self.processed_image = img
        self.display_image(self.processed_image, self.result_label, "Result Image")
        self.export_btn.configure(state="normal")

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
