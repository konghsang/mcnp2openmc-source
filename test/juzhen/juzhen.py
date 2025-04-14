import openmc
from openmc.stats import Box
# 定义几何、材料
materials = openmc.Materials()
water = openmc.Material()
water.add_element("H", 0.667, "ao")
water.add_element("O", 0.334, percent_type="ao")
water.set_density("g/cm3", 1.0)
materials.append(water)
materials.export_to_xml()

# geometry - surfaces
sphere = openmc.Sphere(r=5.0)
sphere.boundary_type = "vacuum"
inside_sphere = -sphere
outside_sphere = +sphere
# geometry cells
universe = openmc.Universe()
moderator = openmc.Cell(fill=water, region=inside_sphere)
universe.add_cell(moderator)
geometry = openmc.Geometry(universe)
geometry.export_to_xml()

# run mode
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.particles = 10000000
settings.max_tracks = 1000000
settings.batches = 1
# output
settings.output = {"tallies": True, "summary": True}
# source
# 定义四个象限的立方体空间分布
box1 = Box([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])  # 第1象限
box2 = Box([-1.0, 0.0, 0.0], [0.0, 1.0, 1.0])  # 第2象限
box3 = Box([-1.0, -1.0, 0.0], [0.0, 0.0, 1.0])  # 第3象限
box4 = Box([0.0, -1.0, 0.0], [1.0, 0.0, 1.0])  # 第4象限

sources = []
# 定义四个源，并分配不同的 strength 权重
source1 = openmc.Source(space=box1, strength=0.7)
source2 = openmc.Source(space=box2, strength=0.1)
source3 = openmc.Source(space=box3, strength=0.1)
source4 = openmc.Source(space=box4, strength=0.1)
sources.append(source1)
sources.append(source2)
sources.append(source3)
sources.append(source4)
# 将源添加到设置中
settings.source = sources

settings.export_to_xml()

# tallies
cell_filter = openmc.CellFilter([moderator])
tally1 = openmc.Tally()
tally1.scores = ["flux"]
tally1.filters.append(cell_filter)
tallies = openmc.Tallies()
tallies.append(tally1)
tallies.export_to_xml()

# run
openmc.run(tracks=True)
