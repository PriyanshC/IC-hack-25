import networkx as nx
import matplotlib.pyplot as plt

from model import Model
from building import Building

# Create building
building = Building([10, 5, 2], [3, 2], 2)

# Model building
model = Model(building)


# Create plot figure
fig = plt.figure(figsize=(10, 7))
axes = fig.add_subplot(111, projection="3d")

model.plot(axes)

plt.title("Building Escape Route with Blocked Nodes")
plt.show()
