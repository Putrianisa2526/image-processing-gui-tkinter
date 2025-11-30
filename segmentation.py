from PIL import Image, ImageFilter, ImageDraw, ImageFont
import numpy as np

# Membuat efek contour pada gambar
def contour_image(img):
    gray = img.convert("L")
    contour = gray.filter(ImageFilter.CONTOUR)
    return contour.convert("RGB")

# Segmentasi watershed sederhana
def watershed_image(img):
    gray = img.convert("L")
    img_np = np.array(gray, dtype=np.int32)

    gx = np.zeros_like(img_np)
    gy = np.zeros_like(img_np)

    gx[:, :-1] = np.abs(img_np[:, 1:] - img_np[:, :-1])
    gy[:-1, :] = np.abs(img_np[1:, :] - img_np[:-1, :])

    grad = gx + gy
    grad = np.clip(grad, 0, 255).astype(np.uint8)

    thresh = 30
    mask = grad > thresh

    np.random.seed(42)
    color_map = np.random.randint(0, 255, (256, 3), dtype=np.uint8)

    seg_img = np.zeros((img_np.shape[0], img_np.shape[1], 3), dtype=np.uint8)
    seg_img[mask] = color_map[grad[mask]]

    return Image.fromarray(seg_img)

def watermark_image(img, text="watermark"):
    """
    Menambahkan watermark teks berulang secara diagonal
    di seluruh gambar (seperti contoh Google tadi).
    """
    base = img.convert("RGBA")
    w, h = base.size

    # Layer transparan untuk seluruh watermark
    wm_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Ukuran font relatif ke gambar
    font_size = max(w, h) // 25
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Hitung ukuran teks
    dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)
    try:
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except:
        text_w, text_h = dummy_draw.textsize(text, font=font)

    # Bikin satu "stamp" teks, lalu diputar miring
    pad = 10
    stamp = Image.new("RGBA", (text_w + 2 * pad, text_h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(stamp)
    # warna abu-abu semi transparan
    d.text((pad, pad), text, font=font, fill=(150, 150, 150, 180))

    # Putar miring (negatif = miring ke kiri atas / kanan bawah)
    angle = -30
    stamp = stamp.rotate(angle, expand=True)

    sw, sh = stamp.size

    # Jarak antar watermark (boleh di-adjust kalau mau lebih rapat / renggang)
    step_x = int(sw * 2)
    step_y = int(sh * 2)

    # Tile stamp ke seluruh gambar
    for y_pos in range(-sh, h + sh, step_y):
        for x_pos in range(-sw, w + sw, step_x):
            wm_layer.alpha_composite(stamp, (x_pos, y_pos))

    # Gabungkan dengan gambar asli
    combined = Image.alpha_composite(base, wm_layer)
    return combined.convert("RGB")
