import torch

from sionna.phy.channel.tr38901 import (
    PanelArray,
    UMa,
    UMi
)

from sionna.phy.channel import cir_to_ofdm_channel
from sionna.phy.ofdm import subcarrier_frequencies


# ============================================================
# 1. Basic configuration
# ============================================================

carrier_frequency = 3.5e9

batch_size = 1
num_bs = 1
num_ut = 1

fft_size = 64
subcarrier_spacing = 30e3


# ============================================================
# 2. UT antenna
# ============================================================

ut_array = PanelArray(
    num_rows_per_panel=1,
    num_cols_per_panel=1,
    polarization="single",
    polarization_type="V",
    antenna_pattern="omni",
    carrier_frequency=carrier_frequency,
)


# ============================================================
# 3. BS antenna
# ============================================================

bs_array = PanelArray(
    num_rows_per_panel=1,
    num_cols_per_panel=4,
    polarization="single",
    polarization_type="V",
    antenna_pattern="38.901",
    carrier_frequency=carrier_frequency,
)


# ============================================================
# 4. UMa channel model
# ============================================================

channel_model = UMa(
    carrier_frequency=carrier_frequency,
    o2i_model="low",
    ut_array=ut_array,
    bs_array=bs_array,
    direction="downlink",
    enable_pathloss=True,
    enable_shadow_fading=True,
)


# ============================================================
# 5. Topology
# ============================================================

bs_loc = torch.tensor(
    [[[0.0, 0.0, 25.0]]],
    dtype=torch.float32,
)

ut_loc = torch.tensor(
    [[[100.0, 0.0, 1.5]]],
    dtype=torch.float32,
)

bs_orientation = torch.zeros(
    (batch_size, num_bs, 3),
    dtype=torch.float32,
)

ut_orientation = torch.zeros(
    (batch_size, num_ut, 3),
    dtype=torch.float32,
)

ut_velocities = torch.zeros(
    (batch_size, num_ut, 3),
    dtype=torch.float32,
)

in_state = torch.tensor(
    [[False]],
    dtype=torch.bool,
)

# Force UMa-NLOS
los = False


channel_model.set_topology(
    ut_loc=ut_loc,
    bs_loc=bs_loc,
    ut_orientations=ut_orientation,
    bs_orientations=bs_orientation,
    ut_velocities=ut_velocities,
    in_state=in_state,
    los=los,
)


# ============================================================
# 6. Generate CIR
# ============================================================

num_time_samples = 1

a, tau = channel_model(
    num_time_samples=num_time_samples,
    sampling_frequency=1.0,
)

print("=== CIR ===")
print("a shape   :", a.shape)
print("tau shape :", tau.shape)


# ============================================================
# 7. OFDM subcarrier frequencies
# ============================================================

frequencies = subcarrier_frequencies(
    num_subcarriers=fft_size,
    subcarrier_spacing=subcarrier_spacing,
)

print("\n=== OFDM frequencies ===")
print("shape:", frequencies.shape)
print(frequencies)


# ============================================================
# 8. CIR -> frequency-domain channel
# ============================================================

h_freq = cir_to_ofdm_channel(
    frequencies,
    a,
    tau,
    normalize=False,
)

print("\n=== Frequency-domain channel ===")
print("dtype:", h_freq.dtype)
print("shape:", h_freq.shape)


# ============================================================
# 9. Inspect results
# ============================================================

print("\nFull h_freq:")
print(h_freq)