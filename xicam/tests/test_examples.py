import numpy as np
from numpy import random


from pytest import fixture
import random
from skimage import data
from scipy.ndimage.interpolation import shift

from pystxmtools.corrections.register import register_frames_stack

@fixture
def test_stack():
    image = data.camera()
    n_frames = 10
    shifts = [(round(random.uniform(1, 50), 2), round(random.uniform(1, 50), 2)) for i in range(n_frames)]
    stack = []
    for n in range(n_frames):
        stack.append(shift(image, shifts[n]))
    return np.asarray(stack), shifts

def test_register_frame_stack(test_stack):
    aligned_frames = register_frames_stack(test_stack[0], mode='translation')
    shifts_calc = register_frames_stack(test_stack[1])
    print(aligned_frames.shape)
    print(test_stack.shape)

    assert aligned_frames.shape[0] == test_stack[0].shape[0]
    assert shifts_calc == test_stack[1]


