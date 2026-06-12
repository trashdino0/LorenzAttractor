"""
Lorenz Attractor — Interactive 3D Visualization
================================================

An interactive 3D visualisation of the Lorenz system of ordinary differential
equations, built with VisPy (GPU-accelerated) and PyQt5.

Controls
--------
* Sliders — adjust σ, ρ, β in real time
* Preset buttons — instantly switch to well-known parameter sets
* Animate Trace — slowly reveal the trajectory as it is being drawn
* Reset View — re-centre the camera on the full attractor
* Reset Parameters — restore the classic (σ=10, ρ=28, β=8/3) set

Keyboard Shortcuts
------------------
  Space  — toggle trace animation
  R      — reset camera view
  P      — cycle through presets
"""

import sys

import numpy as np
from vispy import scene
from vispy.color import get_colormap
from PyQt5.QtWidgets import (
    QApplication,
    QSlider,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QGroupBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor

# ---------------------------------------------------------------------------
#  Lorenz system
# ---------------------------------------------------------------------------

SIGMA_DEFAULT = 10.0
RHO_DEFAULT = 28.0
BETA_DEFAULT = 8.0 / 3.0
DT = 0.01
NUM_STEPS = 8000
X0, Y0, Z0 = 0.0, 1.0, 1.05

PRESETS = {
    "Classic":       (10.0, 28.0, 8.0 / 3.0),
    "Butterfly":     (10.0, 28.0, 2.0),
    "Chaos":         (10.0, 99.0, 8.0 / 3.0),
    "Lazy":          (5.0,  20.0, 1.0),
    "Transient":     (16.0, 45.0, 4.0),
}


def compute_lorenz(s: float, r: float, b: float, n: int = NUM_STEPS) -> np.ndarray:
    """Integrate the Lorenz system with forward Euler."""
    x, y, z = X0, Y0, Z0
    traj = np.empty((n, 3))
    for i in range(n):
        dx = s * (y - x) * DT
        dy = (x * (r - z) - y) * DT
        dz = (x * y - b * z) * DT
        x += dx
        y += dy
        z += dz
        traj[i] = x, y, z
    return traj


# ---------------------------------------------------------------------------
#  GUI
# ---------------------------------------------------------------------------


class LorenzGUI(QWidget):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.sigma = SIGMA_DEFAULT
        self.rho = RHO_DEFAULT
        self.beta = BETA_DEFAULT
        self.animating = False
        self.anim_frame = 0
        self.full_traj: np.ndarray | None = None

        self._build_ui()
        self._keyboard_setup()
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate_step)
        self.compute_and_display()

    # -- UI construction ------------------------------------------------

    def _build_ui(self):
        self.setWindowTitle("Lorenz Attractor")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)

        pal = QPalette()
        pal.setColor(QPalette.Window, QColor("#1e1e2e"))
        pal.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(pal)

        root = QHBoxLayout()
        self.setLayout(root)

        # -- 3D canvas --
        self.canvas = scene.SceneCanvas(keys=None, bgcolor="#0d0d1a", parent=self)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.TurntableCamera(fov=40, distance=60)
        root.addWidget(self.canvas.native, stretch=3)

        # -- side panel --
        side = QVBoxLayout()
        root.addLayout(side, stretch=1)

        group_style = (
            "QGroupBox { color: #cdd6f4; font-weight: bold;"
            " border: 1px solid #45475a; border-radius: 6px;"
            " margin-top: 8px; padding-top: 14px; }"
            "QGroupBox::title { subcontrol-origin: margin;"
            " left: 10px; padding: 0 4px; }"
        )
        btn_style = (
            "QPushButton { background: #313244; color: #cdd6f4;"
            " border: 1px solid #45475a; border-radius: 4px; padding: 6px; }"
            "QPushButton:hover { background: #45475a; }"
        )

        # ---- Parameters ----
        grp = QGroupBox("Parameters")
        grp.setStyleSheet(group_style)
        pl = QVBoxLayout()
        grp.setLayout(pl)
        side.addWidget(grp)

        self.slider_sigma = self._make_slider(0.1, 50, self.sigma, "\u03c3 (Sigma)", pl)
        self.slider_rho = self._make_slider(0.1, 100, self.rho, "\u03c1 (Rho)", pl)
        self.slider_beta = self._make_slider(0.1, 15, self.beta, "\u03b2 (Beta)", pl)

        self.slider_sigma.valueChanged.connect(self._on_param_change)
        self.slider_rho.valueChanged.connect(self._on_param_change)
        self.slider_beta.valueChanged.connect(self._on_param_change)

        # ---- Presets ----
        grp = QGroupBox("Presets")
        grp.setStyleSheet(group_style)
        pl = QVBoxLayout()
        grp.setLayout(pl)
        side.addWidget(grp)

        for name, (s, r, b) in PRESETS.items():
            btn = QPushButton(name)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(
                lambda _, ss=s, rr=r, bb=b: self.load_preset(ss, rr, bb)
            )
            pl.addWidget(btn)

        # ---- Controls ----
        grp = QGroupBox("Controls")
        grp.setStyleSheet(group_style)
        pl = QVBoxLayout()
        grp.setLayout(pl)
        side.addWidget(grp)

        self.anim_cb = QCheckBox("\u25b6 Animate Trace")
        self.anim_cb.setStyleSheet("color: #cdd6f4;")
        self.anim_cb.toggled.connect(self._toggle_animation)
        pl.addWidget(self.anim_cb)

        btn = QPushButton("\u27f2 Reset View")
        btn.setStyleSheet(btn_style)
        btn.clicked.connect(self.reset_view)
        pl.addWidget(btn)

        btn = QPushButton("\u27f2 Reset Parameters")
        btn.setStyleSheet(btn_style)
        btn.clicked.connect(self._reset_params)
        pl.addWidget(btn)

        # ---- Help ----
        help_lbl = QLabel(
            "Shortcuts:  [Space] Animate  \u00b7  [R] Reset View  \u00b7  [P] Cycle Presets"
        )
        help_lbl.setStyleSheet("color: #6c7086; font-size: 11px; padding: 8px 0;")
        help_lbl.setWordWrap(True)
        side.addWidget(help_lbl)
        side.addStretch()

    def _make_slider(
        self,
        vmin: float,
        vmax: float,
        default: float,
        label_text: str,
        layout: QVBoxLayout,
    ) -> QSlider:
        row = QVBoxLayout()
        lbl = QLabel(f"{label_text}  =  {default:.2f}")
        lbl.setStyleSheet("color: #cdd6f4; font-size: 12px;")
        row.addWidget(lbl)
        sl = QSlider(Qt.Horizontal)
        sl.setMinimum(int(vmin * 100))
        sl.setMaximum(int(vmax * 100))
        sl.setValue(int(default * 100))
        sl.setStyleSheet(
            "QSlider::groove:horizontal { height: 4px; background: #313244;"
            " border-radius: 2px; }"
            "QSlider::handle:horizontal { background: #89b4fa; width: 14px;"
            " height: 14px; margin: -5px 0; border-radius: 7px; }"
        )
        sl._label = lbl
        sl._label_tmpl = label_text
        row.addWidget(sl)
        layout.addLayout(row)
        return sl

    # -- keyboard -------------------------------------------------------

    def _keyboard_setup(self):
        self.canvas.events.key_press.connect(self._on_key)

    def _on_key(self, event):
        key = event.text if event.text else event.key.name
        if key == " ":
            self.anim_cb.toggle()
        elif key in ("r", "R"):
            self.reset_view()
        elif key in ("p", "P"):
            self._cycle_preset()

    # -- render ---------------------------------------------------------

    def compute_and_display(self):
        """Re-compute the trajectory and update all visuals."""
        self.full_traj = compute_lorenz(self.sigma, self.rho, self.beta)
        colors = self._gradient_colors(self.full_traj)

        if hasattr(self, "line"):
            self.line.set_data(pos=self.full_traj, color=colors)
        else:
            self.line = scene.visuals.Line(
                pos=self.full_traj,
                color=colors,
                width=1.2,
                parent=self.view.scene,
                antialias=True,
            )

        if hasattr(self, "trace_line"):
            self.trace_line.set_data(pos=self.full_traj[:1], color="#f38ba8")
        else:
            self.trace_line = scene.visuals.Line(
                pos=self.full_traj[:1],
                color="#f38ba8",
                width=3.0,
                parent=self.view.scene,
                antialias=True,
            )

        if hasattr(self, "head"):
            self.head.set_data(pos=self.full_traj[:1])
        else:
            self.head = scene.visuals.Markers(
                pos=self.full_traj[:1],
                face_color="#f38ba8",
                size=8,
                edge_color="#f5c2e7",
                edge_width=0.5,
                parent=self.view.scene,
            )

        if not hasattr(self, "axis"):
            self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        self.anim_frame = 0
        self._frame_camera()

    @staticmethod
    def _gradient_colors(traj: np.ndarray) -> np.ndarray:
        """Map the z-axis onto a cool-warm colour gradient."""
        z = traj[:, 2]
        lo, hi = z.min(), z.max()
        norm = np.zeros_like(z) if hi - lo < 1e-12 else (z - lo) / (hi - lo)
        return get_colormap("coolwarm")[norm]

    def _frame_camera(self):
        if self.full_traj is None:
            return
        mn = self.full_traj.min(axis=0)
        mx = self.full_traj.max(axis=0)
        center = (mn + mx) / 2
        size = (mx - mn).max()
        self.view.camera.center = center
        self.view.camera.distance = size * 1.5

    # -- parameter / preset handling ------------------------------------

    def _on_param_change(self):
        self.sigma = self.slider_sigma.value() / 100.0
        self.rho = self.slider_rho.value() / 100.0
        self.beta = self.slider_beta.value() / 100.0

        self.slider_sigma._label.setText(
            f"{self.slider_sigma._label_tmpl}  =  {self.sigma:.2f}"
        )
        self.slider_rho._label.setText(
            f"{self.slider_rho._label_tmpl}  =  {self.rho:.2f}"
        )
        self.slider_beta._label.setText(
            f"{self.slider_beta._label_tmpl}  =  {self.beta:.2f}"
        )
        self.compute_and_display()

    def load_preset(self, s: float, r: float, b: float):
        self.slider_sigma.setValue(int(s * 100))
        self.slider_rho.setValue(int(r * 100))
        self.slider_beta.setValue(int(b * 100))

    def _reset_params(self):
        self.load_preset(SIGMA_DEFAULT, RHO_DEFAULT, BETA_DEFAULT)

    _PRESET_NAMES = list(PRESETS)

    def _cycle_preset(self):
        if not hasattr(self, "_preset_idx"):
            self._preset_idx = 0
        self._preset_idx = (self._preset_idx + 1) % len(self._PRESET_NAMES)
        s, r, b = PRESETS[self._PRESET_NAMES[self._preset_idx]]
        self.load_preset(s, r, b)

    # -- animation ------------------------------------------------------

    def _toggle_animation(self, on: bool):
        self.animating = on
        if on:
            self.anim_frame = 0
            self._timer.start(20)
        else:
            self._timer.stop()
            self.trace_line.set_data(pos=self.full_traj[:1])
            self.head.set_data(pos=self.full_traj[:1])

    def _animate_step(self):
        if self.full_traj is None:
            return
        n = len(self.full_traj)
        self.anim_frame = min(self.anim_frame + 15, n)
        self.trace_line.set_data(pos=self.full_traj[: self.anim_frame])
        self.head.set_data(
            pos=self.full_traj[self.anim_frame - 1 : self.anim_frame]
        )
        if self.anim_frame >= n:
            self.anim_frame = 0

    # -- view -----------------------------------------------------------

    def reset_view(self):
        self._frame_camera()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = LorenzGUI()
    win.show()
    sys.exit(app.exec_())
