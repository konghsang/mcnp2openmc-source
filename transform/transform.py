import openmc
import numpy as np
from openmc.stats import CylindricalIndependent, Uniform
import openmc.stats
import re


# 读取程序（读取mcnp输入文件中有源设置参数）
# ==============================================================================
def read_data_file(filename):
    data = {}
    current_key = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()

            # 修改正则表达式以允许字母+数字的组合（如SI2）
            if len(parts) >= 2 and len(parts[1]) == 1 and re.match(r"^[A-Za-z][A-Za-z0-9]*$", parts[0]):
                key = parts[0] + parts[1]
                current_key = key
                try:
                    values = list(map(float, parts[2:]))
                    data.setdefault(key, []).extend(values)
                except:
                    current_key = None
            else:
                # 处理数据行
                if current_key is not None:
                    try:
                        values = list(map(float, parts))
                        data[current_key].extend(values)
                    except:
                        pass
    return data


# 读取数据文件
data = read_data_file("mcnp_sdef.txt")
# ==============================================================================
# 读取相关参数
# 圆柱参数
R = 468.280  # 半径 (cm)
Z_MIN = -300  # 轴向最小坐标 (cm)
Z_MAX = 300  # 轴向最大坐标 (cm)
# 径向分环边界
r_bins_SI2H = data.get("SI2H", [])
# 径向分环概率
r_bins_SP2D = data.get("SP2D", [])
# 轴向分层边界
z_bins_SI42H = data.get("SI42H", [])
# 对DS3Q进行处理
list = data.get("DS3Q", [])
# 筛选出奇数索引位置的元素
new_list_odd = list[::2]
# 筛选出偶数索引位置的元素，转换为整数并按照“SI数P”的规则组成新数组
new_list_even = ["SP" + str(int(num)) + "D" for num in list[1::2]]
sources = []

# 创建源项
# --------------------------------------------------
# 遍历径向环 (0,1,2)
for r_idx in range(len(r_bins_SI2H) - 1):
    r_min = r_bins_SI2H[r_idx]
    r_max = r_bins_SI2H[r_idx + 1]

    # 遍历轴向层 (0,1,2)
    for z_idx in range(len(z_bins_SI42H) - 1):
        z_min = z_bins_SI42H[z_idx]
        z_max = z_bins_SI42H[z_idx + 1]

        # --------------------------------------------------
        # 创建圆柱坐标系空间分布
        # --------------------------------------------------
        spatial = CylindricalIndependent(
            r=Uniform(r_min, r_max), phi=Uniform(0.0, 2 * np.pi), z=Uniform(z_min, z_max)  # 径向均匀分布  # 全角度覆盖  # 当前轴向层均匀分布
        )

        # -------------------------------------------------
        # 设置源参数
        # --------------------------------------------------
        source = openmc.IndependentSource()
        source.space = spatial

        z_bins_P = data.get(new_list_even[r_idx], [])
        source.strength = z_bins_P[z_idx + 1] * r_bins_SP2D[r_idx + 1]  # 设置概率
        source.energy = openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=10000.0)
        source.angle = openmc.stats.Isotropic()
        sources.append(source)
# 归一化总强度（可选，但推荐）
total_strength = sum(src.strength for src in sources)
for src in sources:
    src.strength /= total_strength
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.batches = 1
settings.particles = 100000
settings.max_tracks = 100000
settings.source = sources
settings.export_to_xml()
