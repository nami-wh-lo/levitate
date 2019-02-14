import numpy as np


pos = np.array([
    [-0.026175, -0.005235, 0.],
    [-0.036645, -0.005235, 0.],
    [-0.005235, -0.005235, 0.],
    [-0.015705, -0.005235, 0.],
    [-0.026175, -0.015705, 0.],
    [-0.036645, -0.015705, 0.],
    [-0.005235, -0.015705, 0.],
    [-0.015705, -0.015705, 0.],
    [-0.026175, -0.026175, 0.],
    [-0.036645, -0.026175, 0.],
    [-0.005235, -0.026175, 0.],
    [-0.015705, -0.026175, 0.],
    [-0.026175, -0.036645, 0.],
    [-0.036645, -0.036645, 0.],
    [-0.005235, -0.036645, 0.],
    [-0.015705, -0.036645, 0.],
    [-0.026175, -0.047115, 0.],
    [-0.036645, -0.047115, 0.],
    [-0.005235, -0.047115, 0.],
    [-0.015705, -0.047115, 0.],
    [-0.026175, -0.057585, 0.],
    [-0.036645, -0.057585, 0.],
    [-0.005235, -0.057585, 0.],
    [-0.015705, -0.057585, 0.],
    [-0.026175, -0.068055, 0.],
    [-0.036645, -0.068055, 0.],
    [-0.005235, -0.068055, 0.],
    [-0.015705, -0.068055, 0.],
    [-0.026175, -0.078525, 0.],
    [-0.036645, -0.078525, 0.],
    [-0.005235, -0.078525, 0.],
    [-0.015705, -0.078525, 0.],
    [-0.068055, -0.047115, 0.],
    [-0.078525, -0.047115, 0.],
    [-0.047115, -0.047115, 0.],
    [-0.057585, -0.047115, 0.],
    [-0.068055, -0.057585, 0.],
    [-0.078525, -0.057585, 0.],
    [-0.047115, -0.057585, 0.],
    [-0.057585, -0.057585, 0.],
    [-0.068055, -0.068055, 0.],
    [-0.078525, -0.068055, 0.],
    [-0.047115, -0.068055, 0.],
    [-0.057585, -0.068055, 0.],
    [-0.068055, -0.078525, 0.],
    [-0.078525, -0.078525, 0.],
    [-0.047115, -0.078525, 0.],
    [-0.057585, -0.078525, 0.],
    [-0.068055, -0.005235, 0.],
    [-0.078525, -0.005235, 0.],
    [-0.047115, -0.005235, 0.],
    [-0.057585, -0.005235, 0.],
    [-0.068055, -0.015705, 0.],
    [-0.078525, -0.015705, 0.],
    [-0.047115, -0.015705, 0.],
    [-0.057585, -0.015705, 0.],
    [-0.068055, -0.026175, 0.],
    [-0.078525, -0.026175, 0.],
    [-0.047115, -0.026175, 0.],
    [-0.057585, -0.026175, 0.],
    [-0.068055, -0.036645, 0.],
    [-0.078525, -0.036645, 0.],
    [-0.047115, -0.036645, 0.],
    [-0.057585, -0.036645, 0.],
    [-0.047115, 0.005235, 0.],
    [-0.057585, 0.005235, 0.],
    [-0.068055, 0.005235, 0.],
    [-0.078525, 0.005235, 0.],
    [-0.047115, 0.015705, 0.],
    [-0.057585, 0.015705, 0.],
    [-0.068055, 0.015705, 0.],
    [-0.078525, 0.015705, 0.],
    [-0.047115, 0.026175, 0.],
    [-0.057585, 0.026175, 0.],
    [-0.068055, 0.026175, 0.],
    [-0.078525, 0.026175, 0.],
    [-0.047115, 0.036645, 0.],
    [-0.057585, 0.036645, 0.],
    [-0.068055, 0.036645, 0.],
    [-0.078525, 0.036645, 0.],
    [-0.047115, 0.047115, 0.],
    [-0.057585, 0.047115, 0.],
    [-0.068055, 0.047115, 0.],
    [-0.078525, 0.047115, 0.],
    [-0.047115, 0.057585, 0.],
    [-0.057585, 0.057585, 0.],
    [-0.068055, 0.057585, 0.],
    [-0.078525, 0.057585, 0.],
    [-0.047115, 0.068055, 0.],
    [-0.057585, 0.068055, 0.],
    [-0.068055, 0.068055, 0.],
    [-0.078525, 0.068055, 0.],
    [-0.047115, 0.078525, 0.],
    [-0.057585, 0.078525, 0.],
    [-0.068055, 0.078525, 0.],
    [-0.078525, 0.078525, 0.],
    [-0.005235, 0.047115, 0.],
    [-0.015705, 0.047115, 0.],
    [-0.026175, 0.047115, 0.],
    [-0.036645, 0.047115, 0.],
    [-0.005235, 0.057585, 0.],
    [-0.015705, 0.057585, 0.],
    [-0.026175, 0.057585, 0.],
    [-0.036645, 0.057585, 0.],
    [-0.005235, 0.068055, 0.],
    [-0.015705, 0.068055, 0.],
    [-0.026175, 0.068055, 0.],
    [-0.036645, 0.068055, 0.],
    [-0.005235, 0.078525, 0.],
    [-0.015705, 0.078525, 0.],
    [-0.026175, 0.078525, 0.],
    [-0.036645, 0.078525, 0.],
    [-0.005235, 0.005235, 0.],
    [-0.015705, 0.005235, 0.],
    [-0.026175, 0.005235, 0.],
    [-0.036645, 0.005235, 0.],
    [-0.005235, 0.015705, 0.],
    [-0.015705, 0.015705, 0.],
    [-0.026175, 0.015705, 0.],
    [-0.036645, 0.015705, 0.],
    [-0.005235, 0.026175, 0.],
    [-0.015705, 0.026175, 0.],
    [-0.026175, 0.026175, 0.],
    [-0.036645, 0.026175, 0.],
    [-0.005235, 0.036645, 0.],
    [-0.015705, 0.036645, 0.],
    [-0.026175, 0.036645, 0.],
    [-0.036645, 0.036645, 0.],
    [0.036645, 0.005235, 0.],
    [0.026175, 0.005235, 0.],
    [0.015705, 0.005235, 0.],
    [0.005235, 0.005235, 0.],
    [0.036645, 0.015705, 0.],
    [0.026175, 0.015705, 0.],
    [0.015705, 0.015705, 0.],
    [0.005235, 0.015705, 0.],
    [0.036645, 0.026175, 0.],
    [0.026175, 0.026175, 0.],
    [0.015705, 0.026175, 0.],
    [0.005235, 0.026175, 0.],
    [0.036645, 0.036645, 0.],
    [0.026175, 0.036645, 0.],
    [0.015705, 0.036645, 0.],
    [0.005235, 0.036645, 0.],
    [0.036645, 0.047115, 0.],
    [0.026175, 0.047115, 0.],
    [0.015705, 0.047115, 0.],
    [0.005235, 0.047115, 0.],
    [0.036645, 0.057585, 0.],
    [0.026175, 0.057585, 0.],
    [0.015705, 0.057585, 0.],
    [0.005235, 0.057585, 0.],
    [0.036645, 0.068055, 0.],
    [0.026175, 0.068055, 0.],
    [0.015705, 0.068055, 0.],
    [0.005235, 0.068055, 0.],
    [0.036645, 0.078525, 0.],
    [0.026175, 0.078525, 0.],
    [0.015705, 0.078525, 0.],
    [0.005235, 0.078525, 0.],
    [0.078525, 0.047115, 0.],
    [0.068055, 0.047115, 0.],
    [0.057585, 0.047115, 0.],
    [0.047115, 0.047115, 0.],
    [0.078525, 0.057585, 0.],
    [0.068055, 0.057585, 0.],
    [0.057585, 0.057585, 0.],
    [0.047115, 0.057585, 0.],
    [0.078525, 0.068055, 0.],
    [0.068055, 0.068055, 0.],
    [0.057585, 0.068055, 0.],
    [0.047115, 0.068055, 0.],
    [0.078525, 0.078525, 0.],
    [0.068055, 0.078525, 0.],
    [0.057585, 0.078525, 0.],
    [0.047115, 0.078525, 0.],
    [0.078525, 0.005235, 0.],
    [0.068055, 0.005235, 0.],
    [0.057585, 0.005235, 0.],
    [0.047115, 0.005235, 0.],
    [0.078525, 0.015705, 0.],
    [0.068055, 0.015705, 0.],
    [0.057585, 0.015705, 0.],
    [0.047115, 0.015705, 0.],
    [0.078525, 0.026175, 0.],
    [0.068055, 0.026175, 0.],
    [0.057585, 0.026175, 0.],
    [0.047115, 0.026175, 0.],
    [0.078525, 0.036645, 0.],
    [0.068055, 0.036645, 0.],
    [0.057585, 0.036645, 0.],
    [0.047115, 0.036645, 0.],
    [0.057585, -0.005235, 0.],
    [0.047115, -0.005235, 0.],
    [0.078525, -0.005235, 0.],
    [0.068055, -0.005235, 0.],
    [0.057585, -0.015705, 0.],
    [0.047115, -0.015705, 0.],
    [0.078525, -0.015705, 0.],
    [0.068055, -0.015705, 0.],
    [0.057585, -0.026175, 0.],
    [0.047115, -0.026175, 0.],
    [0.078525, -0.026175, 0.],
    [0.068055, -0.026175, 0.],
    [0.057585, -0.036645, 0.],
    [0.047115, -0.036645, 0.],
    [0.078525, -0.036645, 0.],
    [0.068055, -0.036645, 0.],
    [0.057585, -0.047115, 0.],
    [0.047115, -0.047115, 0.],
    [0.078525, -0.047115, 0.],
    [0.068055, -0.047115, 0.],
    [0.057585, -0.057585, 0.],
    [0.047115, -0.057585, 0.],
    [0.078525, -0.057585, 0.],
    [0.068055, -0.057585, 0.],
    [0.057585, -0.068055, 0.],
    [0.047115, -0.068055, 0.],
    [0.078525, -0.068055, 0.],
    [0.068055, -0.068055, 0.],
    [0.057585, -0.078525, 0.],
    [0.047115, -0.078525, 0.],
    [0.078525, -0.078525, 0.],
    [0.068055, -0.078525, 0.],
    [0.015705, -0.047115, 0.],
    [0.005235, -0.047115, 0.],
    [0.036645, -0.047115, 0.],
    [0.026175, -0.047115, 0.],
    [0.015705, -0.057585, 0.],
    [0.005235, -0.057585, 0.],
    [0.036645, -0.057585, 0.],
    [0.026175, -0.057585, 0.],
    [0.015705, -0.068055, 0.],
    [0.005235, -0.068055, 0.],
    [0.036645, -0.068055, 0.],
    [0.026175, -0.068055, 0.],
    [0.015705, -0.078525, 0.],
    [0.005235, -0.078525, 0.],
    [0.036645, -0.078525, 0.],
    [0.026175, -0.078525, 0.],
    [0.015705, -0.005235, 0.],
    [0.005235, -0.005235, 0.],
    [0.036645, -0.005235, 0.],
    [0.026175, -0.005235, 0.],
    [0.015705, -0.015705, 0.],
    [0.005235, -0.015705, 0.],
    [0.036645, -0.015705, 0.],
    [0.026175, -0.015705, 0.],
    [0.015705, -0.026175, 0.],
    [0.005235, -0.026175, 0.],
    [0.036645, -0.026175, 0.],
    [0.026175, -0.026175, 0.],
    [0.015705, -0.036645, 0.],
    [0.005235, -0.036645, 0.],
    [0.036645, -0.036645, 0.],
    [0.026175, -0.036645, 0.]])

norm = np.tile((0, 0, 1), (256, 1))
dragonfly_grid = (pos, norm)
