<div align="center">

# Lorenz Attractor

**Interactive 3D visualization of the Lorenz system**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![VisPy](https://img.shields.io/badge/VisPy-GPU%20Accelerated-4B8BBE)
![PyQt5](https://img.shields.io/badge/PyQt5-Desktop%20GUI-41CD52)

[Features](#features) •
[Installation](#installation) •
[Usage](#usage) •
[Controls](#controls) •
[Gallery](#gallery) •
[Theory](#theory)

</div>

---

## Overview

This application provides a real-time, GPU-accelerated 3D visualization of the
[Lorenz system](https://en.wikipedia.org/wiki/Lorenz_system), a set of
ordinary differential equations known for producing chaotic behaviour and the
iconic "butterfly" attractor. Adjust parameters on the fly, animate the
trajectory tracing, and explore a range of preset configurations.

## Features

- **Real-time parameter adjustment** — sliders for σ, ρ, β with instant visual feedback
- **Colour-mapped trajectory** — the path is shaded from cool to warm along the
  vertical (z) axis using a perceptually uniform colour scale
- **Trace animation** — watch the attractor being drawn point-by-point with a
  highlighted head marker
- **Preset configurations** — switch instantly between *Classic*, *Butterfly*,
  *Chaos*, *Lazy*, and *Transient* parameter sets
- **Dark-themed UI** — modern Catppuccin-inspired palette with custom-styled
  sliders and buttons
- **Keyboard shortcuts** — space to animate, R to reset the view, P to cycle
  presets
- **Auto-framing camera** — the view automatically centres and scales to fit
  the attractor whenever parameters change

## Installation

### Prerequisites

- Python 3.10 or later
- A GPU with OpenGL support (most modern integrated and discrete GPUs)

### Steps

```bash
# Clone the repository
git clone https://github.com/trashdino0/LorenzAttractor.git
cd LorenzAttractor

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

> **Note on Qt**: `PyQt5` is used for the GUI layer. If you prefer PySide2,
> replace `PyQt5` in the import statements and requirements file.

## Usage

```bash
python lorenz_attractor.py
```

A window will open with the classic Lorenz attractor rendered in 3D. Use your
mouse to orbit, pan, and zoom the camera:

| Action        | Input               |
|---------------|---------------------|
| Orbit         | Left-drag           |
| Pan           | Right-drag          |
| Zoom          | Scroll wheel        |

### Controls reference

| Control             | Description                                     |
|---------------------|-------------------------------------------------|
| σ (Sigma) slider    | Prandtl number — rate of heat/momentum transfer |
| ρ (Rho) slider      | Rayleigh number — temperature gradient          |
| β (Beta) slider     | Physical proportion of the system               |
| Preset buttons      | Load a predefined parameter set                 |
| Animate Trace       | Toggle trajectory tracing animation             |
| Reset View          | Re-centre the camera on the full attractor      |
| Reset Parameters    | Restore σ=10, ρ=28, β=8/3                       |
| Space               | Toggle animation (keyboard)                     |
| R                   | Reset view (keyboard)                           |
| P                   | Cycle presets (keyboard)                        |

## Presets

| Preset      | σ   | ρ   | β      | Behaviour                              |
|-------------|-----|-----|--------|----------------------------------------|
| Classic     | 10  | 28  | 8/3    | The canonical butterfly attractor      |
| Butterfly   | 10  | 28  | 2.0    | Extended wingspan                      |
| Chaos       | 10  | 99  | 8/3    | Highly chaotic, widely spread orbits   |
| Lazy        | 5   | 20  | 1.0    | Compact, slower-evolving trajectory    |
| Transient   | 16  | 45  | 4.0    | Long transient before settling         |

## Project structure

```
LorenzAttractor/
├── lorenz_attractor.py    # Main application
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## Theory

The Lorenz system was developed by Edward Lorenz in 1963 as a simplified
model of atmospheric convection. The three coupled ordinary differential
equations are:

```
dx/dt = σ (y - x)
dy/dt = x (ρ - z) - y
dz/dt = x y - β z
```

Where:
- **x** is proportional to the rate of convection
- **y** is proportional to the horizontal temperature variation
- **z** is proportional to the vertical temperature variation
- **σ** (Prandtl number) — ratio of viscosity to thermal conductivity
- **ρ** (Rayleigh number) — proportional to the temperature difference
- **β** — ratio of the width to height of the convection cell

For the classic parameters (σ=10, ρ=28, β=8/3), the system exhibits
sensitive dependence on initial conditions — the hallmark of deterministic
chaos — and traces out the familiar two-lobed "butterfly" attractor.

## Dependencies

| Package    | Version   | Purpose                          |
|------------|-----------|----------------------------------|
| VisPy      | ≥0.14     | GPU-accelerated 3D rendering     |
| NumPy      | ≥1.24     | Numerical computation            |
| PyQt5      | ≥5.15     | Desktop GUI framework            |

## License

This project is open source and available under the [MIT License](LICENSE).
