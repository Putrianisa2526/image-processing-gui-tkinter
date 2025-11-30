from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np

# Membuat citra negatif
def negative(img: Image.Image) -> Image.Image:
    arr = np.array(img)
    arr = 255 - arr
    return Image.fromarray(arr.astype(np.uint8))

# Mengubah citra ke grayscale
def grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L")

# Operasi aritmatika pada citra (add, sub, mul, div)
def arithmetic(img: Image.Image, op="add", value=50) -> Image.Image:
    arr = np.array(img, dtype=np.int16)
    if op == "add":
        arr = arr + value
    elif op == "sub":
        arr = arr - value
    elif op == "mul":
        arr = arr * value
    elif op == "div":
        arr = arr / value
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

# Operasi NOT (invers) pada citra
def boolean_not(img: Image.Image) -> Image.Image:
    arr = np.array(img.convert("L"))
    arr = 255 - arr
    return Image.fromarray(arr.astype(np.uint8))

# Operasi logika AND dua citra
def boolean_and(img1: Image.Image, img2: Image.Image) -> Image.Image:
    a1 = np.array(img1.convert("L"))
    a2 = np.array(img2.convert("L"))
    return Image.fromarray(np.bitwise_and(a1, a2).astype(np.uint8))

# Operasi logika OR dua citra
def boolean_or(img1: Image.Image, img2: Image.Image) -> Image.Image:
    a1 = np.array(img1.convert("L"))
    a2 = np.array(img2.convert("L"))
    return Image.fromarray(np.bitwise_or(a1, a2).astype(np.uint8))

# Operasi logika XOR dua citra
def boolean_xor(img1: Image.Image, img2: Image.Image) -> Image.Image:
    a1 = np.array(img1.convert("L"))
    a2 = np.array(img2.convert("L"))
    return Image.fromarray(np.bitwise_xor(a1, a2).astype(np.uint8))

# Translasi (geser) citra
def translation(img: Image.Image, tx=50, ty=50) -> Image.Image:
    return img.transform(img.size, Image.AFFINE, (1, 0, tx, 0, 1, ty))

# Rotasi citra
def rotation(img: Image.Image, angle=45) -> Image.Image:
    return img.rotate(angle, expand=True)

# Zoom (resize) citra dengan faktor
def zooming(img: Image.Image, factor=1.2) -> Image.Image:
    w, h = img.size
    return img.resize((int(w * factor), int(h * factor)))

# Flip citra horizontal/vertical
def flipping(img: Image.Image, mode="horizontal") -> Image.Image:
    if mode == "horizontal":
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        return img.transpose(Image.FLIP_TOP_BOTTOM)

# Crop (potong) bagian citra
def cropping(img: Image.Image, box=(50, 50, 200, 200)) -> Image.Image:
    return img.crop(box)

# Thresholding biner sederhana
def threshold(img: Image.Image, t=128) -> Image.Image:
    gray = img.convert("L")
    return gray.point(lambda p: 255 if p > t else 0)

# Mengubah citra ke mode biner
def to_binary(img: Image.Image) -> Image.Image:
    return img.convert("1")

# Konversi ke RGB
def to_rgb(img: Image.Image) -> Image.Image:
    return img.convert("RGB")

# Konversi ke HSV
def to_hsv(img: Image.Image) -> Image.Image:
    return img.convert("HSV")

# Konversi ke CMY
def to_cmy(img: Image.Image) -> Image.Image:
    rgb = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
    cmy = 1 - rgb
    return Image.fromarray((cmy * 255).astype(np.uint8))

# Konversi ke YUV
def to_yuv(img: Image.Image) -> Image.Image:
    rgb = np.array(img.convert("RGB"), dtype=np.float32)
    transform = np.array([
        [0.299,    0.587,    0.114],
        [-0.14713, -0.28886, 0.436],
        [0.615,   -0.51499, -0.10001]
    ])
    yuv = np.dot(rgb, transform.T)
    yuv = np.clip(yuv, 0, 255)
    return Image.fromarray(yuv.astype(np.uint8))

# Konversi ke YIQ
def to_yiq(img: Image.Image) -> Image.Image:
    rgb = np.array(img.convert("RGB"), dtype=np.float32)
    transform = np.array([
        [0.299,     0.587,     0.114],
        [0.595716, -0.274453, -0.321263],
        [0.211456, -0.522591,  0.311135]
    ])
    yiq = np.dot(rgb, transform.T)
    yiq = np.clip(yiq, 0, 255)
    return Image.fromarray(yiq.astype(np.uint8))

# Pseudo-color dari citra grayscale
def pseudo_color(img: Image.Image) -> Image.Image:
    gray = np.array(img.convert("L"))
    pseudo = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
    pseudo[..., 0] = np.where(gray < 85, 255 - 3 * gray, 0)
    pseudo[..., 1] = np.where(
        (gray >= 85) & (gray < 170),
        3 * (gray - 85),
        255 - 3 * (gray - 170)
    )
    pseudo[..., 2] = np.where(gray >= 170, 3 * (gray - 170), 0)
    return Image.fromarray(pseudo)

# Convolution manual untuk grayscale/RGB
def convolution(img: Image.Image, kernel=None) -> Image.Image:
    if kernel is None:
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)

    arr = np.array(img).astype(np.float32)
    if arr.ndim == 2:
        arr = arr[:, :, None]

    h, w, c = arr.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(arr, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode="edge")
    out = np.zeros_like(arr)

    for y in range(h):
        for x in range(w):
            for ch in range(c):
                region = padded[y:y + kh, x:x + kw, ch]
                out[y, x, ch] = np.sum(region * kernel)

    out = np.clip(out, 0, 255).astype(np.uint8)

    if out.shape[2] == 1:
        return Image.fromarray(out[:, :, 0], mode="L")
    return Image.fromarray(out, mode="RGB")

# Blur citra dengan Gaussian
def blur_image(img: Image.Image, intensity=1):
    return img.filter(ImageFilter.GaussianBlur(radius=intensity))

# Menajamkan citra dengan faktor intensity
def sharpen_image(img: Image.Image, intensity=1):
    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(1 + intensity)

# Deteksi tepi dengan Sobel dan threshold
def edge_detect_image(img: Image.Image, threshold_val=100):
    gray = np.array(img.convert("L"), dtype=np.float32)

    Kx = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ], dtype=np.float32)

    Ky = np.array([
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ], dtype=np.float32)

    def convolve(img_arr, kernel):
        kh, kw = kernel.shape
        pad_h, pad_w = kh // 2, kw // 2
        padded = np.pad(img_arr, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        h, w = img_arr.shape
        output = np.zeros_like(img_arr)
        for i in range(h):
            for j in range(w):
                region = padded[i:i + kh, j:j + kw]
                output[i, j] = np.sum(region * kernel)
        return output

    Gx = convolve(gray, Kx)
    Gy = convolve(gray, Ky)
    G = np.sqrt(Gx ** 2 + Gy ** 2)
    G = np.clip(G, 0, 255)
    G = (G > threshold_val) * 255
    return Image.fromarray(G.astype(np.uint8))

# Fourier transform dengan pewarnaan kanal RGB
def fourier_transform(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float32)
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]

    total = R + G + B + 1e-5
    R_ratio = R / total
    G_ratio = G / total
    B_ratio = B / total

    gray = arr.mean(axis=2)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.log1p(np.abs(fshift))
    magnitude = 255 * (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min())

    out = np.zeros_like(arr, dtype=np.uint8)
    out[..., 0] = (magnitude * R_ratio).astype(np.uint8)
    out[..., 1] = (magnitude * G_ratio).astype(np.uint8)
    out[..., 2] = (magnitude * B_ratio).astype(np.uint8)
    return Image.fromarray(out)
