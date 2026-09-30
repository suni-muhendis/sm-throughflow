"""The correlations are plain numpy, pinned to hand-computed values."""
import subprocess
import sys

import numpy as np
import pytest

from sm_throughflow.correlations import camber, carter_deviation, lieblein_diffusion_factor


def test_the_correlations_import_no_solver():
    code = "import sys, sm_throughflow.correlations; assert 'turbodesign' not in sys.modules, sorted(sys.modules)"
    subprocess.run([sys.executable, "-c", code], check=True)


def test_camber_is_inlet_minus_exit_metal_angle():
    assert camber([50.0, 40.0], [30.0, 40.0]) == pytest.approx([20.0, 0.0])


def test_carter_deviation():
    # delta = m * theta / sqrt(sigma): theta = 20 deg, sigma = 1 and 4.
    assert carter_deviation([50.0, 50.0], [30.0, 30.0], [1.0, 4.0]) == pytest.approx([5.0, 2.5])
    assert carter_deviation(50.0, 30.0, 1.0, m=0.2) == pytest.approx(4.0)


def test_lieblein_diffusion_factor():
    # D = 1 - W2/W1 + |dW_theta| / (2 sigma W1) = 1 - 0.7 + 50 / 200.
    assert lieblein_diffusion_factor(100.0, 70.0, -50.0, 1.0) == pytest.approx(0.55)
    assert np.shape(lieblein_diffusion_factor(np.full(11, 100.0), np.full(11, 70.0), np.full(11, 50.0), np.full(11, 1.0))) == (11,)
