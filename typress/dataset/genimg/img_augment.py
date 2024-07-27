from PIL import Image, ImageFilter
import numpy as np
import random
import cv2
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


def add_gaussian_noise(image, mean, std):
    image_array = np.asarray(image)
    noise = np.random.normal(mean, std, image_array.shape)
    noisy_image = image_array + noise
    noisy_image = np.clip(noisy_image, 0, 255)
    return Image.fromarray(noisy_image.astype(np.uint8))


def rotate_image(image, angle):
    return image.rotate(
        angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor="white"
    )


def generate_distorted_points(img, segment, threshold):
    cut = img.shape[1] // segment
    points_src = [
        (0, 0),
        (img.shape[1], 0),
        (img.shape[1], img.shape[0]),
        (0, img.shape[0]),
    ]
    points_dst = [
        (random.randint(0, threshold), random.randint(0, threshold)),
        (img.shape[1] - random.randint(0, threshold), random.randint(0, threshold)),
        (
            img.shape[1] - random.randint(0, threshold),
            img.shape[0] - random.randint(0, threshold),
        ),
        (random.randint(0, threshold), img.shape[0] - random.randint(0, threshold)),
    ]

    for i in range(1, segment):
        points_src.append((cut * i, 0))
        points_src.append((cut * i, img.shape[0]))
        points_dst.append(
            (
                cut * i + random.randint(-threshold // 2, threshold // 2),
                random.randint(-threshold // 2, threshold // 2),
            )
        )
        points_dst.append(
            (
                cut * i + random.randint(-threshold // 2, threshold // 2),
                img.shape[0] + random.randint(-threshold // 2, threshold // 2),
            )
        )

    return points_src, points_dst


def apply_mls_transformation(img, points_src, points_dst):
    height, width = img.shape[:2]
    src_points = np.array(points_src, dtype=np.float32)
    dst_points = np.array(points_dst, dtype=np.float32)

    grid_x, grid_y = np.meshgrid(np.arange(width), np.arange(height))
    grid_z = griddata(dst_points, src_points, (grid_x, grid_y), method="cubic")
    map_x = np.append([], [ar[:, 0] for ar in grid_z]).reshape(height, width)
    map_y = np.append([], [ar[:, 1] for ar in grid_z]).reshape(height, width)

    map_x = np.clip(map_x, 0, width - 1).astype(np.float32)
    map_y = np.clip(map_y, 0, height - 1).astype(np.float32)

    result = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)

    return result


def distort_image(img_input, segment, threshold_factor):
    img = np.array(img_input)
    cut = img.shape[1] // segment
    threshold = int(cut * threshold_factor)
    points_src, points_dst = generate_distorted_points(img, segment, threshold)
    result = apply_mls_transformation(img, points_src, points_dst)

    result_img = Image.fromarray(result)
    result_with_white_bg = Image.new("RGB", result_img.size, (255, 255, 255))
    result_with_white_bg.paste(
        result_img, mask=result_img.split()[3] if result_img.mode == "RGBA" else None
    )

    return result_with_white_bg


def smooth_image(image, radius):
    return image.filter(ImageFilter.GaussianBlur(radius))


def augment_image(image, noise=True, rotate=True, distort=True, smooth=True):
    if rotate:
        angle = random.uniform(-3, 3)
        image = rotate_image(image, angle)
    if distort:
        image = distort_image(image, 4, 0.05)
    if noise:
        mean = np.random.uniform(-2, 2)
        std = np.random.uniform(5, 15)
        image = add_gaussian_noise(image, mean, std)
    if smooth:
        radius = np.random.uniform(0, 0.5)
        image = smooth_image(image, radius)
    return image


def augment_image_file(filename):
    image = Image.open(filename)

    augmented_image = augment_image(
        image, noise=True, rotate=True, distort=True, smooth=True
    )
    augmented_image.save(filename)
