"""Small, explicit physics adapters around the pinned turbo-design backend."""

class SeededLossAdapter:
    """Supply a finite pre-solve seed before a state-dependent loss is usable."""

    def __init__(self, delegate, initial_loss=0.05):
        self.delegate = delegate
        self.initial_loss = initial_loss
        self._loss_type = delegate._loss_type

    @property
    def LossType(self):
        return self._loss_type

    @property
    def loss_type(self):
        return self._loss_type

    def _needs_seed(self, row):
        import numpy as np

        mach = row.M_rel if getattr(row.row_type, "name", "") == "Rotor" else row.M
        return not np.any(np.asarray(mach, dtype=float) > 1e-8)

    def __call__(self, row, upstream):
        import numpy as np

        if self._needs_seed(row):
            return np.full_like(row.r, self.initial_loss, dtype=float)
        return self.delegate(row, upstream)
