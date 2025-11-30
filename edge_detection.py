import numpy as np
from PIL import Image

# Konversi gambar ke array grayscale (float)
def _to_gray(img):
    if img.mode != "L":
        return np.array(img.convert("L"), dtype=np.float32)
    return np.array(img, dtype=np.float32)

# Konversi array grayscale ke objek Image
def _to_image(arr):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "L")

# Convolution 2D sederhana untuk array grayscale
def _convolve(arr, kernel):
    h, w = arr.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(arr, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
    out = np.zeros_like(arr)
    for i in range(h):
        for j in range(w):
            out[i, j] = np.sum(padded[i:i+kh, j:j+kw] * kernel)
    return out

# Deteksi tepi dengan operator Sobel
def sobel_edge(img):
    arr = _to_gray(img)
    Kx = np.array([[1, 0, -1],
                   [2, 0, -2],
                   [1, 0, -1]], float)
    Ky = np.array([[1, 2, 1],
                   [0, 0, 0],
                   [-1, -2, -1]], float)
    gx = _convolve(arr, Kx)
    gy = _convolve(arr, Ky)
    return _to_image(np.sqrt(gx**2 + gy**2))

# Deteksi tepi dengan operator Prewitt
def prewitt_edge(img):
    arr = _to_gray(img)
    Kx = np.array([[1, 0, -1],
                   [1, 0, -1],
                   [1, 0, -1]], float)
    Ky = np.array([[1, 1, 1],
                   [0, 0, 0],
                   [-1, -1, -1]], float)
    gx = _convolve(arr, Kx)
    gy = _convolve(arr, Ky)
    return _to_image(np.sqrt(gx**2 + gy**2))

# Deteksi tepi dengan operator Roberts
def roberts_edge(img):
    arr = _to_gray(img)
    Kx = np.array([[1, 0],
                   [0, -1]], float)
    Ky = np.array([[0, 1],
                   [-1, 0]], float)
    gx = _convolve(arr, Kx)
    gy = _convolve(arr, Ky)
    return _to_image(np.sqrt(gx**2 + gy**2))

# Deteksi tepi dengan operator Laplacian
def laplacian_edge(img):
    arr = _to_gray(img)
    kernel = np.array([[0, 1, 0],
                       [1, -4, 1],
                       [0, 1, 0]], float)
    return _to_image(np.abs(_convolve(arr, kernel)))

# Deteksi tepi dengan LoG (Gaussian blur + Laplacian)
def log_edge(img):
    arr = _to_gray(img)
    gauss = np.array([[1, 2, 1],
                      [2, 4, 2],
                      [1, 2, 1]], float) / 16
    blurred = _convolve(arr, gauss)
    lap_kernel = np.array([[0, 1, 0],
                           [1, -4, 1],
                           [0, 1, 0]], float)
    return _to_image(np.abs(_convolve(blurred, lap_kernel)))

# Deteksi tepi ala Canny sederhana (pakai magnitude dan threshold)
def canny_edge(img, low=50, high=150):
    arr = _to_gray(img)
    Kx = np.array([[1, 0, -1],
                   [2, 0, -2],
                   [1, 0, -1]], float)
    Ky = np.array([[1, 2, 1],
                   [0, 0, 0],
                   [-1, -2, -1]], float)
    gx = _convolve(arr, Kx)
    gy = _convolve(arr, Ky)
    mag = np.sqrt(gx**2 + gy**2)
    edges = np.where((mag >= low) & (mag <= high), 255, 0)
    return _to_image(edges)

# Deteksi tepi dengan operator Kirsch (kompas)
def compass_edge(img):
    arr = _to_gray(img)
    kirsch_kernels = [
        np.array([[5, 5, 5],
                  [-3, 0, -3],
                  [-3, -3, -3]]),
        np.array([[5, 5, -3],
                  [5, 0, -3],
                  [-3, -3, -3]]),
        np.array([[5, -3, -3],
                  [5, 0, -3],
                  [-3, -3, 5]]),
        np.array([[-3, -3, -3],
                  [5, 0, -3],
                  [5, 5, -3]]),
        np.array([[-3, -3, -3],
                  [-3, 0, -3],
                  [5, 5, 5]]),
        np.array([[-3, -3, -3],
                  [-3, 0, 5],
                  [-3, 5, 5]]),
        np.array([[-3, -3, 5],
                  [-3, 0, 5],
                  [-3, -3, 5]]),
        np.array([[5, 5, 5],
                  [-3, 0, -3],
                  [-3, -3, -3]])
    ]
    responses = np.array([_convolve(arr, k) for k in kirsch_kernels])
    return _to_image(np.max(responses, axis=0))
