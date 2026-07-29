"""
Fourier-feature SPINN TL vs theoretical TL for a 2-D expansion-chamber
Helmholtz sound-wave problem.

Geometry:
    L_in = 0.05 m, L_e = 0.20 m, L_out = 0.05 m
    D_in = 0.025 m, D_e = 0.10 m, D_out = 0.025 m

This script compares:
    1) TL_theory: classical lossless plane-wave transfer-matrix formula.
    2) TL_PINN: TL computed from the trained Fourier-feature SPINN pressure field.

Frequency sweep:
    20 Hz to 3150 Hz, every 10 Hz, with a linear x-axis.

Important note:
    TL_PINN is obtained from the neural pressure solution, not copied from the
    theoretical formula. Its accuracy depends on the number of epochs,
    collocation points, rank, initialization, and optimizer settings. A pure
    PINN/SPINN does not mathematically guarantee <= 1 dB accuracy over the full
    20--3150 Hz band.

Install:
    pip install torch numpy matplotlib pandas imageio tqdm

Examples:
    # Full frequency sweep on GPU. This is expensive because it trains one model per frequency.
    python pinn_fourier_spinn_tl_vs_theory.py --device cuda --epochs 3000

    # Fast code-path test.
    python pinn_fourier_spinn_tl_vs_theory.py --device cpu --quick --epochs 2 --anim-frames 4

    # Fewer training points for debugging.
    python pinn_fourier_spinn_tl_vs_theory.py --device cuda --freq-step 100 --epochs 1000
"""

from __future__ import annotations

import argparse
import copy
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import imageio.v2 as imageio
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from tqdm import tqdm


# -----------------------------
# Geometry and constants
# -----------------------------

@dataclass
class Geometry:
    L_in: float = 0.05
    L_e: float = 0.20
    L_out: float = 0.05
    D_in: float = 0.025
    D_e: float = 0.10
    D_out: float = 0.025

    @property
    def L(self) -> float:
        return self.L_in + self.L_e + self.L_out

    @property
    def x1(self) -> float:
        return self.L_in

    @property
    def x2(self) -> float:
        return self.L_in + self.L_e

    @property
    def area_in(self) -> float:
        return math.pi * self.D_in**2 / 4.0

    @property
    def area_e(self) -> float:
        return math.pi * self.D_e**2 / 4.0

    @property
    def area_out(self) -> float:
        return math.pi * self.D_out**2 / 4.0

    def half_height_np(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x)
        return np.where(
            x < self.x1,
            0.5 * self.D_in,
            np.where(x <= self.x2, 0.5 * self.D_e, 0.5 * self.D_out),
        )

    def inside_mask_np(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.abs(y) <= self.half_height_np(x) + 1e-12


@dataclass
class Physical:
    c0: float = 343.0
    rho0: float = 1.2041
    p_inc: float = 1.0
    p_ref: float = 20e-6


FIELD_FREQS = [300.0, 500.0, 700.0]

def make_frequency_grid(start: float = 300.0, stop: float = 1000.0, step: float = 10.0) -> List[float]:
    freqs = np.arange(start, stop + 0.5 * step, step, dtype=float)
    freqs = freqs[freqs <= stop + 1e-9]
    if abs(freqs[-1] - stop) > 1e-9:
        freqs = np.append(freqs, stop)
    return freqs.tolist()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def safe_db_np(amplitude_pa: np.ndarray, p_ref: float = 20e-6, floor_pa: float = 1e-12) -> np.ndarray:
    amp = np.maximum(np.abs(amplitude_pa), floor_pa)
    return 20.0 * np.log10(amp / p_ref)


def complex_abs2(z: torch.Tensor) -> torch.Tensor:
    return z.real.square() + z.imag.square()


# -----------------------------
# Theoretical TL
# -----------------------------

class TheoryTLSolver:
    """Classical lossless plane-wave transfer-matrix TL for an expansion chamber."""

    def __init__(self, geom: Geometry, phys: Physical):
        self.geom = geom
        self.phys = phys

    def k(self, freq: float) -> float:
        return 2.0 * math.pi * freq / self.phys.c0

    def transfer_matrix_tl(self, freq: float) -> float:
        """TL = 10 log10(1 + 1/4 (m - 1/m)^2 sin^2(k L_e))."""
        k = self.k(freq)
        m = self.geom.area_e / self.geom.area_in
        val = 1.0 + 0.25 * (m - 1.0 / m) ** 2 * math.sin(k * self.geom.L_e) ** 2
        return 10.0 * math.log10(max(val, 1e-30))


# -----------------------------
# Fourier-feature SPINN
# -----------------------------

class FourierFeatures(nn.Module):
    def __init__(self, in_dim: int, n_features: int, sigma: float = 8.0):
        super().__init__()
        B = sigma * torch.randn(in_dim, n_features)
        self.register_buffer("B", B)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        xb = 2.0 * math.pi * x @ self.B
        return torch.cat([torch.sin(xb), torch.cos(xb)], dim=-1)


class AxisFourierNet(nn.Module):
    def __init__(self, rank: int, n_features: int = 48, hidden: int = 96, layers: int = 3):
        super().__init__()
        self.ff = FourierFeatures(1, n_features)
        mods: List[nn.Module] = []
        dim = 2 * n_features
        for _ in range(layers):
            lin = nn.Linear(dim, hidden)
            nn.init.xavier_uniform_(lin.weight)
            nn.init.zeros_(lin.bias)
            mods += [lin, nn.Tanh()]
            dim = hidden
        out = nn.Linear(dim, 2 * rank)
        nn.init.xavier_uniform_(out.weight)
        nn.init.zeros_(out.bias)
        mods.append(out)
        self.net = nn.Sequential(*mods)
        self.rank = rank

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.net(self.ff(x)).view(-1, self.rank, 2)
        return torch.complex(z[..., 0], z[..., 1])


class FourierSPINN(nn.Module):
    """Separable complex pressure ansatz P(x,y) = P_inc + sum_r alpha_r X_r(x)Y_r(y)."""

    def __init__(self, geom: Geometry, rank: int = 48, hidden: int = 96, layers: int = 3, n_features: int = 48):
        super().__init__()
        self.geom = geom
        self.fx = AxisFourierNet(rank, n_features=n_features, hidden=hidden, layers=layers)
        self.fy = AxisFourierNet(rank, n_features=n_features, hidden=hidden, layers=layers)
        self.alpha = nn.Parameter(torch.randn(rank, dtype=torch.cfloat) / math.sqrt(rank))
        self.bias = nn.Parameter(torch.zeros((), dtype=torch.cfloat))

    def normalize(self, xy: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x = 2.0 * xy[:, 0:1] / self.geom.L - 1.0
        y = 2.0 * xy[:, 1:2] / self.geom.D_e
        return x, y

    def forward(self, xy: torch.Tensor, k: float, p_inc: float = 1.0) -> torch.Tensor:
        x, y = self.normalize(xy)
        X = self.fx(x)
        Y = self.fy(y)
        corr = torch.sum(self.alpha.view(1, -1) * X * Y, dim=1, keepdim=True) + self.bias
        incident = p_inc * torch.exp(-1j * k * xy[:, 0:1])
        return incident + corr


def complex_grad(p: torch.Tensor, xy: torch.Tensor) -> torch.Tensor:
    gre = torch.autograd.grad(p.real.sum(), xy, create_graph=True, retain_graph=True)[0]
    gim = torch.autograd.grad(p.imag.sum(), xy, create_graph=True, retain_graph=True)[0]
    return torch.complex(gre, gim)


class Sampler:
    def __init__(self, geom: Geometry, device: torch.device, dtype: torch.dtype):
        self.geom = geom
        self.device = device
        self.dtype = dtype

    def tensor(self, a: np.ndarray) -> torch.Tensor:
        return torch.tensor(a, device=self.device, dtype=self.dtype)

    def interior(self, n: int) -> torch.Tensor:
        x = np.random.rand(n, 1) * self.geom.L
        h = self.geom.half_height_np(x)
        y = (2.0 * np.random.rand(n, 1) - 1.0) * h
        return self.tensor(np.hstack([x, y]))

    def inlet(self, n: int) -> torch.Tensor:
        y = (2.0 * np.random.rand(n, 1) - 1.0) * 0.5 * self.geom.D_in
        return self.tensor(np.hstack([np.zeros_like(y), y]))

    def outlet(self, n: int) -> torch.Tensor:
        y = (2.0 * np.random.rand(n, 1) - 1.0) * 0.5 * self.geom.D_out
        return self.tensor(np.hstack([np.full_like(y, self.geom.L), y]))

    def walls(self, n: int) -> List[Tuple[torch.Tensor, int]]:
        g = self.geom
        items: List[Tuple[torch.Tensor, int]] = []
        for xa, xb, h in [(0.0, g.x1, 0.5*g.D_in), (g.x1, g.x2, 0.5*g.D_e), (g.x2, g.L, 0.5*g.D_out)]:
            x = xa + (xb - xa) * np.random.rand(n, 1)
            items.append((self.tensor(np.hstack([x, np.full_like(x, h)])), 1))
            items.append((self.tensor(np.hstack([x, np.full_like(x, -h)])), 1))
        for x0, ds in [(g.x1, g.D_in), (g.x2, g.D_out)]:
            y0, y1 = 0.5 * ds, 0.5 * g.D_e
            y = y0 + (y1 - y0) * np.random.rand(n, 1)
            x = np.full_like(y, x0)
            items.append((self.tensor(np.hstack([x, y])), 0))
            items.append((self.tensor(np.hstack([x, -y])), 0))
        return items


def fourier_spinn_loss(
    model: FourierSPINN,
    sampler: Sampler,
    freq: float,
    geom: Geometry,
    phys: Physical,
    n_int: int,
    n_io: int,
    n_wall: int,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    k = 2.0 * math.pi * freq / phys.c0

    xy = sampler.interior(n_int).requires_grad_(True)
    p = model(xy, k, phys.p_inc)
    grad = complex_grad(p, xy)
    pxx = complex_grad(grad[:, 0:1], xy)[:, 0:1]
    pyy = complex_grad(grad[:, 1:2], xy)[:, 1:2]
    res = (pxx + pyy + k*k*p) / (k*k + (math.pi/geom.L)**2)
    loss_pde = complex_abs2(res).mean()

    xin = sampler.inlet(n_io).requires_grad_(True)
    pin = model(xin, k, phys.p_inc)
    gin = complex_grad(pin, xin)
    bc_in = (gin[:, 0:1] - 1j*k*pin + 2j*k*phys.p_inc) / max(k, 1.0)
    loss_in = complex_abs2(bc_in).mean()

    xout = sampler.outlet(n_io).requires_grad_(True)
    pout = model(xout, k, phys.p_inc)
    gout = complex_grad(pout, xout)
    bc_out = (gout[:, 0:1] + 1j*k*pout) / max(k, 1.0)
    loss_out = complex_abs2(bc_out).mean()

    wall_terms = []
    for xw, comp in sampler.walls(n_wall):
        xw = xw.requires_grad_(True)
        pw = model(xw, k, phys.p_inc)
        gw = complex_grad(pw, xw)
        wall_terms.append(complex_abs2(gw[:, comp:comp+1] / max(k, 1.0)).mean())
    loss_wall = torch.stack(wall_terms).mean()

    loss = loss_pde + 8.0 * (loss_in + loss_out) + 4.0 * loss_wall
    parts = {
        "loss": float(loss.detach().cpu()),
        "pde": float(loss_pde.detach().cpu()),
        "inlet": float(loss_in.detach().cpu()),
        "outlet": float(loss_out.detach().cpu()),
        "wall": float(loss_wall.detach().cpu()),
    }
    return loss, parts


def make_model(geom: Geometry, args: argparse.Namespace, device: torch.device, dtype: torch.dtype) -> FourierSPINN:
    model = FourierSPINN(
        geom,
        rank=args.rank,
        hidden=args.hidden,
        layers=args.layers,
        n_features=args.fourier_features,
    ).to(device)
    if dtype == torch.float64:
        model = model.double()
    return model


def train_fourier_spinn(
    freq: float,
    geom: Geometry,
    phys: Physical,
    args: argparse.Namespace,
    init_state: Optional[Dict[str, torch.Tensor]] = None,
) -> Tuple[FourierSPINN, pd.DataFrame]:
    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    dtype = torch.float64 if args.dtype == "float64" else torch.float32
    model = make_model(geom, args, device, dtype)
    if init_state is not None:
        model.load_state_dict(init_state, strict=False)

    sampler = Sampler(geom, device, dtype)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-6)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(args.epochs, 1), eta_min=args.lr * 0.05)

    hist: List[Dict[str, float]] = []
    iterator = tqdm(range(args.epochs), desc=f"Fourier-SPINN {freq:g} Hz", leave=False)
    for ep in iterator:
        opt.zero_grad(set_to_none=True)
        loss, parts = fourier_spinn_loss(model, sampler, freq, geom, phys, args.n_int, args.n_io, args.n_wall)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 10.0)
        opt.step()
        scheduler.step()
        if ep == 0 or (ep + 1) % args.log_every == 0 or ep == args.epochs - 1:
            row = {"epoch": ep + 1, **parts}
            hist.append(row)
            iterator.set_postfix({"loss": f"{parts['loss']:.2e}"})

    if args.lbfgs_steps > 0:
        opt2 = torch.optim.LBFGS(
            model.parameters(),
            max_iter=args.lbfgs_steps,
            tolerance_grad=1e-9,
            tolerance_change=1e-12,
            line_search_fn="strong_wolfe",
        )

        def closure() -> torch.Tensor:
            opt2.zero_grad(set_to_none=True)
            loss, _ = fourier_spinn_loss(model, sampler, freq, geom, phys, args.n_int, args.n_io, args.n_wall)
            loss.backward()
            return loss

        opt2.step(closure)

    return model, pd.DataFrame(hist)


# -----------------------------
# PINN TL and field evaluation
# -----------------------------

@torch.no_grad()
def model_real_dtype(model: nn.Module) -> torch.dtype:
    for param in model.parameters():
        if not torch.is_complex(param):
            return param.dtype
    return torch.float32


def outlet_plane_wave_amplitude_from_pinn(
    model: FourierSPINN,
    freq: float,
    geom: Geometry,
    phys: Physical,
    n: int = 501,
) -> complex:
    """Average complex pressure over the outlet cross-section as transmitted plane-mode amplitude."""
    device = next(model.parameters()).device
    dtype = model_real_dtype(model)
    y = np.linspace(-0.5 * geom.D_out, 0.5 * geom.D_out, n).reshape(-1, 1)
    x = np.full_like(y, geom.L)
    xy = torch.tensor(np.hstack([x, y]), device=device, dtype=dtype)
    k = 2.0 * math.pi * freq / phys.c0
    p = model(xy, k, phys.p_inc).detach().cpu().numpy().reshape(-1)
    return complex(np.mean(p))


def tl_from_transmitted_amplitude(T: complex, geom: Geometry, phys: Physical) -> float:
    """Transmission loss from plane-mode amplitude.

    For unequal inlet/outlet areas, include the area ratio. Here D_in = D_out, so this term is zero.
    """
    amp = max(abs(T), 1e-12)
    return 10.0 * math.log10(geom.area_in / geom.area_out) + 20.0 * math.log10(phys.p_inc / amp)


@torch.no_grad()
def predict_pinn_on_grid(
    model: FourierSPINN,
    freq: float,
    geom: Geometry,
    phys: Physical,
    nx: int = 420,
    ny: int = 160,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    device = next(model.parameters()).device
    dtype = model_real_dtype(model)
    xs = np.linspace(0.0, geom.L, nx)
    ys = np.linspace(-0.5 * geom.D_e, 0.5 * geom.D_e, ny)
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    pts = np.column_stack([X.ravel(), Y.ravel()])
    xy = torch.tensor(pts, device=device, dtype=dtype)
    k = 2.0 * math.pi * freq / phys.c0
    chunks = []
    for chunk in torch.split(xy, 20000, dim=0):
        chunks.append(model(chunk, k, phys.p_inc).detach().cpu())
    P = torch.cat(chunks, dim=0).numpy().reshape(ny, nx)
    P[~geom.inside_mask_np(X, Y)] = np.nan + 1j * np.nan
    return X, Y, P


# -----------------------------
# Plotting
# -----------------------------

def plot_tl_comparison(df: pd.DataFrame, outdir: Path) -> None:
    fig, ax = plt.subplots(figsize=(14.0, 6.0))
    ax.plot(df["freq_Hz"], df["TL_PINN_dB"], linewidth=2.0, label="Fourier-SPINN TL")
    ax.plot(df["freq_Hz"], df["TL_theory_dB"], linestyle="--", linewidth=2.0, label="theory TL")

    ax.set_xlim(20.0, 3150.0)
    ax.set_xlabel("Frequency / Hz")
    ax.set_ylabel("Transmission loss / dB")
    major_ticks = [20, 500, 1000, 1500, 2000, 2500, 3000, 3150]
    ax.set_xticks(major_ticks)
    ax.set_xticklabels([str(t) for t in major_ticks])
    ax.xaxis.set_minor_locator(MultipleLocator(10.0))

    ymax_data = np.nanmax([df["TL_PINN_dB"].to_numpy(), df["TL_theory_dB"].to_numpy()])
    ymax = max(10.0, math.ceil(float(ymax_data) / 5.0) * 5.0 + 5.0)
    ax.set_ylim(0.0, ymax)
    ax.yaxis.set_major_locator(MultipleLocator(5.0))
    ax.grid(True, which="major", alpha=0.4)
    ax.grid(True, which="minor", axis="x", alpha=0.12)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "TL_PINN_vs_theory.png", dpi=300)
    plt.close(fig)


def plot_tl_error(df: pd.DataFrame, outdir: Path) -> None:
    fig, ax = plt.subplots(figsize=(14.0, 4.6))
    ax.plot(df["freq_Hz"], df["error_PINN_minus_theory_dB"], linewidth=2.0, label="PINN - theory")
    ax.axhline(0.0, linestyle="--", linewidth=1.5)
    ax.axhline(1.0, linestyle=":", linewidth=1.2)
    ax.axhline(-1.0, linestyle=":", linewidth=1.2)
    ax.set_xlim(20.0, 3150.0)
    ax.set_xlabel("Frequency / Hz")
    ax.set_ylabel("TL error / dB")
    major_ticks = [20, 500, 1000, 1500, 2000, 2500, 3000, 3150]
    ax.set_xticks(major_ticks)
    ax.set_xticklabels([str(t) for t in major_ticks])
    ax.xaxis.set_minor_locator(MultipleLocator(10.0))
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.grid(True, which="major", alpha=0.4)
    ax.grid(True, which="minor", axis="x", alpha=0.12)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "TL_error_PINN_minus_theory.png", dpi=300)
    plt.close(fig)


def plot_pinn_field(freq: float, model: FourierSPINN, geom: Geometry, phys: Physical, outdir: Path) -> None:
    X, Y, P = predict_pinn_on_grid(model, freq, geom, phys)
    amp_db = safe_db_np(np.abs(P), phys.p_ref)
    phase = np.angle(P)

    fig, ax = plt.subplots(figsize=(10.2, 3.6))
    im = ax.pcolormesh(X, Y, amp_db, shading="auto")
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(f"Fourier-SPINN pressure amplitude at {freq:g} Hz / dB re 20 µPa")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    fig.colorbar(im, ax=ax).set_label("dB")
    fig.tight_layout()
    fig.savefig(outdir / f"pressure_dB_FourierSPINN_{freq:g}Hz.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.2, 3.6))
    im = ax.pcolormesh(X, Y, phase, shading="auto", vmin=-math.pi, vmax=math.pi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(f"Fourier-SPINN pressure phase at {freq:g} Hz / rad")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    fig.colorbar(im, ax=ax).set_label("rad")
    fig.tight_layout()
    fig.savefig(outdir / f"phase_FourierSPINN_{freq:g}Hz.png", dpi=220)
    plt.close(fig)


def make_pinn_animation(freq: float, model: FourierSPINN, geom: Geometry, phys: Physical, outdir: Path, frames: int = 48) -> None:
    X, Y, P = predict_pinn_on_grid(model, freq, geom, phys, nx=360, ny=140)
    w = 2.0 * math.pi * freq
    imgs = []
    vmax = np.nanmax(safe_db_np(np.abs(P), phys.p_ref))
    vmin = vmax - 60.0
    frame_dir = outdir / "_frames_pinn"
    frame_dir.mkdir(exist_ok=True)
    for i in range(frames):
        t = i / frames / freq
        inst = np.real(P * np.exp(1j*w*t))
        db = safe_db_np(np.abs(inst), phys.p_ref)
        fig, ax = plt.subplots(figsize=(10.2, 3.6))
        im = ax.pcolormesh(X, Y, db, shading="auto", vmin=vmin, vmax=vmax)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"Fourier-SPINN instantaneous |p(t)| at {freq:g} Hz / dB, frame {i+1}/{frames}")
        ax.set_xlabel("x / m")
        ax.set_ylabel("y / m")
        fig.colorbar(im, ax=ax).set_label("dB re 20 µPa")
        fig.tight_layout()
        fp = frame_dir / f"frame_{i:04d}.png"
        fig.savefig(fp, dpi=130)
        plt.close(fig)
        imgs.append(imageio.imread(fp))
    imageio.mimsave(outdir / f"propagation_dB_FourierSPINN_{freq:g}Hz.gif", imgs, duration=1/24)
    try:
        imageio.mimsave(outdir / f"propagation_dB_FourierSPINN_{freq:g}Hz.mp4", imgs, fps=24)
    except Exception as exc:
        print(f"MP4 skipped: {exc}")


# -----------------------------
# Driver
# -----------------------------

def run(args: argparse.Namespace) -> None:
    set_seed(args.seed)
    geom = Geometry()
    phys = Physical(c0=args.c0, rho0=args.rho0, p_inc=1.0)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    model_dir = outdir / "models"
    hist_dir = outdir / "histories"
    model_dir.mkdir(exist_ok=True)
    hist_dir.mkdir(exist_ok=True)

    theory = TheoryTLSolver(geom, phys)

    if args.quick:
        freqs = [20.0, 500.0, 3150.0]
        field_freqs = [500.0]
        args.n_int = min(args.n_int, 256)
        args.n_io = min(args.n_io, 64)
        args.n_wall = min(args.n_wall, 32)
    else:
        freqs = make_frequency_grid(args.freq_start, args.freq_stop, args.freq_step)
        field_freqs = [float(f) for f in args.field_freqs]
        # Ensure field frequencies are trained too.
        freqs = sorted(set(freqs + field_freqs))

    rows = []
    trained_models: Dict[float, FourierSPINN] = {}
    last_state: Optional[Dict[str, torch.Tensor]] = None

    for f in freqs:
        model_path = model_dir / f"fourier_spinn_{f:g}Hz.pt"
        print(f"\nTraining / loading Fourier-SPINN at {f:g} Hz")

        if args.load_existing and model_path.exists():
            device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
            dtype = torch.float64 if args.dtype == "float64" else torch.float32
            model = make_model(geom, args, device, dtype)
            state = torch.load(model_path, map_location=device)
            model.load_state_dict(state)
            history = pd.DataFrame()
        else:
            model, history = train_fourier_spinn(
                float(f), geom, phys, args,
                init_state=last_state if args.continuation else None,
            )
            torch.save(model.state_dict(), model_path)
            if not history.empty:
                history.to_csv(hist_dir / f"history_fourier_spinn_{f:g}Hz.csv", index=False)

        if args.continuation:
            last_state = copy.deepcopy(model.state_dict())

        T_pinn = outlet_plane_wave_amplitude_from_pinn(model, float(f), geom, phys, n=args.n_outlet_eval)
        tl_pinn = tl_from_transmitted_amplitude(T_pinn, geom, phys)
        tl_theory = theory.transfer_matrix_tl(float(f))
        rows.append({
            "freq_Hz": float(f),
            "TL_PINN_dB": tl_pinn,
            "TL_theory_dB": tl_theory,
            "error_PINN_minus_theory_dB": tl_pinn - tl_theory,
            "T_PINN_abs": abs(T_pinn),
            "T_PINN_real": T_pinn.real,
            "T_PINN_imag": T_pinn.imag,
        })

        if float(f) in field_freqs:
            trained_models[float(f)] = model

    df = pd.DataFrame(rows).sort_values("freq_Hz")
    df.to_csv(outdir / "TL_PINN_vs_theory.csv", index=False)
    plot_tl_comparison(df, outdir)
    plot_tl_error(df, outdir)

    for f in field_freqs:
        model = trained_models.get(float(f))
        if model is not None:
            plot_pinn_field(float(f), model, geom, phys, outdir)

    if args.make_animation:
        anim_freq = float(args.animation_freq)
        model = trained_models.get(anim_freq)
        if model is None:
            candidates = sorted(trained_models.keys())
            if not candidates:
                print("No trained field model is available for animation; animation skipped.")
            else:
                model = trained_models[candidates[0]]
                anim_freq = candidates[0]
        if model is not None:
            make_pinn_animation(anim_freq, model, geom, phys, outdir, frames=args.anim_frames)

    print("\nSaved outputs to:", outdir.resolve())
    print(df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--device", choices=["cuda", "cpu"], default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--dtype", choices=["float32", "float64"], default="float32")
    p.add_argument("--outdir", default="results_fourier_spinn_tl_vs_theory")
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--c0", type=float, default=343.0)
    p.add_argument("--rho0", type=float, default=1.2041)

    p.add_argument("--freq-start", type=float, default=20.0)
    p.add_argument("--freq-stop", type=float, default=3150.0)
    p.add_argument("--freq-step", type=float, default=10.0)
    p.add_argument("--field-freqs", type=float, nargs="+", default=FIELD_FREQS)

    p.add_argument("--epochs", type=int, default=3000)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--rank", type=int, default=48)
    p.add_argument("--hidden", type=int, default=96)
    p.add_argument("--layers", type=int, default=3)
    p.add_argument("--fourier-features", type=int, default=48)
    p.add_argument("--n-int", type=int, default=4096)
    p.add_argument("--n-io", type=int, default=512)
    p.add_argument("--n-wall", type=int, default=256)
    p.add_argument("--n-outlet-eval", type=int, default=501)
    p.add_argument("--lbfgs-steps", type=int, default=0)
    p.add_argument("--log-every", type=int, default=200)
    p.add_argument("--continuation", action="store_true", default=True, help="initialize each frequency from previous frequency")
    p.add_argument("--no-continuation", dest="continuation", action="store_false")
    p.add_argument("--load-existing", action="store_true", help="reuse saved models when available")

    p.add_argument("--make-animation", action="store_true")
    p.add_argument("--animation-freq", type=float, default=500.0)
    p.add_argument("--anim-frames", type=int, default=48)
    p.add_argument("--quick", action="store_true", help="small frequency set and small collocation sizes for testing")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
