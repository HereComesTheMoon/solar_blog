from enum import Enum
from PIL import Image
import numpy as np
import functools


class DIFFUSION(Enum):
    NAIVE = ((0, 1),)
    FLOYDSTEINBERG = (
        (0, 0, 7),
        (3, 5, 1),
    )
    JARVISJUDICENINKE = (
        (0, 0, 0, 7, 5),
        (3, 5, 7, 5, 3),
        (1, 3, 5, 3, 1),
    )
    BURKES = (
        (0, 0, 0, 8, 4),
        (2, 4, 8, 4, 2),
    )
    SIERRA = (
        (0, 0, 0, 5, 3),
        (2, 4, 5, 4, 2),
        (0, 2, 3, 2, 0),
    )


def error_diffusion_dither(
    img: Image.Image, diffusion: tuple, steps: tuple[int]
) -> Image.Image:
    diffusion = diffusion.value
    for step in steps:
        assert step in range(256)
    start = 0
    for x in diffusion[0]:
        if x != 0:
            break
        start += 1
    mass = sum(sum(row) for row in diffusion)

    errors = [[0.0 for _ in range(img.size[1])] for _ in range(img.size[0])]

    data = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            errs = (
                (
                    abs(data[i, j] + errors[i][j] - step),
                    data[i, j] + errors[i][j] - step,
                    step,
                )
                for step in steps
            )
            _, err, step = min(errs)
            data[i, j] = step
            for ii, row in enumerate(diffusion):
                for jj, _ in enumerate(row):
                    iii = i + ii
                    jjj = j - start + jj
                    if iii not in range(len(errors)):
                        continue
                    if jjj not in range(len(errors[0])):
                        continue
                    errors[iii][jjj] += (err * diffusion[ii][jj]) / mass
    return img


@functools.cache
def bayer_matrix(n: int) -> np.ndarray:
    assert n % 2 == 0
    if n == 2:
        return np.array([[0, 2 / 4], [3 / 4, 1 / 4]])
    m = n // 2
    return np.kron(np.ones((2, 2)), bayer_matrix(m)) + np.kron(
        bayer_matrix(2), np.ones((m, m))
    ) / (m * m)


def apply_bayer(image, gap, order) -> np.ndarray:
    img = np.array(image, "uint8")
    xx, yy = np.meshgrid(range(img.shape[1]), range(img.shape[0]))
    xx %= order
    yy %= order
    bayer = bayer_matrix(order)
    return img + np.expand_dims(gap * bayer[yy, xx] - 1 / 2, axis=2)
