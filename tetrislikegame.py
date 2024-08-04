import streamlit as st
import numpy as np
import time

# 定数の設定
GRID_HEIGHT = 20
GRID_WIDTH = 10
SHAPES = {
    'I': np.array([[1, 1, 1, 1]]),
    'O': np.array([[1, 1], [1, 1]]),
    'T': np.array([[0, 1, 0], [1, 1, 1]]),
    'S': np.array([[0, 1, 1], [1, 1, 0]]),
    'Z': np.array([[1, 1, 0], [0, 1, 1]]),
    'J': np.array([[1, 0, 0], [1, 1, 1]]),
    'L': np.array([[0, 0, 1], [1, 1, 1]])
}

# ゲーム状態の初期化
grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
current_shape = SHAPES['I']
current_position = [0, GRID_WIDTH // 2 - len(current_shape[0]) // 2]

def check_collision(grid, shape, position):
    shape_height, shape_width = shape.shape
    grid_height, grid_width = grid.shape
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i, j] and (position[0] + i >= grid_height or position[1] + j < 0 or position[1] + j >= grid_width or grid[position[0] + i, position[1] + j]):
                return True
    return False

def merge_shape(grid, shape, position):
    shape_height, shape_width = shape.shape
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i, j]:
                grid[position[0] + i, position[1] + j] = shape[i, j]
    return grid

def draw_grid(grid):
    st.write('```')
    for row in grid:
        st.write(' '.join(['#' if cell else '.' for cell in row]))
    st.write('```')

st.title("Streamlit Tetris")

while True:
    grid_copy = grid.copy()
    if not check_collision(grid_copy, current_shape, current_position):
        grid_copy = merge_shape(grid_copy, current_shape, current_position)
    draw_grid(grid_copy)

    time.sleep(1)

    current_position[0] += 1
    if check_collision(grid, current_shape, current_position):
        current_position[0] -= 1
        grid = merge_shape(grid, current_shape, current_position)
        current_shape = SHAPES['I']
        current_position = [0, GRID_WIDTH // 2 - len(current_shape[0]) // 2]

    if st.button("左"):
        new_position = [current_position[0], current_position[1] - 1]
        if not check_collision(grid, current_shape, new_position):
            current_position = new_position
    if st.button("右"):
        new_position = [current_position[0], current_position[1] + 1]
        if not check_collision(grid, current_shape, new_position):
            current_position = new_position
    if st.button("下"):
        new_position = [current_position[0] + 1, current_position[1]]
        if not check_collision(grid, current_shape, new_position):
            current_position = new_position
