import customtkinter as ctk
import cv2
import numpy as np
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import os

class BackgroundRemoverAndEnhancer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Background Remover and Enhancer")
        self.geometry("1200x800")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Sidebar content
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Background Remover\nand Enhancer",
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Buttons
        self.load_button = ctk.CTkButton(self.sidebar_frame, text="Load Image",
                                       command=self.open_image)
        self.load_button.grid(row=1, column=0, padx=20, pady=10)

        self.remove_button = ctk.CTkButton(self.sidebar_frame, text="Remove Background",
                                          command=self.remove_background)
        self.remove_button.grid(row=2, column=0, padx=20, pady=10)
        self.remove_button.configure(state="disabled")

        self.enhance_button = ctk.CTkButton(self.sidebar_frame, text="Enhance Image",
                                           command=self.enhance_image)
        self.enhance_button.grid(row=3, column=0, padx=20, pady=10)
        self.enhance_button.configure(state="disabled")

        self.save_button = ctk.CTkButton(self.sidebar_frame, text="Save Image",
                                       command=self.save_image)
        self.save_button.grid(row=4, column=0, padx=20, pady=10)
        self.save_button.configure(state="disabled")

        # Status label in sidebar
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Ready",
                                       font=ctk.CTkFont(size=12))
        self.status_label.grid(row=6, column=0, padx=20, pady=(10, 20))

        # Create main frame for image display
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create frames for original, processed, and enhanced images
        self.original_frame = ctk.CTkFrame(self.main_frame)
        self.original_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.processed_frame = ctk.CTkFrame(self.main_frame)
        self.processed_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.enhanced_frame = ctk.CTkFrame(self.main_frame)
        self.enhanced_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Labels for images
        self.original_label = ctk.CTkLabel(self.original_frame, text="Original Image")
        self.original_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.input_preview = ctk.CTkLabel(self.original_frame, text="No image loaded")
        self.input_preview.grid(row=1, column=0, padx=10, pady=5)

        self.processed_label = ctk.CTkLabel(self.processed_frame, text="After Background Removal")
        self.processed_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.output_preview = ctk.CTkLabel(self.processed_frame, text="No image processed")
        self.output_preview.grid(row=1, column=0, padx=10, pady=5)

        self.enhanced_label = ctk.CTkLabel(self.enhanced_frame, text="Enhanced Image")
        self.enhanced_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.enhanced_preview = ctk.CTkLabel(self.enhanced_frame, text="No image enhanced")
        self.enhanced_preview.grid(row=1, column=0, padx=10, pady=5)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        # Initialize variables
        self.input_image = None
        self.output_image = None
        self.enhanced_image = None

    def update_preview(self, image, preview_label):
        # Resize image while maintaining aspect ratio
        display_size = (400, 400)
        image_copy = image.copy()
        image_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image_copy)
        preview_label.configure(image=photo, text="")
        preview_label.image = photo

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                self.input_image = Image.open(file_path)
                self.update_preview(self.input_image, self.input_preview)
                self.remove_button.configure(state="normal")
                self.enhance_button.configure(state="normal")
                self.status_label.configure(text="Image loaded")
                self.progress_bar.set(0)
            except Exception as e:
                self.show_error("Failed to load image", str(e))

    def remove_background(self):
        if not self.input_image:
            return

        self.remove_button.configure(state="disabled")
        self.progress_bar.start()
        self.status_label.configure(text="Removing background...")

        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            self.input_image.save(img_byte_arr, format=self.input_image.format)
            img_byte_arr = img_byte_arr.getvalue()

            # Remove background
            output_bytes = remove(img_byte_arr)
            self.output_image = Image.open(io.BytesIO(output_bytes))

            # Update preview
            self.update_preview(self.output_image, self.output_preview)
            self.save_button.configure(state="normal")
            self.status_label.configure(text="Background removed")

        except Exception as e:
            self.show_error("Background removal failed", str(e))
            self.status_label.configure(text="Error removing background")
        finally:
            self.progress_bar.stop()
            self.progress_bar.set(1)
            self.remove_button.configure(state="normal")

    def enhance_image(self):
        if not self.output_image:
            return

        self.enhance_button.configure(state="disabled")
        self.progress_bar.start()
        self.status_label.configure(text="Enhancing image...")

        try:
            # Apply image enhancement techniques
            enhanced_image = self.apply_enhancements(self.output_image)
            self.enhanced_image = enhanced_image

            # Update preview
            self.update_preview(self.enhanced_image, self.enhanced_preview)
            self.save_button.configure(state="normal")
            self.status_label.configure(text="Image enhanced")

        except Exception as e:
            self.show_error("Image enhancement failed", str(e))
            self.status_label.configure(text="Error enhancing image")
        finally:
            self.progress_bar.stop()
            self.progress_bar.set(1)
            self.enhance_button.configure(state="normal")

    def apply_enhancements(self, image):
        # Convert to LAB color space
        lab_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2LAB)

        # Split LAB channels
        l, a, b = cv2.split(lab_image)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_l = clahe.apply(l)

        # Merge channels back
        enhanced_lab = cv2.merge([enhanced_l, a, b])

        # Convert back to RGB
        enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

        # Apply sharpening
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        enhanced_sharp = cv2.filter2D(enhanced_rgb, -1, kernel)

        # Denoise
        enhanced_image = cv2.fastNlMeansDenoisingColored(enhanced_sharp)

        return Image.fromarray(np.uint8(enhanced_image * 255))

    def save_image(self):
        if not self.enhanced_image:
            self.show_error("No image to save", "Please process an image first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            title="Save the output image"
        )

        if file_path:
            try:
                self.enhanced_image.save(file_path)
                self.status_label.configure(text="Image saved")
                self.show_success("Success", f"Image saved to:\n{file_path}")
            except Exception as e:
                self.show_error("Failed to save", str(e))

    def show_error(self, title, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title(title)
        error_window.geometry("300x150")
        error_window.transient(self)
        error_window.grab_set()
        
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=20)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)

    def show_success(self, title, message):
        success_window = ctk.CTkToplevel(self)
        success_window.title(title)
        success_window.geometry("300x150")
        success_window.transient(self)
        success_window.grab_set()
        
        ctk.CTkLabel(success_window, text=message, wraplength=250).pack(pady=20)
        ctk.CTkButton(success_window, text="OK", command=success_window.destroy).pack(pady=10)

def main():
    app = BackgroundRemoverAndEnhancer()
    app.mainloop()

if __name__ == "__main__":
    main()