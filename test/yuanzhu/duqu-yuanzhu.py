import h5py
import numpy as np


def validate_cylindrical_source():
    R = 5.0  # 圆柱半径 (cm)
    r_bins = [0.0, 2, 3, 5.0]
    z_bins = [-2.0, -1.0, 1.0, 2.0]

    # 初始化统计计数器
    valid_positions = []
    total_particles = 0  # 总读取粒子数
    valid_neutrons = 0  # 有效中子数（粒子类型正确）
    valid_in_geom = 0  # 几何范围内中子数

    with h5py.File("tracks.h5", "r") as f:
        # 遍历所有轨迹 (每个轨迹对应一个粒子的历史记录)
        for track_key in f:
            if not track_key.startswith("track_"):
                continue

            total_particles += 1  # 统计总粒子数

            track = f[track_key]

            # === Step 1: 检查粒子类型 ===
            particle_code = track.attrs.get("particles", [-1])[0]
            if particle_code != 0:  # 过滤非中子轨迹
                continue

            valid_neutrons += 1  # 统计有效中子数

            # === Step 2: 提取坐标字段 ===
            coord_fields = ["r", "position"]
            field = None
            for candidate in coord_fields:
                if candidate in track.dtype.names:
                    field = candidate
                    break
            if field is None:
                continue  # 跳过无坐标字段的轨迹

            # === Step 3: 提取初始状态 ===
            coordinates = track[field]
            if coordinates.shape[0] < 1:
                continue  # 跳过无状态数据的轨迹

            initial_state = coordinates[0]
            x, y, z = initial_state

            # === Step 4: 检查几何范围 ===
            r = np.sqrt(x**2 + y**2)
            if r <= R and z_bins[0] <= z <= z_bins[-1]:
                valid_positions.append([r, z])
                valid_in_geom += 1  # 统计几何范围内中子数

    # === 输出统计结果 ===
    print(f"[统计报告]")
    print(f"总读取粒子数: {total_particles}")
    print(f"有效中子数: {valid_neutrons} (占比 {valid_neutrons/total_particles:.1%})")
    print(f"几何范围内中子数: {valid_in_geom} (占中子数 {valid_in_geom/valid_neutrons:.1%})")

    # === 分布比例计算 ===
    if valid_in_geom == 0:
        print("警告：没有符合几何条件的中子！")
        return

    valid_positions = np.array(valid_positions)
    r = valid_positions[:, 0]
    z = valid_positions[:, 1]

    # 分箱统计
    r_indices = np.digitize(r, r_bins) - 1
    z_indices = np.digitize(z, z_bins) - 1
    count_matrix = np.zeros((len(r_bins) - 1, len(z_bins) - 1))

    for i, j in zip(r_indices, z_indices):
        if 0 <= i < count_matrix.shape[0] and 0 <= j < count_matrix.shape[1]:
            count_matrix[i, j] += 1

    print("\n径向-轴向分布矩阵:")
    print("行对应径向区间 (0-2, 2-3, 3-5 cm)")
    print("列对应轴向区间 (-2--1, -1-1, 1-2 cm)")
    print(count_matrix)

    print("\n归一化分布比例:")
    print(count_matrix / count_matrix.sum())


validate_cylindrical_source()
