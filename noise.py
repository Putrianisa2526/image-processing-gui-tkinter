import numpy as np
from PIL import Image

# Konversi PIL Image ke array float32
def _to_array(img):
    if img.mode == "RGB":
        arr = np.asarray(img, dtype=np.float32)
    else:
        arr = np.asarray(img.convert("L"), dtype=np.float32)
    return arr

# Konversi array NumPy ke PIL Image
def _to_image(arr, mode="L"):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    if len(arr.shape) == 3 and arr.shape[2] == 3:
        return Image.fromarray(arr, mode="RGB")
    else:
        return Image.fromarray(arr, mode="L")

# Terapkan fungsi noise ke tiap channel jika RGB
def _apply_noise_to_rgb(img, noise_func):
    if img.mode == "RGB":
        arr = np.asarray(img, dtype=np.float32)
        noisy = np.zeros_like(arr)
        for c in range(3):  # R, G, B
            noisy[..., c] = noise_func(arr[..., c])
        return _to_image(noisy, "RGB")
    else:
        arr = np.asarray(img.convert("L"), dtype=np.float32)
        noisy = noise_func(arr)
        return _to_image(noisy, "L")

# Tambah noise Gaussian
def add_gaussian_noise(img, mean=0, sigma=30):
    def noise_func(channel):
        noise = np.random.normal(mean, sigma, channel.shape)
        return channel + noise
    return _apply_noise_to_rgb(img, noise_func)

# Tambah noise Rayleigh
def add_rayleigh_noise(img, scale=40):
    def noise_func(channel):
        noise = np.random.rayleigh(scale, channel.shape)
        return channel + noise - scale
    return _apply_noise_to_rgb(img, noise_func)

# Tambah noise Erlang (Gamma)
def add_erlang_noise(img, shape_param=3, scale=20):
    def noise_func(channel):
        noise = np.random.gamma(shape_param, scale, channel.shape)
        return channel + noise - (shape_param * scale / 2)
    return _apply_noise_to_rgb(img, noise_func)

# Tambah noise Eksponensial
def add_exponential_noise(img, scale=35):
    def noise_func(channel):
        noise = np.random.exponential(scale, channel.shape)
        return channel + noise - scale / 2
    return _apply_noise_to_rgb(img, noise_func)

# Tambah noise Uniform
def add_uniform_noise(img, low=-50, high=50):
    def noise_func(channel):
        noise = np.random.uniform(low, high, channel.shape)
        return channel + noise
    return _apply_noise_to_rgb(img, noise_func)

# Tambah noise salt & pepper
def add_impulse_noise(img, amount=0.05, salt_vs_pepper=0.5):
    if img.mode == "RGB":
        arr = np.asarray(img, dtype=np.float32)
        noisy = arr.copy()
        total_pixels = arr.shape[0] * arr.shape[1]

        num_salt = int(amount * total_pixels * salt_vs_pepper)
        num_pepper = int(amount * total_pixels * (1.0 - salt_vs_pepper))

        # Salt (putih)
        coords = (
            np.random.randint(0, arr.shape[0], num_salt),
            np.random.randint(0, arr.shape[1], num_salt)
        )
        noisy[coords[0], coords[1], :] = 255

        # Pepper (hitam)
        coords = (
            np.random.randint(0, arr.shape[0], num_pepper),
            np.random.randint(0, arr.shape[1], num_pepper)
        )
        noisy[coords[0], coords[1], :] = 0

        return _to_image(noisy, "RGB")

    else:
        arr = np.asarray(img.convert("L"), dtype=np.float32)
        noisy = arr.copy()
        total_pixels = arr.size

        num_salt = int(amount * total_pixels * salt_vs_pepper)
        num_pepper = int(amount * total_pixels * (1.0 - salt_vs_pepper))

        # Salt (putih)
        coords = (
            np.random.randint(0, arr.shape[0], num_salt),
            np.random.randint(0, arr.shape[1], num_salt)
        )
        noisy[coords] = 255

        # Pepper (hitam)
        coords = (
            np.random.randint(0, arr.shape[0], num_pepper),
            np.random.randint(0, arr.shape[1], num_pepper)
        )
        noisy[coords] = 0

        return _to_image(noisy, "L")
