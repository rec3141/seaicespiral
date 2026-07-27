#!/usr/bin/env python3
"""Arctic sea ice "death spiral" — PIOMAS daily ice volume, 1979-present.

Python port of seaicespiral.R. Renders:
  - seaicespiral.png         final full-spiral frame (square)
  - seaicespiral_tiktok.mp4  ~24 s vertical (1080x1920, 30 fps) animation

Data: PIOMAS daily Arctic sea ice volume (10^3 km^3), Polar Science Center,
University of Washington:
https://psc.apl.uw.edu/research/projects/arctic-sea-ice-volume-anomaly/
Background image: IBCAO bathymetry (resized/transparent copy from reric.org).
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------- data
data = np.loadtxt("seaicevolume.dat.csv", skiprows=1)
years, days, vol = data[:, 0].astype(int), data[:, 1].astype(int), data[:, 2]
n = len(vol)
theta = (days - 1) / 365.0 * 2 * np.pi  # Jan 1 at 0, clockwise via axes setup

# annual September minima for the end-card stat
first_min = vol[years == years[0]].min()
last_full_year = years[-1] - 1  # last year with a complete summer
recent_min = vol[years == last_full_year].min()
pct_drop = 100 * (1 - recent_min / first_min)

# ---------------------------------------------------------------- style
SURFACE = "#0a1420"
TRAIL_CMAP = LinearSegmentedColormap.from_list("trail", ["#2a6da6", "#6fbef5"])
HEAD = "#E84A38"
INK, INK_MUTED = "#f2f6fa", "#8fa3b5"
HEAD_LEN = 10  # trailing days drawn as the red "now" head

trail_colors = TRAIL_CMAP((years - years[0]) / (years[-1] - years[0]))

FPS = 30
STEP = 27  # days of data revealed per frame  -> ~21 s of growth
HOLD = 3 * FPS  # seconds holding the finished spiral
frames_grow = int(np.ceil(n / STEP))
total_frames = frames_grow + HOLD

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(9, 16), dpi=120)
fig.patch.set_facecolor(SURFACE)

# square rect for the spiral, centered; height_frac = width_frac * 1080/1920
w = 0.84
rect = [(1 - w) / 2, 0.315, w, w * 9 / 16]

bg = fig.add_axes(rect)
bg.imshow(plt.imread("ibcao.png"))
bg.axis("off")

ax = fig.add_axes(rect, polar=True, frameon=False)
ax.patch.set_alpha(0)
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_rlim(0, 35)
ax.set_rticks([5, 15, 25, 35])
ax.set_yticklabels(["5", "15", "25", "35"], color=INK_MUTED, fontsize=9)
ax.set_rlabel_position(80)
ax.set_xticks(np.arange(12) * np.pi / 6)
ax.set_xticklabels(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    color=INK, fontsize=13, fontweight="bold",
)
ax.tick_params(pad=6)
ax.grid(color="white", alpha=0.12, linewidth=0.8)
ax.spines.clear()

trail = ax.scatter([], [], s=7, linewidths=0, zorder=3)
head = ax.scatter([], [], s=[], c=HEAD, edgecolors="white",
                  linewidths=0.6, zorder=4)

fig.text(0.5, 0.955, "ARCTIC SEA ICE", ha="center", color=INK,
         fontsize=34, fontweight="bold")
fig.text(0.5, 0.928, f"volume in 1000 km³ · PIOMAS · "
         f"{years[0]}–{years[-1]}", ha="center", color=INK_MUTED,
         fontsize=15)
year_txt = fig.text(0.5, 0.235, "", ha="center", color=INK,
                    fontsize=64, fontweight="bold")
vol_txt = fig.text(0.5, 0.20, "", ha="center", color=INK_MUTED, fontsize=18)
stat_txt = fig.text(0.5, 0.14, "", ha="center", color=HEAD,
                    fontsize=22, fontweight="bold")
fig.text(0.5, 0.022,
         "Data: PIOMAS, Polar Science Center, University of Washington\n"
         "Original animation: R. Eric Collins · github.com/rec3141/seaicespiral",
         ha="center", color=INK_MUTED, fontsize=10)


def draw(frame):
    i = min((frame + 1) * STEP, n)
    trail.set_offsets(np.column_stack([theta[:i], vol[:i]]))
    trail.set_facecolors(trail_colors[:i])
    h0 = max(0, i - HEAD_LEN)
    head.set_offsets(np.column_stack([theta[h0:i], vol[h0:i]]))
    head.set_sizes(np.linspace(15, 70, i - h0))
    year_txt.set_text(str(years[i - 1]))
    vol_txt.set_text(f"{vol[i - 1] * 1000:,.0f} km³ of sea ice")
    if frame >= frames_grow:
        stat_txt.set_text(
            f"summer minimum down {pct_drop:.0f}% since {years[0]}")
    return trail, head, year_txt, vol_txt, stat_txt


anim = FuncAnimation(fig, draw, frames=total_frames, blit=False)
anim.save(
    "seaicespiral_tiktok.mp4",
    writer=FFMpegWriter(fps=FPS, codec="h264",
                        extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]),
)

# ---------------------------------------------------------------- final still
draw(total_frames - 1)
fig.savefig("seaicespiral.png", dpi=120, facecolor=SURFACE)
print(f"done: {n} days plotted, {total_frames} frames, "
      f"{total_frames / FPS:.0f} s video")
