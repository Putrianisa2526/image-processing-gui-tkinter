import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import numpy as np
import webbrowser
import os

# Import modul operasi dasar
from basic_ops import (
    negative, grayscale, arithmetic,
    boolean_not, boolean_and, boolean_or, boolean_xor,
    translation, rotation, zooming, flipping, cropping,
    threshold, to_binary, to_rgb, to_hsv, to_cmy,
    to_yuv, to_yiq, pseudo_color,
    convolution, fourier_transform,
    blur_image, sharpen_image, edge_detect_image
)

# Import modul enhancement
from enhancement import (
    adjust_brightness,
    adjust_contrast,
    histogram_equalization,
    smoothing,
    sharpening,
    correction
)

# Import modul noise
from noise import (
    add_gaussian_noise,
    add_rayleigh_noise,
    add_erlang_noise,
    add_exponential_noise,
    add_uniform_noise,
    add_impulse_noise
)

# Import modul edge detection
from edge_detection import (
    sobel_edge,
    prewitt_edge,
    roberts_edge,
    laplacian_edge,
    log_edge,
    canny_edge,
    compass_edge
)

# Import modul segmentation
from segmentation import (
    contour_image,
    watershed_image,
    watermark_image
)

class AplikasiPCD:
    # Inisialisasi aplikasi dan komponen utama GUI
    def __init__(self, root):
        self.root = root
        self.about_window = None
        self.info_frame = None
        self.root.title("Aplikasi Pengolahan Citra Digital")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1a1a1a")

        # Variabel citra
        self.current_image = None
        self.current_image_path = None
        self.original_image = None
        self.display_image = None

        # Stack Undo / Redo
        self.history_stack = []
        self.redo_stack = []
        self.zoom_factor = 1.0

        # Slider aktif
        self.active_slider = None
        self.active_slider_func = None
        self.active_slider_label = None
        self.history_stack_slider = []

        # Registry slider dan flag reset
        self.slider_registry = {}
        self._is_reseting_sliders = False

        # Flag tampilan About
        self.is_showing_about = False

        # Font custom / fallback
        try:
            import tkinter.font as tkfont
            self.custom_font = tkfont.Font(family="Horizon Type - AcherusFeral-Bold", size=9)
            self.custom_font_bold = tkfont.Font(family="Horizon Type - AcherusFeral-Bold", size=10, weight="bold")
            self.custom_font_small = tkfont.Font(family="Horizon Type - AcherusFeral-Bold", size=8)
            self.custom_font_medium = tkfont.Font(family="Horizon Type - AcherusFeral-Bold", size=11, weight="bold")
        except:
            self.custom_font = ("Roboto", 9)
            self.custom_font_bold = ("Roboto", 10, "bold")
            self.custom_font_small = ("Roboto", 8)
            self.custom_font_medium = ("Roboto", 11, "bold")

        # Frame menu atas
        self.top_menu_frame = tk.Frame(root, bg="#2C3E50", height=45)
        self.top_menu_frame.pack(side="top", fill="x")
        self.top_menu_frame.pack_propagate(False)

        # Logo kiri atas
        logo_frame = tk.Frame(self.top_menu_frame, bg="#2C3E50", width=120)
        logo_frame.pack(side="left", fill="y")
        logo_frame.pack_propagate(False)
        try:
            logo_img = Image.open("logo.png").resize((100, 100), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(logo_frame, image=self.logo_photo, bg="#2C3E50").pack(expand=True)
        except:
            tk.Label(logo_frame, text="PQ", font=self.custom_font_bold, bg="#2C3E50", fg="#ECF0F1").pack(expand=True)

        # Container tombol menu utama
        menu_container = tk.Frame(self.top_menu_frame, bg="#2C3E50")
        menu_container.pack(side="left", expand=True, fill="both")

        # Daftar menu utama
        menu_buttons = [
            ("File", self.menu_file),
            ("Basic Ops", self.menu_basic_ops),
            ("Enhancement", self.menu_enhancement),
            ("Noise", self.menu_noise),
            ("Edge Detection", self.menu_edge_detection),
            ("Segmentation", self.menu_segmentation),
            ("About", self.show_info),
        ]

        # Tombol menu utama
        for name, cmd in menu_buttons:
            tk.Button(
                menu_container,
                text=name,
                font=self.custom_font,
                bg="#34495E",
                fg="#ECF0F1",
                activebackground="#1A89BC",
                activeforeground="#ffffff",
                relief="flat",
                padx=12, pady=8,
                command=cmd,
                cursor="hand2",
                bd=0
            ).pack(side="left", expand=True, fill="both", padx=1)

        # Frame utama
        self.main_frame = tk.Frame(root, bg="#1a1a1a")
        self.main_frame.pack(expand=True, fill="both", padx=0, pady=0)

        # Frame kiri menu
        self.left_frame = tk.Frame(self.main_frame, bg="#34495E", width=150)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        # Frame kiri kedua (submenu level 2)
        self.left_frame2 = tk.Frame(self.main_frame, bg="#2C3E50", width=150)
        self.left_frame2.pack(side="left", fill="y")
        self.left_frame2.pack_propagate(False)
        self.left_frame2.pack_forget()

        self.left_frame_title = tk.Label(
            self.left_frame,
            text="Menu",
            font=self.custom_font_bold,
            bg="#2C3E50",
            fg="#ECF0F1",
            pady=10
        )
        self.left_frame_title.pack(side="top", fill="x")

        # Frame kanan tampilan gambar
        self.image_frame = tk.Frame(self.main_frame, bg="#1a1a1a", relief="flat", bd=0)
        self.image_frame.pack(side="left", expand=True, fill="both", padx=(0, 0))

        # Label placeholder awal
        self.image_label = tk.Label(
            self.image_frame,
            bg="#1a1a1a",
            text="Belum ada gambar\nKlik File → Open",
            anchor="center",
            font=self.custom_font,
            fg="#7F8C8D"
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Footer
        tk.Label(
            root,
            text="© 2025 Pixel Queens - Teknik Informatika Universitas Riau",
            bg="#2C3E50",
            fg="#ECF0F1",
            font=self.custom_font_small,
            anchor="center",
            pady=8
        ).pack(side="bottom", fill="x")

        # Event resize window
        self.root.bind("<Configure>", self.on_resize)

    # Mendaftarkan slider agar bisa direset
    def register_slider(self, name, slider_widget, default_value):
        self.slider_registry[name] = {"slider": slider_widget, "default": default_value}

    # Mengosongkan daftar slider saat pindah panel
    def clear_slider_registry(self):
        self.slider_registry.clear()

    # Mereset semua slider ke nilai default
    def reset_all_sliders_to_default(self):
        self._is_reseting_sliders = True
        try:
            for name, info in list(self.slider_registry.items()):
                s = info["slider"]
                if not s or not s.winfo_exists():
                    continue
                default = info["default"]
                cmd = s.cget("command")
                s.configure(command=None)
                s.set(default)
                s.configure(command=cmd)
        finally:
            self._is_reseting_sliders = False

    # Menghapus widget di frame menu kiri
    def clear_left_submenu(self):
        for w in self.left_frame.winfo_children():
            w.destroy()

    # Menghapus widget di frame submenu kiri kedua
    def clear_left_submenu2(self):
        for w in self.left_frame2.winfo_children():
            w.destroy()

    # Menyembunyikan frame About dan mengembalikan tampilan gambar
    def _hide_info_frame(self):
        if hasattr(self, "info_frame") and self.info_frame:
            try:
                if self.info_frame.winfo_exists():
                    self.info_frame.destroy()
            except Exception:
                pass
            finally:
                self.info_frame = None

        self.is_showing_about = False

        if self.current_image:
            self.image_label.place_forget()
            self.display_image_fit()
        else:
            self.image_label.config(
                image="",
                text="Belum ada gambar\nKlik File → Open",
                anchor="center",
                font=self.custom_font,
                fg="#7F8C8D",
                bg="#1a1a1a",
            )
            self.image_label.place(relx=0.5, rely=0.5, anchor="center")

    # Menambahkan submenu utama di frame kiri
    def add_submenu_left(self, options, commands, show_undo=True, title="Menu"):
        self._hide_info_frame()
        self.clear_slider_registry()

        self.clear_left_submenu()
        self.left_frame2.pack_forget()
        self.left_frame_title = tk.Label(
            self.left_frame,
            text=title,
            font=self.custom_font_bold,
            bg="#2C3E50",
            fg="#ECF0F1",
            pady=10
        )
        self.left_frame_title.pack(side="top", fill="x")

        for i, op in enumerate(options):
            tk.Button(
                self.left_frame,
                text=op,
                font=self.custom_font,
                bg="#5CA0BF",
                fg="#ECF0F1",
                activebackground="#1664A0",
                activeforeground="#ffffff",
                relief="flat",
                width=16,
                pady=7,
                command=commands[i],
                cursor="hand2",
                bd=0
            ).pack(pady=2, padx=5)

        # Tambah tombol Undo / Redo / Reset
        if show_undo:
            reset_bar = tk.Frame(self.left_frame, bg="#2C3E50")
            reset_bar.pack(side="bottom", fill="x", pady=(0, 5), padx=5)

            btn_reset = tk.Button(
                reset_bar,
                text="⟳ Reset",
                font=self.custom_font_bold,
                bg="#FFFFFF",
                fg="#2C3E50",
                activebackground="#FFFFFF",
                activeforeground="#2C3E50",
                relief="flat",
                width=18,
                pady=7,
                command=self.reset_image,
                cursor="hand2",
                bd=0
            )
            btn_reset.pack(fill="x")

            bottom_bar = tk.Frame(self.left_frame, bg="#2C3E50")
            bottom_bar.pack(side="bottom", fill="x", pady=5, padx=5)

            btn_undo = tk.Button(
                bottom_bar,
                text="↶ Undo",
                font=self.custom_font_bold,
                bg="#E74C3C",
                fg="#ffffff",
                activebackground="#C0392B",
                activeforeground="#ffffff",
                relief="flat",
                width=8,
                pady=7,
                command=self.undo_image,
                cursor="hand2",
                bd=0
            )
            btn_undo.pack(side="left", expand=True, fill="x", padx=(0, 2))

            btn_redo = tk.Button(
                bottom_bar,
                text="↷ Redo",
                font=self.custom_font_bold,
                bg="#27AE60",
                fg="#ffffff",
                activebackground="#1E8E4F",
                activeforeground="#ffffff",
                relief="flat",
                width=8,
                pady=7,
                command=self.redo_image,
                cursor="hand2",
                bd=0
            )
            btn_redo.pack(side="left", expand=True, fill="x", padx=(2, 0))

    # Menambahkan submenu level 2 di frame kiri kedua
    def add_submenu_left2(self, options, commands, title="Detail"):
        self._hide_info_frame()
        self.clear_slider_registry()
        self.clear_left_submenu2()

        self.left_frame2.pack(side="left", fill="y", before=self.image_frame)
        tk.Label(
            self.left_frame2,
            text=title,
            font=self.custom_font_bold,
            bg="#1C2833",
            fg="#ECF0F1",
            pady=10
        ).pack(side="top", fill="x")

        for i, op in enumerate(options):
            tk.Button(
                self.left_frame2,
                text=op,
                font=self.custom_font_small,
                bg="#5CA0BF",
                fg="#ECF0F1",
                activebackground="#1664A0",
                activeforeground="#ffffff",
                relief="flat",
                width=16,
                pady=6,
                command=commands[i],
                cursor="hand2",
                bd=0
            ).pack(pady=2, padx=5)

    # Menjalankan operasi citra di thread terpisah
    def update_image_async(self, func, *args):
        if self.current_image:
            self.history_stack.append(self.current_image.copy())
            self.redo_stack.clear()

        def task():
            try:
                result = func(*args)
                self.root.after(0, lambda: self.update_image(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=task, daemon=True).start()

    # Menampilkan submenu File
    def menu_file(self):
        ops = ["Open", "Save", "Save As", "Exit"]
        cmds = [self.open_image, self.save_image, self.save_as_image, self.root.quit]
        self.add_submenu_left(ops, cmds, show_undo=False, title="File")

    # Menampilkan submenu Basic Operations
    def menu_basic_ops(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return
        ops = [
            "Negative", "Arithmetic", "Boolean", "Geometrics",
            "Thresholding", "Convolution", "Fourier Transform", "Colouring"
        ]
        cmds = [
            self.apply_negative,
            self.show_arithmetic,
            self.show_boolean,
            self.show_geometrics,
            self.apply_thresholding,
            self.show_convolution,
            self.apply_fourier,
            self.show_colouring
        ]
        self.add_submenu_left(ops, cmds, title="Basic Ops")

    # Menampilkan submenu Enhancement
    def menu_enhancement(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        ops = [
            "Brightness",
            "Contrast",
            "Hist. Equalization",
            "Smoothing",
            "Sharpening",
            "Geometric Correction"
        ]
        cmds = [
            self.show_brightness,
            self.show_contrast,
            self.apply_hist_eq,
            self.show_smoothing,
            self.show_sharpening,
            self.apply_correction
        ]
        self.add_submenu_left(ops, cmds, title="Enhancement")

    # Menampilkan submenu Noise
    def menu_noise(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        ops = [
            "Gaussian Noise",
            "Rayleigh Noise",
            "Erlang Noise",
            "Exponential Noise",
            "Uniform Noise",
            "Impulse Noise"
        ]
        cmds = [
            lambda: self.update_image_async(add_gaussian_noise, self.current_image),
            lambda: self.update_image_async(add_rayleigh_noise, self.current_image),
            lambda: self.update_image_async(add_erlang_noise, self.current_image),
            lambda: self.update_image_async(add_exponential_noise, self.current_image),
            lambda: self.update_image_async(add_uniform_noise, self.current_image),
            lambda: self.update_image_async(add_impulse_noise, self.current_image)
        ]
        self.add_submenu_left(ops, cmds, title="Noise")

    # Menampilkan submenu Edge Detection
    def menu_edge_detection(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        ops = ["1'st Detectional", "2'nd Differential ", "Compass"]
        cmds = [self.show_first_gradient, self.show_second_gradient, self.apply_compass]
        self.add_submenu_left(ops, cmds, title="Edge Detection")

    # Submenu edge orde pertama
    def show_first_gradient(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return
        ops = ["Sobel", "Prewitt", "Robert"]
        cmds = [
            lambda: self.update_image_async(sobel_edge, self.current_image),
            lambda: self.update_image_async(prewitt_edge, self.current_image),
            lambda: self.update_image_async(roberts_edge, self.current_image)
        ]
        self.add_submenu_left2(ops, cmds, title="1'st Gradient")

    # Submenu edge orde kedua
    def show_second_gradient(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return
        ops = ["Laplacian", "LoG", "Canny"]
        cmds = [
            lambda: self.update_image_async(laplacian_edge, self.current_image),
            lambda: self.update_image_async(log_edge, self.current_image),
            lambda: self.update_image_async(canny_edge, self.current_image)
        ]
        self.add_submenu_left2(ops, cmds, title="2'nd Gradient")

    # Menjalankan Compass Edge Detection
    def apply_compass(self):
        self.clear_left_submenu2()
        self.left_frame2.pack_forget()

        max_dim = 800
        img = self.current_image.copy()
        w, h = img.size
        if max(w, h) > max_dim:
            ratio = max_dim / max(w, h)
            img_small = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        else:
            img_small = img

        self.update_image_async(compass_edge, img_small)

    # Menampilkan submenu Segmentation
    def menu_segmentation(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        ops = ["Contour", "Watershed", "Watermark"]
        cmds = [
            lambda: self.update_image_async(contour_image, self.current_image),
            lambda: self.update_image_async(watershed_image, self.current_image),
            self.apply_watermark
        ]
        self.add_submenu_left(ops, cmds, title="Segmentation")

    # Submenu operasi aritmatik
    def show_arithmetic(self):
        ops = ["Add", "Subtract", "Multiply", "Divide"]
        cmds = [
            lambda: self.update_image_async(arithmetic, self.current_image, "add", 50),
            lambda: self.update_image_async(arithmetic, self.current_image, "sub", 50),
            lambda: self.update_image_async(arithmetic, self.current_image, "mul", 2),
            lambda: self.update_image_async(arithmetic, self.current_image, "div", 2)
        ]
        self.add_submenu_left2(ops, cmds, title="Arithmetic")

    # Submenu convolution dengan slider
    def show_convolution(self):
        self.clear_left_submenu2()
        self.left_frame2.pack(side="left", fill="y", before=self.image_frame)

        tk.Label(
            self.left_frame2,
            text="Convolution Filters",
            font=self.custom_font_bold,
            bg="#1C2833",
            fg="#ECF0F1",
            pady=10
        ).pack(side="top", fill="x")

        if not self.current_image:
            return

        original_image = self.current_image.copy()

        def create_slider(name, from_, to_, default, filter_func):
            frame = tk.Frame(self.left_frame2, bg="#1C2833")
            frame.pack(pady=10, fill="x")
            tk.Label(frame, text=name, font=self.custom_font_small, bg="#1C2833", fg="#ECF0F1").pack()

            def on_slide(val):
                val = int(val)
                if val == 0:
                    self.update_image(original_image)
                else:
                    try:
                        self.update_image_async(filter_func, original_image, val)
                    except TypeError:
                        self.update_image_async(filter_func, original_image)

            s = tk.Scale(
                frame,
                from_=from_,
                to=to_,
                orient="horizontal",
                bg="#1C2833",
                fg="#ECF0F1",
                length=140,
                command=on_slide
            )
            s.set(default)
            s.pack()

            self.register_slider(name, s, default)
            return s

        create_slider("Blur", 0, 10, 0, blur_image)
        create_slider("Sharpen", 0, 5, 0, sharpen_image)
        create_slider("Edge Detect", 0, 255, 0, edge_detect_image)

    # Submenu operasi boolean
    def show_boolean(self):
        ops = ["NOT", "AND", "OR", "XOR"]
        cmds = [
            self.apply_boolean_not,
            self.apply_boolean_and,
            self.apply_boolean_or,
            self.apply_boolean_xor
        ]
        self.add_submenu_left2(ops, cmds, title="Boolean")

    # Template submenu enhancement dengan slider
    def show_enhancement(self, label, func, from_, to_, default):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        self.clear_left_submenu2()
        self.left_frame2.pack(side="left", fill="y", before=self.image_frame)

        tk.Label(
            self.left_frame2,
            text=label,
            font=self.custom_font_bold,
            bg="#1C2833",
            fg="#ECF0F1",
            pady=10
        ).pack(side="top", fill="x")

        original_image = self.current_image.copy()

        def on_slide(val):
            factor = float(val)
            self.update_image_async(func, original_image, factor)

        slider = tk.Scale(
            self.left_frame2,
            from_=from_,
            to=to_,
            orient="horizontal",
            resolution=0.01 if isinstance(default, float) else 1,
            bg="#1C2833",
            fg="#ECF0F1",
            length=180,
            command=on_slide
        )
        slider.set(default)
        slider.pack(pady=20)

        self.active_slider = slider
        self.active_slider_func = func
        self.active_slider_label = label

        self.register_slider(label, slider, default)

    # Submenu operasi geometrik
    def show_geometrics(self):
        ops = ["Translation", "Rotation", "Zoom In", "Zoom Out", "Flip", "Crop"]
        cmds = [
            self.apply_translation,
            self.apply_rotation,
            lambda: self.apply_zooming("in"),
            lambda: self.apply_zooming("out"),
            self.apply_flipping,
            self.apply_cropping
        ]
        self.add_submenu_left2(ops, cmds, title="Geometrics")

    # Submenu pewarnaan / konversi warna
    def show_colouring(self):
        ops = ["Binary", "Grayscale", "RGB", "HSV", "CMY", "YUV", "YIQ", "Pseudo"]
        cmds = [
            self.apply_binary_fixed,
            self.apply_grayscale,
            self.apply_rgb,
            self.apply_hsv,
            self.apply_cmy,
            self.apply_yuv,
            self.apply_yiq,
            self.apply_pseudo
        ]
        self.add_submenu_left2(ops, cmds, title="Colouring")

    # Undo ke state gambar sebelumnya
    def undo_image(self):
        if self.history_stack:
            if self.current_image:
                self.redo_stack.append(self.current_image.copy())
            self.current_image = self.history_stack.pop()
            self.zoom_factor = 1.0
            self.display_image_fit()
            self.reset_all_sliders_to_default()
        else:
            messagebox.showinfo("Undo", "Tidak ada langkah sebelumnya.")

    # Redo ke state gambar berikutnya
    def redo_image(self):
        if self.redo_stack:
            if self.current_image:
                self.history_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.zoom_factor = 1.0
            self.display_image_fit()
            self.reset_all_sliders_to_default()
        else:
            messagebox.showinfo("Redo", "Tidak ada langkah Redo.")

    # Reset gambar ke kondisi awal
    def reset_image(self):
        if self.original_image is None:
            messagebox.showwarning("Peringatan", "Belum ada gambar untuk di-reset.")
            return

        self.current_image = self.original_image.copy()
        self.history_stack.clear()
        self.redo_stack.clear()
        self.zoom_factor = 1.0

        self.display_image_fit()
        self.reset_all_sliders_to_default()

    # Buka gambar dari file
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
        if path:
            img = Image.open(path)
            self.original_image = img.copy()
            self.current_image = img
            self.current_image_path = path
            self.history_stack.clear()
            self.redo_stack.clear()
            self.zoom_factor = 1.0
            self.display_image_fit()

    # Simpan gambar ke folder Downloads
    def save_image(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Tidak ada gambar untuk disimpan.")
            return

        home_dir = os.path.expanduser("~")
        downloads_dir = os.path.join(home_dir, "Downloads")

        if not os.path.isdir(downloads_dir):
            downloads_dir = home_dir

        if self.current_image_path:
            base_name = os.path.basename(self.current_image_path)
        else:
            base_name = "hasil_pcd.png"

        save_path = os.path.join(downloads_dir, base_name)

        try:
            self.current_image.save(save_path)
            messagebox.showinfo(
                "Sukses",
                f"Gambar berhasil disimpan di:\n{save_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Gagal menyimpan gambar:\n{e}"
            )

    # Simpan gambar sebagai file baru
    def save_as_image(self):
        if self.current_image:
            path = filedialog.asksaveasfilename(defaultextension=".png")
            if path:
                self.current_image.save(path)
                messagebox.showinfo("Sukses", "Disimpan sebagai file baru.")
        else:
            messagebox.showwarning("Peringatan", "Tidak ada gambar untuk disimpan.")

    # Update current_image dan refresh tampilan
    def update_image(self, img):
        self.current_image = img.copy()
        self.display_image_fit()

    # Menyesuaikan ukuran gambar dengan frame tampilan
    def display_image_fit(self):
        if self.is_showing_about:
            return
        if not self.current_image:
            return

        frame_w = self.image_frame.winfo_width()
        frame_h = self.image_frame.winfo_height()
        if frame_w > 50 and frame_h > 50:
            img_w, img_h = self.current_image.size
            ratio = min(frame_w / img_w, frame_h / img_h) * self.zoom_factor * 0.95
            new_w, new_h = max(1, int(img_w * ratio)), max(1, int(img_h * ratio))
            img_resized = self.current_image.resize((new_w, new_h), Image.LANCZOS)
            self.display_image = ImageTk.PhotoImage(img_resized)
            self.image_label.config(image=self.display_image, text="")
            self.image_label.place(relx=0.5, rely=0.5, anchor="center")

    # Handler ketika window di-resize
    def on_resize(self, event):
        if self.current_image and not self.is_showing_about:
            self.display_image_fit()

    # Terapkan operasi negatif
    def apply_negative(self):
        if self.current_image:
            self.update_image_async(negative, self.current_image)

    # Terapkan grayscale
    def apply_grayscale(self):
        if self.current_image:
            self.update_image_async(grayscale, self.current_image)

    # Terapkan thresholding dengan nilai input user
    def apply_thresholding(self):
        if self.current_image:
            t = simpledialog.askinteger(
                "Threshold", "Nilai threshold (0-255):", minvalue=0, maxvalue=255
            )
            if t is not None:
                self.update_image_async(threshold, self.current_image, t)

    # Terapkan biner tetap (threshold 128)
    def apply_binary_fixed(self):
        if self.current_image:
            self.update_image_async(
                lambda img: img.convert("L").point(
                    lambda p: 255 if p > 128 else 0
                ),
                self.current_image
            )

    # Tampilkan channel RGB terpisah dalam satu citra
    def apply_rgb(self):
        if self.current_image:
            def rgb_to_display(img):
                rgb_img = img.convert("RGB")
                r, g, b = rgb_img.split()
                r_img = Image.merge(
                    "RGB",
                    (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0))
                )
                g_img = Image.merge(
                    "RGB",
                    (Image.new("L", g.size, 0), g, Image.new("L", g.size, 0))
                )
                b_img = Image.merge(
                    "RGB",
                    (Image.new("L", b.size, 0), Image.new("L", b.size, 0), b)
                )
                total_width = r_img.width * 3
                max_height = r_img.height
                new_img = Image.new("RGB", (total_width, max_height))
                new_img.paste(r_img, (0, 0))
                new_img.paste(g_img, (r_img.width, 0))
                new_img.paste(b_img, (r_img.width * 2, 0))
                return new_img

            self.update_image_async(rgb_to_display, self.current_image)

    # Tampilkan HSV dengan komponen H,S,V sebagai RGB
    def apply_hsv(self):
        if self.current_image:
            def hsv_to_display(img):
                hsv_img = img.convert("HSV")
                h, s, v = hsv_img.split()
                merged = Image.merge("RGB", (h, s, v))
                return merged

            self.update_image_async(hsv_to_display, self.current_image)

    # Terapkan konversi ke CMY
    def apply_cmy(self):
        if self.current_image:
            self.update_image_async(to_cmy, self.current_image)

    # Terapkan konversi ke YUV
    def apply_yuv(self):
        if self.current_image:
            self.update_image_async(to_yuv, self.current_image)

    # Terapkan konversi ke YIQ
    def apply_yiq(self):
        if self.current_image:
            self.update_image_async(to_yiq, self.current_image)

    # Terapkan pseudo-color
    def apply_pseudo(self):
        if self.current_image:
            self.update_image_async(pseudo_color, self.current_image)

    # Terapkan operasi boolean NOT
    def apply_boolean_not(self):
        if self.current_image:
            self.update_image_async(boolean_not, self.current_image)

    # Terapkan operasi boolean AND dengan gambar lain
    def apply_boolean_and(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return
        f = filedialog.askopenfilename(title="Pilih gambar kedua untuk AND")
        if f:
            img2 = Image.open(f).resize(self.current_image.size)
            self.update_image_async(boolean_and, self.current_image, img2)

    # Terapkan operasi boolean OR
    def apply_boolean_or(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return
        f = filedialog.askopenfilename(title="Pilih gambar kedua untuk OR")
        if f:
            img2 = Image.open(f).resize(self.current_image.size)
            self.update_image_async(boolean_or, self.current_image, img2)

    # Terapkan operasi boolean XOR
    def apply_boolean_xor(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return
        f = filedialog.askopenfilename(title="Pilih gambar kedua untuk XOR")
        if f:
            img2 = Image.open(f).resize(self.current_image.size)
            self.update_image_async(boolean_xor, self.current_image, img2)

    # Terapkan convolution dengan kernel pilihan user
    def apply_convolution(self):
        kernels = {
            "blur": np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.float32) / 9.0,
            "sharpen": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32),
            "edge": np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
        }

        pilihan = simpledialog.askstring(
            "Convolution", "Pilih kernel: blur / sharpen / edge"
        )
        if not pilihan:
            return

        key = pilihan.strip().lower()
        if key not in kernels:
            messagebox.showinfo(
                "Info", "Kernel tidak dikenali. Gunakan: blur, sharpen, atau edge"
            )
            return

        kernel = kernels[key]
        self.update_image_async(convolution, self.current_image, kernel)

    # Terapkan Fourier Transform
    def apply_fourier(self):
        self.clear_left_submenu2()
        self.left_frame2.pack_forget()
        self.update_image_async(fourier_transform, self.current_image)

    # Terapkan translasi (geser gambar)
    def apply_translation(self):
        if self.current_image:
            self.update_image_async(translation, self.current_image, 50, 50)

    # Terapkan rotasi
    def apply_rotation(self):
        if self.current_image:
            self.update_image_async(rotation, self.current_image, 45)

    # Zoom in / out dengan mengubah faktor zoom
    def apply_zooming(self, direction="in"):
        if self.current_image:
            self.history_stack.append(self.current_image.copy())
            self.redo_stack.clear()
            if direction == "in":
                self.zoom_factor *= 1.2
            else:
                self.zoom_factor *= 0.8
            self.display_image_fit()

    # Flip horizontal gambar
    def apply_flipping(self):
        if self.current_image:
            self.update_image_async(flipping, self.current_image, "horizontal")

    # Crop bagian tengah gambar
    def apply_cropping(self):
        if self.current_image:
            w, h = self.current_image.size
            self.update_image_async(cropping, self.current_image, (50, 50, w - 50, h - 50))

    # Tampilkan slider brightness
    def show_brightness(self):
        self.show_enhancement("Brightness", adjust_brightness, 0.0, 3.0, 1.0)

    # Tampilkan slider contrast
    def show_contrast(self):
        self.show_enhancement("Contrast", adjust_contrast, 0.0, 3.0, 1.0)

    # Terapkan histogram equalization
    def apply_hist_eq(self):
        self.update_image_async(histogram_equalization, self.current_image)
        self.clear_left_submenu2()
        self.left_frame2.pack_forget()
    
    def apply_watermark(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        text = simpledialog.askstring("Watermark", "Teks watermark:")
        if not text or text.strip() == "":
            return  # batal / kosong

        # Jalanin async biar UI nggak nge-freeze
        self.update_image_async(watermark_image, self.current_image, text.strip())

    # Submenu smoothing (spatial dan frequency)
    def show_smoothing(self):
        self.clear_left_submenu2()
        self.left_frame2.pack(side="left", fill="y", before=self.image_frame)

        tk.Label(
            self.left_frame2,
            text="Smoothing",
            font=self.custom_font_bold,
            bg="#1C2833",
            fg="#ECF0F1",
            pady=10
        ).pack(side="top", fill="x")

        spatial_frame = tk.LabelFrame(
            self.left_frame2,
            text="Spatial Domain",
            bg="#1C2833",
            fg="#ECF0F1",
            font=self.custom_font_small,
            padx=5,
            pady=5
        )
        spatial_frame.pack(fill="x", pady=(5, 10))

        spatial_ops = ["Lowpass Filtering", "Median Filtering"]
        spatial_cmds = [
            lambda: self.update_image_async(smoothing, self.current_image, "lowpass"),
            lambda: self.update_image_async(smoothing, self.current_image, "median")
        ]
        for i, op in enumerate(spatial_ops):
            tk.Button(
                spatial_frame,
                text=op,
                font=self.custom_font_small,
                bg="#5CA0BF",
                fg="#ECF0F1",
                activebackground="#1664A0",
                activeforeground="#ffffff",
                relief="flat",
                width=16,
                pady=6,
                command=spatial_cmds[i],
                cursor="hand2",
                bd=0
            ).pack(pady=2, padx=5)

        freq_frame = tk.LabelFrame(
            self.left_frame2,
            text="Frequency Domain",
            bg="#1C2833",
            fg="#ECF0F1",
            font=self.custom_font_small,
            padx=5,
            pady=5
        )
        freq_frame.pack(fill="x", pady=(5, 10))

        freq_ops = ["ILPF", "BLPF"]
        freq_cmds = [
            lambda: self.update_image_async(smoothing, self.current_image, "ilpf"),
            lambda: self.update_image_async(smoothing, self.current_image, "blpf")
        ]
        for i, op in enumerate(freq_ops):
            tk.Button(
                freq_frame,
                text=op,
                font=self.custom_font_small,
                bg="#5CA0BF",
                fg="#ECF0F1",
                activebackground="#1664A0",
                activeforeground="#ffffff",
                relief="flat",
                width=16,
                pady=6,
                command=freq_cmds[i],
                cursor="hand2",
                bd=0
            ).pack(pady=2, padx=5)

    # Submenu sharpening (spatial dan frequency)
    def show_sharpening(self):
        if not self.current_image:
            self.showwarning("Peringatan", "Buka gambar terlebih dahulu.")
            return

        self.clear_left_submenu2()
        self.left_frame2.pack(side="left", fill="y", before=self.image_frame)

        tk.Label(
            self.left_frame2,
            text="Sharpening",
            font=self.custom_font_bold,
            bg="#1C2833",
            fg="#ECF0F1",
            pady=10
        ).pack(side="top", fill="x")

        original_image = self.current_image.copy()

        spatial_frame = tk.LabelFrame(
            self.left_frame2,
            text="Spatial Domain",
            bg="#1C2833",
            fg="#ECF0F1",
            font=self.custom_font_small,
            padx=5,
            pady=5
        )
        spatial_frame.pack(fill="x", pady=(5, 10))

        spatial_ops = {
            "Highpass Filtering": "highpass",
            "Highboost Filtering": "highboost"
        }

        for op_name, mode in spatial_ops.items():
            tk.Button(
                spatial_frame,
                text=op_name,
                font=self.custom_font_small,
                bg="#5CA0BF",
                fg="#ECF0F1",
                activebackground="#1664A0",
                activeforeground="#ffffff",
                relief="flat",
                width=16,
                pady=6,
                command=lambda m=mode: self.update_image_async(
                    sharpening,
                    original_image.copy(),
                    m,
                    10
                )
            ).pack(pady=5)

        freq_frame = tk.LabelFrame(
            self.left_frame2,
            text="Frequency Domain",
            bg="#1C2833",
            fg="#ECF0F1",
            font=self.custom_font_small,
            padx=5,
            pady=5
        )
        freq_frame.pack(fill="x", pady=(5, 10))

        freq_ops = {
            "IHPF": "ihpf",
            "BHPF": "bhpf"
        }

        for op_name, mode in freq_ops.items():
            tk.Button(
                freq_frame,
                text=op_name,
                font=self.custom_font_small,
                bg="#5CA0BF",
                fg="#ECF0F1",
                activebackground="#1664A0",
                activeforeground="#ffffff",
                relief="flat",
                width=16,
                pady=6,
                command=lambda m=mode: self.update_image_async(
                    sharpening,
                    original_image.copy(),
                    m,
                    60
                )
            ).pack(pady=5)

    # Terapkan geometric correction
    def apply_correction(self):
        self.clear_left_submenu2()
        self.left_frame2.pack_forget()

        try:
            self.update_image_async(correction, self.current_image)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menerapkan correction: {str(e)}")

    # Menampilkan halaman About
    def show_info(self):
        self.clear_left_submenu()
        self.clear_left_submenu2()
        self.left_frame2.pack_forget()
        self.clear_slider_registry()

        if hasattr(self, "info_frame") and self.info_frame:
            try:
                if self.info_frame.winfo_exists():
                    self.info_frame.destroy()
            except Exception:
                pass
            self.info_frame = None

        self.is_showing_about = True
        self.image_label.place_forget()

        self.info_frame = tk.Frame(self.image_frame, bg="#1a1a1a")
        self.info_frame.pack(fill="both", expand=True)

        tk.Label(
            self.info_frame,
            text="About",
            font=self.custom_font_medium,
            bg="#1a1a1a",
            fg="#ECF0F1"
        ).pack(pady=(18, 6))

        tk.Label(
            self.info_frame,
            text="Info Tim Developer\n--------------------------",
            font=self.custom_font,
            bg="#1a1a1a",
            fg="#ECF0F1",
            justify="center"
        ).pack(pady=(0, 12))

        tk.Label(
            self.info_frame,
            text="Tutorial :",
            font=self.custom_font_bold,
            bg="#1a1a1a",
            fg="#ECF0F1",
            anchor="w"
        ).pack(pady=(0, 6), padx=20, fill="x")

        github_label = tk.Label(
            self.info_frame,
            text="GitHub",
            font=self.custom_font,
            bg="#1a1a1a",
            fg="#1ABC9C",
            cursor="hand2"
        )
        github_label.pack(anchor="w", pady=2, padx=20)
        github_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/username"))

        youtube_label = tk.Label(
            self.info_frame,
            text="YouTube",
            font=self.custom_font,
            bg="#1a1a1a",
            fg="#E74C3C",
            cursor="hand2"
        )
        youtube_label.pack(anchor="w", pady=2, padx=20)
        youtube_label.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new(
                "https://youtu.be/hv-tflI7pM4?si=HhwkxAqZJrne_OT3"
            )
        )

    # Popup peringatan dengan animasi dan posisi tengah
    def showwarning(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.title("")
        popup.geometry("300x180")
        popup.configure(bg="#2c3e50")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 90
        popup.geometry(f"+{x}+{y}")

        popup.attributes("-alpha", 0.0)
        for i in range(0, 11):
            popup.after(i * 20, lambda i=i: popup.attributes("-alpha", i / 10))

        tk.Label(
            popup,
            text=title,
            font=("Poppins", 13, "bold"),
            fg="#ECF0F1",
            bg="#2c3e50"
        ).pack(pady=(15, 5))

        tk.Label(
            popup,
            text=message,
            font=("Poppins", 10),
            fg="#BDC3C7",
            bg="#2c3e50",
            wraplength=260,
            justify="center"
        ).pack(pady=(0, 15))

        ok_btn = tk.Button(
            popup,
            text="OK",
            font=("Poppins", 10, "bold"),
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",
            activeforeground="white",
            relief="flat",
            width=10,
            command=popup.destroy
        )
        ok_btn.pack()

        popup.lift()
        popup.grab_set()

    # Placeholder untuk fitur yang belum siap
    def not_ready(self):
        messagebox.showinfo("Info", "Fitur belum tersedia.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiPCD(root)
    root.mainloop()
