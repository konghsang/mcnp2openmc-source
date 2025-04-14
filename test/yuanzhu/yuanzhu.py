import openmc
import numpy as np
from openmc.stats import CylindricalIndependent, Uniform
import openmc.stats

# ==============================================================================
# 圆柱参数
R = 5.0  # 半径 (cm)
Z_MIN = -2.0  # 轴向最小坐标 (cm)
Z_MAX = 2.0  # 轴向最大坐标 (cm)
# 径向分环边界 (3环)
r_bins = [0.0, 2, 3, 5.0]  # 环0:0-1.67, 环1:1.67-3.33, 环2:3.33-5
# 轴向分层边界 (3层)
z_bins = [-2.0, -1.0, 1.0, 2.0]  # 层0:-2~-1, 层1:-1~1, 层2:1~2
# 定义每个区域的概率 (示例值，需用户自定义)
# 格式: prob_matrix[径向环编号][轴向层编号]
prob_matrix = [
    # 环0 的3个轴向层概率
    [0.05, 0.05, 0.05],  # 总概率 0.15
    # 环1 的3个轴向层概率
    [0.05, 0.05, 0.05],  # 总概率 0.15
    # 环2 的3个轴向层概率
    [0.05, 0.60, 0.05],  # 总概率 0.70
]
sources = []
# 遍历径向环 (0,1,2)
for r_idx in range(len(r_bins) - 1):
    r_min = r_bins[r_idx]
    r_max = r_bins[r_idx + 1]

    # 遍历轴向层 (0,1,2)
    for z_idx in range(len(z_bins) - 1):
        z_min = z_bins[z_idx]
        z_max = z_bins[z_idx + 1]

        # --------------------------------------------------
        # 创建圆柱坐标系空间分布
        # --------------------------------------------------
        spatial = CylindricalIndependent(
            r=Uniform(r_min, r_max), phi=Uniform(0.0, 2 * np.pi), z=Uniform(z_min, z_max)  # 径向均匀分布  # 全角度覆盖  # 当前轴向层均匀分布
        )

        # --------------------------------------------------
        # 设置源参数
        # --------------------------------------------------
        source = openmc.IndependentSource()
        source.space = spatial
        source.strength = prob_matrix[r_idx][z_idx]  # 设置概率

        # 其他参数（示例：单能中子，各向同性）
        source.energy = openmc.stats.Discrete([14.1e6], [1.0])  # 14.1 MeV
        source.angle = openmc.stats.Isotropic()

        sources.append(source)
# 归一化总强度（可选，但推荐）
total_strength = sum(src.strength for src in sources)
for src in sources:
    src.strength /= total_strength
# 创建材料
fuel = openmc.Material()
fuel.add_nuclide("U235", 0.1)
fuel.set_density("g/cm3", 0.1)
# 定义圆柱几何边界
outer_cylinder = openmc.ZCylinder(r=R, boundary_type="vacuum")
bottom_plane = openmc.ZPlane(z0=Z_MIN, boundary_type="vacuum")
top_plane = openmc.ZPlane(z0=Z_MAX, boundary_type="vacuum")
# 定义填充区域
cell = openmc.Cell()
cell.region = -outer_cylinder & +bottom_plane & -top_plane
cell.fill = fuel
geometry = openmc.Geometry([cell])
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.batches = 1
settings.particles = 100000
settings.max_tracks = 100000
settings.source = sources
# 导出XML文件
geometry.export_to_xml()
openmc.Materials([fuel]).export_to_xml()
settings.export_to_xml()
# 运行OpenMC
openmc.run(tracks=True)
