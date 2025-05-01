import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg

# Set up figure
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_facecolor('black')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.axis('off')

# Load overlay image
overlay_img = mpimg.imread('C:/Users/colin/Downloads/Circle & Dot.png')
overlay_artist = ax.imshow(overlay_img, extent=[-1.125, 1.125, -1.125, 1.125], zorder=5)

# Tube parameters
tube_radius = 1.0
wire_radius = 0.03

# ArCO2 molecules
num_molecules = 150
r = np.sqrt(np.random.uniform(0, (tube_radius - 0.15)**2, num_molecules))
theta = np.random.uniform(0, 2*np.pi, num_molecules)
molecule_positions = np.vstack((r * np.cos(theta), r * np.sin(theta))).T
molecule_velocities = np.random.uniform(-0.02, 0.02, (num_molecules, 2))

# Muon parameters
muon_start = np.array([-0.5, 1.5])
muon_end = np.array([-1.0, -1.5])

# Electrons
electrons = []
electron_sources = []

# Artists
molecule_scat = ax.scatter([], [], color='gray', s=10)
muon_arrow = ax.annotate('', xy=(0,0), xytext=(0,0), arrowprops=dict(arrowstyle='->', color='lime', lw=2))
electron_scat = ax.scatter([], [], color='deepskyblue', s=10)

# Legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='ArCO₂ Molecule', markersize=8, markerfacecolor='gray'),
    plt.Line2D([0], [0], marker='o', color='none', label='Electron', markersize=8, markerfacecolor='deepskyblue', markeredgewidth=0, markeredgecolor='none'),
    plt.Line2D([0], [0], color='lime', lw=2, label='Muon'),
    plt.Line2D([0], [0], marker='o', color='white', label='Wire', markersize=8, markerfacecolor='white')
]
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.35, 1.15), frameon=False, fontsize=10, labelcolor='white')

def init():
    molecule_scat.set_offsets(molecule_positions)
    muon_arrow.set_position((0, 0))
    muon_arrow.xy = (0, 0)
    electron_scat.set_offsets(np.empty((0, 2)))
    return molecule_scat, muon_arrow, electron_scat, overlay_artist

def update(frame):
    global molecule_positions, electrons, electron_sources

    # Update molecule positions
    molecule_positions += molecule_velocities
    for i, pos in enumerate(molecule_positions):
        if np.linalg.norm(pos) >= (tube_radius - 0.05):
            molecule_velocities[i] = -molecule_velocities[i]
    molecule_scat.set_offsets(molecule_positions)

    # Muon appears
    if 20 <= frame <= 30:
        t = (frame - 20) / 10
        current_pos = (1 - t) * muon_start + t * muon_end
        muon_arrow.set_position((muon_start[0], muon_start[1]))
        muon_arrow.xy = (current_pos[0], current_pos[1])

        # Check for molecule collisions
        new_electrons = []
        for i, pos in enumerate(molecule_positions):
            if i not in electron_sources:
                dist = np.linalg.norm(pos - current_pos)
                if dist < 0.1:
                    new_electrons.append(pos.copy())
                    electron_sources.append(i)
        if new_electrons:
            if len(electrons) == 0:
                electrons = np.array(new_electrons)
            else:
                electrons = np.vstack((electrons, new_electrons))

    # Move electrons toward center
    if len(electrons) > 0:
        electrons = np.array(electrons)
        directions = -electrons
        directions /= np.linalg.norm(directions, axis=1)[:, np.newaxis]
        electrons += directions * 0.02
        electron_scat.set_offsets(electrons)

    return molecule_scat, muon_arrow, electron_scat, overlay_artist

# Animate
ani = animation.FuncAnimation(fig, update, frames=70, init_func=init, blit=True, interval=50)

# Save
ani.save('muon_event.gif', writer='pillow', fps=20)

plt.show()
