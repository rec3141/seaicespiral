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
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------- data
data = np.loadtxt("seaicevolume.dat.csv", skiprows=1)
years, days, vol = data[:, 0].astype(int), data[:, 1].astype(int), data[:, 2]
n = len(vol)
theta = (days - 1) / 365.0 * 2 * np.pi  # Jan 1 at 0, clockwise via axes setup
xtime = years + (days - 1) / 365.25  # decimal year for the timeline panel

# annual September minima for the end-card stat
first_min = vol[years == years[0]].min()
last_full_year = years[-1] - 1  # last year with a complete summer
recent_min = vol[years == last_full_year].min()
pct_drop = 100 * (1 - recent_min / first_min)

# ---------------------------------------------------------------- style
SURFACE = "#0a1420"
# year color sweeps the spectrum, cold blue (1979) -> hot red (now)
TRAIL_CMAP = LinearSegmentedColormap.from_list(
    "trail", ["#3a7bd5", "#2fb3c9", "#45b856", "#e8c33a", "#f28c2e", "#e84a38"])
HEAD = "#E84A38"
INK, INK_MUTED = "#f2f6fa", "#8fa3b5"
HEAD_LEN = 10  # trailing days drawn as the red "now" head

trail_colors = TRAIL_CMAP((years - years[0]) / (years[-1] - years[0]))

# trail line segments, colored by year; subsampled every 3rd day (chords are
# indistinguishable from daily at 1080 px but render ~3x faster)
SUB = 3
sub_idx = np.arange(0, n, SUB)
pts = np.column_stack([theta, vol])[sub_idx]
segments = np.stack([pts[:-1], pts[1:]], axis=1)
seg_colors = trail_colors[sub_idx[:-1]]
tpts = np.column_stack([xtime, vol])[sub_idx]
tsegments = np.stack([tpts[:-1], tpts[1:]], axis=1)

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

trail = LineCollection([], linewidths=1.3, capstyle="round", zorder=3)
ax.add_collection(trail)
head = ax.scatter([], [], s=[], c=HEAD, edgecolors="white",
                  linewidths=0.6, zorder=4)

# timeline panel: volume vs time, same year-color gradient
tax = fig.add_axes([0.14, 0.08, 0.78, 0.115])
tax.set_facecolor("none")
tax.set_xlim(years[0], years[-1] + 0.5)
tax.set_ylim(0, 35)
tax.set_xticks([1980, 1990, 2000, 2010, 2020])
tax.set_yticks([0, 15, 30])
tax.tick_params(colors=INK_MUTED, labelsize=10, length=0)
for spine in tax.spines.values():
    spine.set_visible(False)
tax.grid(axis="y", color="white", alpha=0.1, linewidth=0.8)
tax.set_ylabel("1000 km³", color=INK_MUTED, fontsize=9)
tline = LineCollection([], linewidths=1.6, capstyle="round")
tax.add_collection(tline)
(tdot,) = tax.plot([], [], "o", ms=6, color=HEAD, mec="white", mew=0.6)

fig.text(0.5, 0.955, "ARCTIC SEA ICE", ha="center", color=INK,
         fontsize=34, fontweight="bold")
fig.text(0.5, 0.928, f"volume in 1000 km³ · PIOMAS · "
         f"{years[0]}–{years[-1]}", ha="center", color=INK_MUTED,
         fontsize=15)
year_txt = fig.text(0.5, 0.235, "", ha="center", color=INK,
                    fontsize=64, fontweight="bold")
stat_txt = fig.text(0.5, 0.203, "", ha="center", color=HEAD,
                    fontsize=19, fontweight="bold")
fig.text(0.5, 0.022,
         "Data: PIOMAS, Polar Science Center, University of Washington\n"
         "Original animation: R. Eric Collins · github.com/rec3141/seaicespiral",
         ha="center", color=INK_MUTED, fontsize=10)


def draw(frame):
    i = min((frame + 1) * STEP, n)
    j = max(0, np.searchsorted(sub_idx, i) - 1)
    trail.set_segments(segments[:j])
    trail.set_color(seg_colors[:j])
    h0 = max(0, i - HEAD_LEN)
    head.set_offsets(np.column_stack([theta[h0:i], vol[h0:i]]))
    head.set_sizes(np.linspace(15, 70, i - h0))
    year_txt.set_text(str(years[i - 1]))
    year_txt.set_color(trail_colors[i - 1])
    tline.set_segments(tsegments[:j])
    tline.set_color(seg_colors[:j])
    tdot.set_data([xtime[i - 1]], [vol[i - 1]])
    if frame >= frames_grow:
        stat_txt.set_text(
            f"summer minimum down {pct_drop:.0f}% since {years[0]}")
    return trail, head, tline, tdot, year_txt, stat_txt


anim = FuncAnimation(fig, draw, frames=total_frames, blit=False)
anim.save(
    "seaicespiral_tiktok.mp4",
    writer=FFMpegWriter(fps=FPS, codec="h264",
                        extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]),
    progress_callback=lambda f, tot: (
        print(f"frame {f}/{tot}", flush=True) if f % 100 == 0 else None),
)

# ---------------------------------------------------------------- final still
draw(total_frames - 1)
fig.savefig("seaicespiral.png", dpi=120, facecolor=SURFACE)
print(f"done: {n} days plotted, {total_frames} frames, "
      f"{total_frames / FPS:.0f} s video")
