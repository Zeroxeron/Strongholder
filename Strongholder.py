# ----------------------------------------------------
# Minecraft Strongholder
# ----------------------------------------------------
# Copyright (c) 2026 x_Kiva_x
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

import pyperclip
import matplotlib.pyplot as plt
from Config import CFG
from Util import chunks_from_ring, parse_from_clipboard, from_rings, filter_points_to_lines, top_n_closest, get_resource


class Strongholder:
    rings = []
    lines = []
    plines = []
    sc_results_top = None
    sc_grid = None
    text_results = None
    text_help = None
    text_status = None
    scan_task = None
    active = True

    fig, ax = plt.subplots(num="Minecraft Strongholder v1.1")

    def defaults(self):
        self.rings = []
        for i in range(0, CFG.MAX_RINGS):
            rmin, rmax = CFG.S_RINGS[i]
            self.rings.append(chunks_from_ring(rmin, rmax))
        self.lines = []
        self.plines = []
        self.sc_results_top = None
        self.sc_grid = None
        # text labels reset
        self.text_results.set_text("Expecting [F3+C] clipboard...")
        self.text_help.set_text("[R]-Reload [X]-Copy closest tp")
        self.text_status.set_text("Idle...")

    def __init__(self):
        self.text_results = self.fig.text(
            0.5, 0.25, "Expecting [F3+C] clipboard...",
            ha='center', va='top', fontsize=10, color='white',
            transform=self.fig.transFigure)
        self.text_help = self.fig.text(
            0.5, 0.97, "[R]-Reset [+]-Increase margin [-]-Decrease margin [C]-Copy closest tp",
            ha='center', va='bottom', fontsize=8, color='white', transform=self.fig.transFigure)
        self.text_status = self.fig.text(
            0.01, 0.01, "Idle...",
            ha='left', va='bottom', fontsize=8, color='gray', transform=self.fig.transFigure)
        manager = plt.get_current_fig_manager()
        manager.window.wm_iconbitmap(get_resource("icon.ico"))
        self.setup()
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        print("Initialized!")
        self.scan()
        # self.scan_task = Thread(target=self.scan, daemon=True)
        # self.scan_task.run()
        return

    def scan(self):
        print("Started clipboard scanning task...")
        try:
            while self.active and plt.fignum_exists(self.fig.number):
                self.scan_clipboard()
                plt.pause(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            plt.ioff()
            plt.show(block=True)
        print("Clipboard scanning task stopped")

    def setup(self):
        """ new GUI preparations """
        self.defaults()
        df = from_rings(self.rings)
        xs = df["x"].to_numpy()
        zs = df["z"].to_numpy()
        self.sc_grid = self.ax.scatter(xs, zs, s=10, c="darkgray", label="All")   # scatter of all points
        self.sc_results_top = self.ax.scatter([],[],s=12, c="#00FF00", label="Nearest", edgecolors="lime")
        self.fig.tight_layout()
        self.fig.patch.set_facecolor("#202020")
        self.fig.patch.set_animated(True)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("z")
        self.ax.axis("equal")
        self.ax.grid(True)
        self.ax.legend(loc="upper right")
        self.ax.set_facecolor("#101010")
        self.ax.set_xlabel("x", color="white")
        self.ax.set_ylabel("z", color="white")
        self.ax.set_title("", color="white")
        self.ax.tick_params(axis="x", colors="white")
        self.ax.tick_params(axis="y", colors="white")
        self.ax.set_xlim(auto=True)
        self.ax.set_ylim(auto=True)
        self.fig.subplots_adjust(bottom=0.35)  # add space at bottom
        self.text_results.set_text("Expecting [F3+C] clipboard...")
        for spine in self.ax.spines.values():
            spine.set_color("white")
        self.fig.canvas.draw_idle()

    def on_key(self, event):
        # refresh logic
        if event.key == 'r':
            self.ax.clear()
            self.setup()
            self.ax.set_xlim(-CFG.S_RINGS[CFG.MAX_RINGS][1], CFG.S_RINGS[CFG.MAX_RINGS][1])
            self.ax.set_ylim(-CFG.S_RINGS[CFG.MAX_RINGS][1], CFG.S_RINGS[CFG.MAX_RINGS][1])
            self.fig.canvas.draw_idle()
        elif event.key == 'x':
            if not self.rings: return
            if not self.lines: return
            df = from_rings(self.rings)
            df_near = filter_points_to_lines(df, self.lines)
            df_top = top_n_closest(df_near, n=CFG.MAX_RESULTS)
            if len(df_top) == len(df): return
            nearest = list(df_top['overworld'])
            cmd = f"/tp {nearest[0].replace(' ',' 38 ')}"
            pyperclip.copy(cmd)
            self.text_status.set_text(f"Copied to clipboard: >> {cmd}")
            #status_text.set_text("Example command copied! Paste new /tp to add lines.")
            #fig.canvas.draw_idle()

    def scan_clipboard(self) -> None:
        parsed = parse_from_clipboard()
        if not parsed: return
        self.lines.append(parsed)
        self.update(parsed)

    def update(self, parsed):
        # add new line to plot
        (p0, p1) = parsed
        xline = [p0[0], p1[0]]
        zline = [p0[1], p1[1]]
        # lines
        for i, (p0, p1) in enumerate(self.lines, start=1):
            xs = [p0[0], p1[0]]
            zs = [p0[1], p1[1]]
            self.plines = plt.plot(xs, zs, label=f"Line {i}")
            # mark starting point
            plt.scatter([p0[0]], [p0[1]], c="black", s=20, marker="x")
        self.text_status.set_text(f"Directions: {len(self.lines)} | Margin: {CFG.MAX_MARGIN}")
        self.ax.plot(xline, zline, linewidth=1.5, alpha=0.2)
        self.proceed_closest()
        self.closest_zoom()
        self.fig.canvas.draw_idle()

    def proceed_closest(self):
        df = from_rings(self.rings) # 2. Filter points near all lines (triangulation-like region)
        df_near = filter_points_to_lines(df, self.lines)
        df_top = top_n_closest(df_near, n=CFG.MAX_RESULTS) # 3. Take top 5 closest (by max distance to any line)
        self.sc_results_top.remove()  # clear old points
        self.sc_results_top = self.ax.scatter(df_top["x"], df_top["z"], s=12, c="#00FF00", label="Nearest", edgecolors="lime")
        try:
            if len(df_near) == len(df):
                self.text_results.set_text(f"No valid intersections!\nRefresh and try again or lower the error margin!")
                return
            s = "\n".join([f"{row['overworld']:6}  [{row['nether']:6}] - {row['dist']:.3f} avg." for _, row in df_top[['overworld', 'nether','dist']].iterrows()])
            self.text_results.set_text(f"Nearest locations ({len(df_near)}):\n\n{s}")
        except BaseException as e:
            print(f'Exception {e.args}:\n{e}')

    def closest_zoom(self, margin=10.0):
        xs = []
        ys = []
        for (p0, p1) in self.lines:
            xs.extend([p0[0], p1[0]])
            ys.extend([p0[1], p1[1]])

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        self.ax.set_xlim(xmin - margin, xmax + margin)
        self.ax.set_ylim(ymin - margin, ymax + margin)
        self.ax.figure.canvas.draw_idle()