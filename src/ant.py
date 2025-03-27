import numpy as np

def calculate_ant(n: int) -> int:
    # Image size (pixels)
    width, height = 800, 800

    # Plot window (real and imaginary axis)
    re_min, re_max = -2.0, 1.0
    im_min, im_max = -1.5, 1.5

    # Max number of iterations
    max_iter = 100

    # Create an image array
    image = np.zeros((height, width))

    # Generate Mandelbrot set
    for x in range(width):
        for y in range(height):
            # Map pixel position to complex plane
            c = complex(re_min + (x / width) * (re_max - re_min),
                        im_min + (y / height) * (im_max - im_min))
            z = 0
            iteration = 0
            while abs(z) <= 2 and iteration < max_iter:
                z = z*z + c
                iteration += 1
            image[y, x] = iteration
