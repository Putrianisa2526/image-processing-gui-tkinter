from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

# === ENHANCEMENT OPERATIONS ===

def adjust_brightness(img: Image.Image, factor=1.0) -> Image.Image:
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def adjust_contrast(img: Image.Image, factor=1.0) -> Image.Image:
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)

def histogram_equalization(img: Image.Image) -> Image.Image:
    if img.mode != "L":
        img = img.convert("L")
    return ImageOps.equalize(img)

def smoothing(img: Image.Image, method="lowpass") -> Image.Image:
    """
    Fungsi smoothing / filter citra.

    method:
        "lowpass"   -> Spatial Domain Lowpass Filtering
        "median"    -> Spatial Domain Median Filtering
        "ilpf"      -> Frequency Domain Ideal Low Pass Filter
        "blpf"      -> Frequency Domain Butterworth Low Pass Filter
    """
    img_copy = img.copy()

    if method == "lowpass":
        # Spatial Domain: simple average filter
        return img_copy.filter(ImageFilter.BoxBlur(3))

    elif method == "median":
        # Spatial Domain: median filter
        return img_copy.filter(ImageFilter.MedianFilter(size=5))

    elif method in ["ilpf", "blpf"]:
        # Frequency Domain
        return frequency_lowpass_filter(img_copy, filter_type="ideal" if method=="ilpf" else "butterworth", cutoff=80, order=2)

    else:
        raise ValueError("Method smoothing tidak dikenali.")


def frequency_lowpass_filter(img, filter_type="ideal", cutoff=30, order=2):
    """
    Filter Lowpass di Domain Frekuensi.
    filter_type: "ideal" atau "butterworth"
    cutoff: radius cutoff
    order: hanya untuk butterworth
    """
    # Konversi ke grayscale
    img_gray = img.convert("L")
    img_arr = np.array(img_gray, dtype=np.float32)

    # FFT
    f = np.fft.fft2(img_arr)
    fshift = np.fft.fftshift(f)

    # Buat filter mask
    rows, cols = img_arr.shape
    crow, ccol = rows//2, cols//2
    Y, X = np.ogrid[:rows, :cols]
    distance = np.sqrt((X - ccol)**2 + (Y - crow)**2)

    if filter_type == "ideal":
        mask = distance <= cutoff
    elif filter_type == "butterworth":
        mask = 1 / (1 + (distance / cutoff)**(2*order))
    else:
        raise ValueError("filter_type harus 'ideal' atau 'butterworth'")

    # Terapkan mask
    fshift_filtered = fshift * mask

    # IFFT
    f_ishift = np.fft.ifftshift(fshift_filtered)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    img_back = np.clip(img_back, 0, 255).astype(np.uint8)

    return Image.fromarray(img_back)

def sharpening(img: Image.Image, method="highpass", intensity=1) -> Image.Image:
    img_copy = img.copy()

    if method == "highpass":
        kernel = [-1,-1,-1,
                  -1,8,-1,
                  -1,-1,-1]
        # Kalikan kernel agar efek terlihat signifikan
        kernel = [k * intensity for k in kernel]
        return img_copy.filter(ImageFilter.Kernel((3,3), kernel, scale=None, offset=0))

    elif method == "highboost":
        kernel = [-1,-1,-1,
                  -1,9,-1,
                  -1,-1,-1]
        kernel = [k * intensity for k in kernel]
        return img_copy.filter(ImageFilter.Kernel((3,3), kernel, scale=None, offset=0))

    elif method in ["ihpf", "bhpf"]:
        # frequency highpass dengan cutoff sebagai intensity
        cutoff = max(intensity, 1)  # pastikan cutoff >=1
        return frequency_highpass_filter(
            img_copy,
            filter_type="ideal" if method=="ihpf" else "butterworth",
            cutoff=cutoff,
            order=2
        )

    else:
        raise ValueError("Method sharpening tidak dikenali.")



def frequency_highpass_filter(img, filter_type="ideal", cutoff=30, order=2):
    """
    Filter Highpass di Domain Frekuensi.
    filter_type: "ideal" atau "butterworth"
    cutoff: radius cutoff
    order: hanya untuk butterworth
    """
    # Konversi ke grayscale
    img_gray = img.convert("L")
    img_arr = np.array(img_gray, dtype=np.float32)

    # FFT
    f = np.fft.fft2(img_arr)
    fshift = np.fft.fftshift(f)

    # Buat filter mask
    rows, cols = img_arr.shape
    crow, ccol = rows//2, cols//2
    Y, X = np.ogrid[:rows, :cols]
    distance = np.sqrt((X - ccol)**2 + (Y - crow)**2)

    if filter_type == "ideal":
        mask = distance > cutoff
    elif filter_type == "butterworth":
        mask = 1 / (1 + (cutoff / distance)**(2*order))
        mask[crow, ccol] = 0  # hindari divide by zero
    else:
        raise ValueError("filter_type harus 'ideal' atau 'butterworth'")

    # Terapkan mask
    fshift_filtered = fshift * mask

    # IFFT
    f_ishift = np.fft.ifftshift(fshift_filtered)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    img_back = np.clip(img_back, 0, 255).astype(np.uint8)

    return Image.fromarray(img_back)


from PIL import Image, ImageEnhance, ImageOps

def correction(img: Image.Image) -> Image.Image:
    # Pastikan gambar dalam mode RGB
    img = img.convert("RGB")

    # 1️⃣ Koreksi kontras otomatis
    corrected = ImageOps.autocontrast(img)

    # 2️⃣ Tingkatkan saturasi warna sedikit (1.2x)
    enhancer_color = ImageEnhance.Color(corrected)
    corrected = enhancer_color.enhance(1.2)

    # 3️⃣ Sedikit cerahkan gambar (1.05x)
    enhancer_brightness = ImageEnhance.Brightness(corrected)
    corrected = enhancer_brightness.enhance(1.05)

    return corrected

