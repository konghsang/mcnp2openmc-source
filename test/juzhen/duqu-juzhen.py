import h5py
import numpy as np
import matplotlib.pyplot as plt


def classify_quadrant(x, y):
    if x >= 0 and y >= 0:
        return "Q1"
    elif x < 0 and y >= 0:
        return "Q2"
    elif x < 0 and y < 0:
        return "Q3"
    elif x >= 0 and y < 0:
        return "Q4"
    else:
        return "Unknown"


quadrant_counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "Unknown": 0}
source_positions = []

with h5py.File("tracks.h5", "r") as f:
    for track_key in f:
        if not track_key.startswith("track_"):
            continue

        # 读取轨迹数据集中的结构化数组
        track_data = f[track_key][:]

        # 提取第一个状态的坐标（初始位置）
        initial_state = track_data[0]  # 索引 0 代表初始状态
        x = initial_state["r"]["x"]  # 提取 x 分量
        y = initial_state["r"]["y"]  # 提取 y 分量

        source_positions.append([x, y])
        quadrant = classify_quadrant(x, y)
        quadrant_counts[quadrant] += 1

# 结果处理
if len(source_positions) == 0:
    print("错误：未读取到任何源粒子位置！")
    exit()

source_positions = np.array(source_positions)
total_particles = len(source_positions)

print("\n=== 源粒子分布统计 ===")
print(f"总粒子数: {total_particles}")
for q in ["Q1", "Q2", "Q3", "Q4", "Unknown"]:
    count = quadrant_counts[q]
    ratio = count / total_particles
    expected = 0.7 if q == "Q1" else 0.1 if q in ["Q2", "Q3", "Q4"] else 0.0
    print(f"{q}: {ratio:.4f} (期望值: {expected}) | 粒子数: {count}")

# 可视化
plt.figure(figsize=(10, 6))
plt.scatter(source_positions[:, 0], source_positions[:, 1], alpha=0.3, s=10, c="blue")
plt.axhline(0, color="k", linestyle="--", linewidth=1)
plt.axvline(0, color="k", linestyle="--", linewidth=1)
plt.xlim(-1.1, 1.1)
plt.ylim(-1.1, 1.1)
plt.title("源粒子初始位置分布（最终验证）")
plt.xlabel("X (cm)")
plt.ylabel("Y (cm)")
plt.grid(True)
plt.show()
