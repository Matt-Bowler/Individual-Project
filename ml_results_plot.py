import matplotlib.pyplot as plt
import numpy as np


data = [
    (1, [3.59904025, 8.4223431,  0.6052682,  0.56924338]),
    (2, [0.7366754,  8.58005752, 1.80908638, 1.09821874]),
    (3, [4.35691373, 7.26288806, 2.09621979, 0.13116406]),
    (4, [3.62102222, 3.25070658, 1.40151287, 0.54806201]),
    (5, [3.62102222, 3.25070658, 1.40151287, 0.54806201]),
    (6, [9.17529241, 1.04828217, 2.48294083, 3.46067434]),
    (7, [6.58586418, 2.33714583, 2.48294083, 0.54806201]),
    (8, [9.17529241, 1.04828217, 2.48294083, 3.46067434]),
    (9, [9.17529241, 2.33714583, 2.48294083, 0.54806201]),
    (10, [9.17529241, 1.04828217, 2.48294083, 0.54806201]),
    (11, [9.17529241, 2.33714583, 2.48294083, 0.54806201]),
    (12, [9.17529241, 2.33714583, 2.48294083, 0.54806201])
]

generations = [entry[0] for entry in data]
weights = np.array([entry[1] for entry in data])  

feature_labels = ["Path Difference", "Wall Bonus", "Proximity Bonus", "Forward Bonus"]
markers = ['o', 's', '^', 'D']
colors = ['r', 'g', 'b', 'm']

plt.figure(figsize=(10, 6))
for i in range(4):
    plt.plot(generations, weights[:, i], marker=markers[i], color=colors[i], label=feature_labels[i])

plt.title("Weight Evolution Across Generations")
plt.xlabel("Generation")
plt.ylabel("Weight Value")
plt.ylim(0, 10)
plt.xticks(generations)
plt.legend()
plt.show()
