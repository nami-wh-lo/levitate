import numpy as np
from scipy.optimize import minimize, basinhopping
import logging

from . import models

logger = logging.getLogger(__name__)


class Optimizer:

    def __init__(self, array=None):
        if array is None:
            self.array = models.TransducerArray()
        else:
            self.array = array
        self.objectives = []
        self.basinhopping = False
        self.variable_amplitudes = False

    @property
    def complex_amplitudes(self):
        return self.amplitudes * np.exp(1j * self.phases)

    @complex_amplitudes.setter
    def complex_amplitudes(self, value):
        self.amplitudes = np.abs(value)
        self.phases = np.angle(value)

    def func_and_jac(self, phases_amplitudes):
            results = [f(phases_amplitudes) for f in self.objectives]
            value = np.sum(result[0] for result in results)
            jac = np.sum(result[1] for result in results)
            return value, jac

    def __call__(self):
        # Initialize all parts of the objective function
        # Assemble objective function and jacobian function
        # Start optimization
        # Basin hopping? Check number of iterations?
        # Return phases?
        # self.initialize()
        # Set starting points
        if self.variable_amplitudes:
            start = np.concatenate((self.array.phases, self.array.amplitudes))
        else:
            start = self.array.phases
        # Set bounds for L-BFGS-B
        bounds = [(None, None)] * self.array.num_transducers
        if self.variable_amplitudes:
            bounds += [(1e-3, 1)] * self.array.num_transducers
        # TODO: The method selection should be configureable
        args = {'jac': True,  # self.objective_list[0][1]
                # 'method': 'BFGS', 'options': {'return_all': False, 'gtol': 5e-5, 'norm': 2, 'disp': True}}
                'method': 'L-BFGS-B', 'bounds': bounds, 'options': {'gtol': 1e-9, 'ftol': 1e-15}}
        if self.basinhopping:
            take_step = RadndomDisplacer(self.array.num_transducers, self.variable_amplitudes, stepsize=0.1)
            self.result = basinhopping(self.func_and_jac, start, T=1e-7, take_step=None, minimizer_kwargs=args, disp=True)
        else:
            self.result = minimize(self.func_and_jac, start, callback=None, **args)

        if self.variable_amplitudes:
            self.phases = self.result.x[:self.array.num_transducers]
            self.amplitudes = self.result.x[self.array.num_transducers:]
        else:
            self.phases = self.result.x
            self.amplitudes = self.array.amplitudes

        # self.result = minimize(self.function, self.array.phases, jac=self.jacobian, callback=None,
        # method='L-BFGS-B', bounds=[(-3*np.pi, 3*np.pi)]*self.array.num_transducers, options={'gtol': 1e-7, 'ftol': 1e-12})
        # method='BFGS', options={'return_all': True, 'gtol': 1e-5, 'norm': 2})


class RadndomDisplacer:
    def __init__(self, num_transducers, variable_amplitude=False, stepsize=0.05):
        self.stepsize = stepsize
        self.num_transducers = num_transducers
        self.variable_amplitude = variable_amplitude

    def __call__(self, x):
        if self.variable_amplitude:
            x[:self.num_transducers] += np.random.uniform(-np.pi * self.stepsize, np.pi * self.stepsize, self.num_transducers)
            x[:self.num_transducers] = np.mod(x[:self.num_transducers] + np.pi, 2 * np.pi) - np.pi  # Don't step out of bounds, instead wrap the phase
            x[self.num_transducers:] += np.random.uniform(-self.stepsize, self.stepsize, self.num_transducers)
            x[self.num_transducers:] = np.clip(x[self.num_transducers:], 1e-3, 1)  # Don't step out of bounds!
        else:
            x += np.random.uniform(-np.pi * self.stepsize, np.pi * self.stepsize, self.num_transducers)
        return x


def _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=False):
    if np.iscomplexobj(phases_amplitudes):
        if allow_complex:
            phases = np.angle(phases_amplitudes)
            amplitudes = np.abs(phases_amplitudes)
            variable_amplitudes = None
        else:
            raise NotImplementedError('Jacobian does not exist for complex inputs!')
    elif phases_amplitudes.size == num_transducers:
        phases = phases_amplitudes
        amplitudes = np.ones(num_transducers)
        variable_amplitudes = False
    elif phases_amplitudes.size == 2 * num_transducers:
        phases = phases_amplitudes.ravel()[:num_transducers]
        amplitudes = phases_amplitudes.ravel()[num_transducers:]
        variable_amplitudes = True
    return phases, amplitudes, variable_amplitudes


def gorkov_divergence(array, location, weights=None, spatial_derivatives=None, c_sphere=2350, rho_sphere=25, radius_sphere=1e-3, array_mask=None):
    num_transducers = array.num_transducers
    if array_mask is None:
        array_mask = num_transducers * [True]
    if spatial_derivatives is None:
        spatial_derivatives = array.spatial_derivatives(location, orders=2)

    V = 4 / 3 * np.pi * radius_sphere**3
    rho_air = models.rho_air
    c_air = models.c_air
    compressibility_air = 1 / (rho_air * c_air**2)
    compressibility_sphere = 1 / (rho_sphere * c_sphere**2)
    monopole_coefficient = 1 - compressibility_sphere / compressibility_air  # f_1 in H. Bruus 2012
    dipole_coefficient = 2 * (rho_sphere / rho_air - 1) / (2 * rho_sphere / rho_air + 1)   # f_2 in H. Bruus 2012
    preToVel = 1 / (array.omega * rho_air)  # Converting velocity to pressure gradient using equation of motion
    pressure_coefficient = V / 4 * compressibility_air * monopole_coefficient
    gradient_coefficient = V * 3 / 8 * dipole_coefficient * preToVel**2 * rho_air

    def calc_values(tot_der):
        p_squared = np.abs(tot_der[''])**2
        Ux = (pressure_coefficient * (tot_der['x'] * np.conj(tot_der[''])).real -
              gradient_coefficient * (tot_der['xx'] * np.conj(tot_der['x'])).real -
              gradient_coefficient * (tot_der['xy'] * np.conj(tot_der['y'])).real -
              gradient_coefficient * (tot_der['xz'] * np.conj(tot_der['z'])).real) * 2
        Uy = (pressure_coefficient * (tot_der['y'] * np.conj(tot_der[''])).real -
              gradient_coefficient * (tot_der['xy'] * np.conj(tot_der['x'])).real -
              gradient_coefficient * (tot_der['yy'] * np.conj(tot_der['y'])).real -
              gradient_coefficient * (tot_der['yz'] * np.conj(tot_der['z'])).real) * 2
        Uz = (pressure_coefficient * (tot_der['z'] * np.conj(tot_der[''])).real -
              gradient_coefficient * (tot_der['xz'] * np.conj(tot_der['x'])).real -
              gradient_coefficient * (tot_der['yz'] * np.conj(tot_der['y'])).real -
              gradient_coefficient * (tot_der['zz'] * np.conj(tot_der['z'])).real) * 2

        return p_squared, Ux, Uy, Uz

    def calc_jacobian(tot_der, ind_der):
        dp = 2 * tot_der[''] * np.conj(ind_der[''])
        dUx = (pressure_coefficient * (tot_der['x'] * np.conj(ind_der['']) + tot_der[''] * np.conj(ind_der['x'])) -
               gradient_coefficient * (tot_der['xx'] * np.conj(ind_der['x']) + tot_der['x'] * np.conj(ind_der['xx'])) -
               gradient_coefficient * (tot_der['xy'] * np.conj(ind_der['y']) + tot_der['y'] * np.conj(ind_der['xy'])) -
               gradient_coefficient * (tot_der['xz'] * np.conj(ind_der['z']) + tot_der['z'] * np.conj(ind_der['xz']))) * 2
        dUy = (pressure_coefficient * (tot_der['y'] * np.conj(ind_der['']) + tot_der[''] * np.conj(ind_der['y'])) -
               gradient_coefficient * (tot_der['xy'] * np.conj(ind_der['x']) + tot_der['x'] * np.conj(ind_der['xy'])) -
               gradient_coefficient * (tot_der['yy'] * np.conj(ind_der['y']) + tot_der['y'] * np.conj(ind_der['yy'])) -
               gradient_coefficient * (tot_der['yz'] * np.conj(ind_der['z']) + tot_der['z'] * np.conj(ind_der['yz']))) * 2
        dUz = (pressure_coefficient * (tot_der['z'] * np.conj(ind_der['']) + tot_der[''] * np.conj(ind_der['z'])) -
               gradient_coefficient * (tot_der['xz'] * np.conj(ind_der['x']) + tot_der['x'] * np.conj(ind_der['xz'])) -
               gradient_coefficient * (tot_der['yz'] * np.conj(ind_der['y']) + tot_der['y'] * np.conj(ind_der['yz'])) -
               gradient_coefficient * (tot_der['zz'] * np.conj(ind_der['z']) + tot_der['z'] * np.conj(ind_der['zz']))) * 2

        return dp, dUx, dUy, dUz

    if weights is None:
        def gorkov_divergence(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=True)
            complex_coeff = amplitudes * np.exp(1j * phases)
            tot_der = {}
            for key, value in spatial_derivatives.items():
                tot_der[key] = np.sum(complex_coeff * value)
            _, Ux, Uy, Uz = calc_values(tot_der)
            return Ux, Uy, Uz
    else:
        if len(weights) == 4:
            wp, wx, wy, wz = weights
        elif len(weights) == 3:
            wx, wy, wz = weights
            wp = 0

        def gorkov_divergence(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=False)
            complex_coeff = amplitudes[array_mask] * np.exp(1j * phases[array_mask])
            ind_der = {}
            tot_der = {}
            for key, value in spatial_derivatives.items():
                ind_der[key] = complex_coeff * value
                tot_der[key] = np.sum(ind_der[key])

            p_squared, Ux, Uy, Uz = calc_values(tot_der)
            dp, dUx, dUy, dUz = calc_jacobian(tot_der, ind_der)
            value = wp * p_squared + wx * Ux + wy * Uy + wz * Uz
            jacobian = np.zeros(num_transducers, dtype=np.complex128)
            jacobian[array_mask] = wp * dp + wx * dUx + wy * dUy + wz * dUz

            if variable_amplitudes:
                return value, np.concatenate((jacobian.imag, jacobian.real / amplitudes))
            else:
                return value, jacobian.imag

    return gorkov_divergence


def second_order_force(array, location, weights=None, spatial_derivatives=None, c_sphere=2350, rho_sphere=25, radius_sphere=1e-3, array_mask=None):
    num_transducers = array.num_transducers
    if array_mask is None:
        array_mask = array.num_transducers * [True]
    if spatial_derivatives is None:
        spatial_derivatives = array.spatial_derivatives(location, orders=2)

    for key in spatial_derivatives:
        spatial_derivatives[key] = spatial_derivatives[key][array_mask]

    c_air = models.c_air
    rho_air = models.rho_air
    compressibility_air = 1 / (rho_air * c_air**2)
    compressibility_sphere = 1 / (rho_sphere * c_sphere**2)
    f_1 = 1 - compressibility_sphere / compressibility_air  # f_1 in H. Bruus 2012
    f_2 = 2 * (rho_sphere / rho_air - 1) / (2 * rho_sphere / rho_air + 1)   # f_2 in H. Bruus 2012

    ka = array.k * radius_sphere
    psi_0 = -2 * ka**6 / 9 * (f_1**2 + f_2**2 / 4 + f_1 * f_2) - 1j * ka**3 / 3 * (2 * f_1 + f_2)
    psi_1 = -ka**6 / 18 * f_2**2 + 1j * ka**3 / 3 * f_2
    force_coeff = -np.pi / array.k**5 * compressibility_air

    def calc_values(tot_der):
        Fx = (1j * array.k**2 * (psi_0 * tot_der[''] * np.conj(tot_der['x']) +
                                 psi_1 * tot_der['x']) * np.conj(tot_der['']) +
              1j * 3 * psi_1 * (tot_der['x'] * np.conj(tot_der['xx']) +
                                tot_der['y'] * np.conj(tot_der['xy']) +
                                tot_der['z'] * np.conj(tot_der['xz']))
              ).real * force_coeff
        Fy = (1j * array.k**2 * (psi_0 * tot_der[''] * np.conj(tot_der['y']) +
                                 psi_1 * tot_der['y']) * np.conj(tot_der['']) +
              1j * 3 * psi_1 * (tot_der['x'] * np.conj(tot_der['xy']) +
                                tot_der['y'] * np.conj(tot_der['yy']) +
                                tot_der['z'] * np.conj(tot_der['yz']))
              ).real * force_coeff
        Fz = (1j * array.k**2 * (psi_0 * tot_der[''] * np.conj(tot_der['z']) +
                                 psi_1 * tot_der['z']) * np.conj(tot_der['']) +
              1j * 3 * psi_1 * (tot_der['x'] * np.conj(tot_der['xz']) +
                                tot_der['y'] * np.conj(tot_der['yz']) +
                                tot_der['z'] * np.conj(tot_der['zz']))
              ).real * force_coeff
        return Fx, Fy, Fz

    def calc_jacobian(tot_der, ind_der):
        dFx = (1j * array.k**2 * (psi_0 * tot_der[''] * np.conj(ind_der['x']) - np.conj(psi_0) * tot_der['x'] * np.conj(ind_der['']) +
                                  psi_1 * tot_der['x'] * np.conj(ind_der['']) - np.conj(psi_1) * tot_der[''] * np.conj(ind_der['x'])) +
               1j * 3 * (psi_1 * tot_der['x'] * np.conj(ind_der['xx']) - np.conj(psi_1) * tot_der['xx'] * np.conj(ind_der['x']) +
                         psi_1 * tot_der['y'] * np.conj(ind_der['xy']) - np.conj(psi_1) * tot_der['xy'] * np.conj(ind_der['y']) +
                         psi_1 * tot_der['z'] * np.conj(ind_der['xz']) - np.conj(psi_1) * tot_der['xz'] * np.conj(ind_der['z']))
               ) * force_coeff
        dFy = (1j * array.k**2 * (psi_0 * tot_der[''] * np.conj(ind_der['y']) - np.conj(psi_0) * tot_der['y'] * np.conj(ind_der['']) +
                                  psi_1 * tot_der['y'] * np.conj(ind_der['']) - np.conj(psi_1) * tot_der[''] * np.conj(ind_der['y'])) +
               1j * 3 * (psi_1 * tot_der['x'] * np.conj(ind_der['xy']) - np.conj(psi_1) * tot_der['xy'] * np.conj(ind_der['x']) +
                         psi_1 * tot_der['y'] * np.conj(ind_der['yy']) - np.conj(psi_1) * tot_der['yy'] * np.conj(ind_der['y']) +
                         psi_1 * tot_der['z'] * np.conj(ind_der['yz']) - np.conj(psi_1) * tot_der['yz'] * np.conj(ind_der['z']))
               ) * force_coeff
        dFz = (1j * array.k**2 * (psi_0 * tot_der[''] * np.conj(ind_der['z']) - np.conj(psi_0) * tot_der['z'] * np.conj(ind_der['']) +
                                  psi_1 * tot_der['z'] * np.conj(ind_der['']) - np.conj(psi_1) * tot_der[''] * np.conj(ind_der['z'])) +
               1j * 3 * (psi_1 * tot_der['x'] * np.conj(ind_der['xz']) - np.conj(psi_1) * tot_der['xz'] * np.conj(ind_der['x']) +
                         psi_1 * tot_der['y'] * np.conj(ind_der['yz']) - np.conj(psi_1) * tot_der['yz'] * np.conj(ind_der['y']) +
                         psi_1 * tot_der['z'] * np.conj(ind_der['zz']) - np.conj(psi_1) * tot_der['zz'] * np.conj(ind_der['z']))
               ) * force_coeff
        return dFx, dFy, dFz

    if weights is None:
        def second_order_force(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=True)
            complex_coeff = amplitudes * np.exp(1j * phases)
            tot_der = {}
            for key, value in spatial_derivatives.items():
                tot_der[key] = np.sum(complex_coeff * value)
            return calc_values(tot_der)
    else:
        wx, wy, wz = weights

        def second_order_force(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=False)
            complex_coeff = amplitudes[array_mask] * np.exp(1j * phases[array_mask])
            ind_der = {}
            tot_der = {}
            for key, value in spatial_derivatives.items():
                ind_der[key] = complex_coeff * value
                tot_der[key] = np.sum(ind_der[key])

            Fx, Fy, Fz = calc_values(tot_der)
            dFx, dFy, dFz = calc_jacobian(tot_der, ind_der)
            value = wx * Fx + wy * Fy + wz * Fz
            jacobian = np.zeros(num_transducers, dtype=np.complex128)
            jacobian[array_mask] = wx * dFx + wy * dFy + wz * dFz

            if variable_amplitudes:
                return value, np.concatenate((jacobian.imag, jacobian.real / amplitudes))
            else:
                return value, jacobian.imag
    return second_order_force


def gorkov_laplacian(array, location, weights=None, spatial_derivatives=None, c_sphere=2350, rho_sphere=25, radius_sphere=1e-3, array_mask=None):
    # Before defining the cost function and the jacobian, we need to initialize the following variables:
    num_transducers = array.num_transducers
    if array_mask is None:
        array_mask = array.num_transducers * [True]
    if spatial_derivatives is None:
        spatial_derivatives = array.spatial_derivatives(location)

    for key in spatial_derivatives:
        spatial_derivatives[key] = spatial_derivatives[key][array_mask]

    c_air = models.c_air
    rho_air = models.rho_air
    V = 4 / 3 * np.pi * radius_sphere**3
    compressibility_air = 1 / (rho_air * c_air**2)
    compressibility_sphere = 1 / (rho_sphere * c_sphere**2)
    monopole_coefficient = 1 - compressibility_sphere / compressibility_air  # f_1 in H. Bruus 2012
    dipole_coefficient = 2 * (rho_sphere / rho_air - 1) / (2 * rho_sphere / rho_air + 1)   # f_2 in H. Bruus 2012
    preToVel = 1 / (array.omega * rho_air)  # Converting velocity to pressure gradient using equation of motion
    pressure_coefficient = V / 4 * compressibility_air * monopole_coefficient
    gradient_coefficient = V * 3 / 8 * dipole_coefficient * preToVel**2 * rho_air

    def calc_values(tot_der):
        p_squared = np.abs(tot_der[''])**2
        Uxx = (pressure_coefficient * (tot_der['xx'] * np.conj(tot_der['']) + tot_der['x'] * np.conj(tot_der['x'])).real -
               gradient_coefficient * (tot_der['xxx'] * np.conj(tot_der['x']) + tot_der['xx'] * np.conj(tot_der['xx'])).real -
               gradient_coefficient * (tot_der['xxy'] * np.conj(tot_der['y']) + tot_der['xy'] * np.conj(tot_der['xy'])).real -
               gradient_coefficient * (tot_der['xxz'] * np.conj(tot_der['z']) + tot_der['xz'] * np.conj(tot_der['xz'])).real) * 2
        Uyy = (pressure_coefficient * (tot_der['yy'] * np.conj(tot_der['']) + tot_der['y'] * np.conj(tot_der['y'])).real -
               gradient_coefficient * (tot_der['yyx'] * np.conj(tot_der['x']) + tot_der['xy'] * np.conj(tot_der['xy'])).real -
               gradient_coefficient * (tot_der['yyy'] * np.conj(tot_der['y']) + tot_der['yy'] * np.conj(tot_der['yy'])).real -
               gradient_coefficient * (tot_der['yyz'] * np.conj(tot_der['z']) + tot_der['yz'] * np.conj(tot_der['yz'])).real) * 2
        Uzz = (pressure_coefficient * (tot_der['zz'] * np.conj(tot_der['']) + tot_der['z'] * np.conj(tot_der['z'])).real -
               gradient_coefficient * (tot_der['zzx'] * np.conj(tot_der['x']) + tot_der['xz'] * np.conj(tot_der['xz'])).real -
               gradient_coefficient * (tot_der['zzy'] * np.conj(tot_der['y']) + tot_der['yz'] * np.conj(tot_der['yz'])).real -
               gradient_coefficient * (tot_der['zzz'] * np.conj(tot_der['z']) + tot_der['zz'] * np.conj(tot_der['zz'])).real) * 2
        return p_squared, Uxx, Uyy, Uzz

    def calc_jacobian(tot_der, ind_der):
        dp = 2 * tot_der[''] * np.conj(ind_der[''])
        dUxx = (pressure_coefficient * (tot_der['xx'] * np.conj(ind_der['']) + tot_der[''] * np.conj(ind_der['xx']) + 2 * tot_der['x'] * np.conj(ind_der['x'])) -
                gradient_coefficient * (tot_der['xxx'] * np.conj(ind_der['x']) + tot_der['x'] * np.conj(ind_der['xxx']) + 2 * tot_der['xx'] * np.conj(ind_der['xx'])) -
                gradient_coefficient * (tot_der['xxy'] * np.conj(ind_der['y']) + tot_der['y'] * np.conj(ind_der['xxy']) + 2 * tot_der['xy'] * np.conj(ind_der['xy'])) -
                gradient_coefficient * (tot_der['xxz'] * np.conj(ind_der['z']) + tot_der['z'] * np.conj(ind_der['xxz']) + 2 * tot_der['xz'] * np.conj(ind_der['xz']))) * 2
        dUyy = (pressure_coefficient * (tot_der['yy'] * np.conj(ind_der['']) + tot_der[''] * np.conj(ind_der['yy']) + 2 * tot_der['y'] * np.conj(ind_der['y'])) -
                gradient_coefficient * (tot_der['yyx'] * np.conj(ind_der['x']) + tot_der['x'] * np.conj(ind_der['yyx']) + 2 * tot_der['xy'] * np.conj(ind_der['xy'])) -
                gradient_coefficient * (tot_der['yyy'] * np.conj(ind_der['y']) + tot_der['y'] * np.conj(ind_der['yyy']) + 2 * tot_der['yy'] * np.conj(ind_der['yy'])) -
                gradient_coefficient * (tot_der['yyz'] * np.conj(ind_der['z']) + tot_der['z'] * np.conj(ind_der['yyz']) + 2 * tot_der['yz'] * np.conj(ind_der['yz']))) * 2
        dUzz = (pressure_coefficient * (tot_der['zz'] * np.conj(ind_der['']) + tot_der[''] * np.conj(ind_der['zz']) + 2 * tot_der['z'] * np.conj(ind_der['z'])) -
                gradient_coefficient * (tot_der['zzx'] * np.conj(ind_der['x']) + tot_der['x'] * np.conj(ind_der['zzx']) + 2 * tot_der['xz'] * np.conj(ind_der['xz'])) -
                gradient_coefficient * (tot_der['zzy'] * np.conj(ind_der['y']) + tot_der['y'] * np.conj(ind_der['zzy']) + 2 * tot_der['yz'] * np.conj(ind_der['yz'])) -
                gradient_coefficient * (tot_der['zzz'] * np.conj(ind_der['z']) + tot_der['z'] * np.conj(ind_der['zzz']) + 2 * tot_der['zz'] * np.conj(ind_der['zz']))) * 2
        return dp, dUxx, dUyy, dUzz

    if weights is None:
        def gorkov_laplacian(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=True)
            complex_coeff = amplitudes[array_mask] * np.exp(1j * phases[array_mask])
            tot_der = {}
            for key, value in spatial_derivatives.items():
                tot_der[key] = np.sum(complex_coeff * value)

            _, Uxx, Uyy, Uzz = calc_values(tot_der)
            return Uxx, Uyy, Uzz

    else:
        if len(weights) == 4:
            wp, wx, wy, wz = weights
        elif len(weights) == 3:
            wx, wy, wz = weights
            wp = 0

        def gorkov_laplacian(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=False)
            complex_coeff = amplitudes[array_mask] * np.exp(1j * phases[array_mask])
            ind_der = {}
            tot_der = {}
            for key, value in spatial_derivatives.items():
                ind_der[key] = complex_coeff * value
                tot_der[key] = np.sum(ind_der[key])

            p_squared, Uxx, Uyy, Uzz = calc_values(tot_der)
            dp, dUxx, dUyy, dUzz = calc_jacobian(tot_der, ind_der)
            value = wp * p_squared + wx * Uxx + wy * Uyy + wz * Uzz
            jacobian = np.zeros(num_transducers, dtype=np.complex128)
            jacobian[array_mask] = wp * dp + wx * dUxx + wy * dUyy + wz * dUzz

            if variable_amplitudes:
                return value, np.concatenate((jacobian.imag, jacobian.real / amplitudes))
            else:
                return value, jacobian.imag

    return gorkov_laplacian


def amplitude_limiting(array, bounds=(1e-3, 1 - 1e-3), order=4, scaling=10, array_mask=None):
    num_transducers = array.num_transducers
    if array_mask is None:
        array_mask = array.num_transducers * [True]
    lower_bound = np.asarray(bounds).min()
    upper_bound = np.asarray(bounds).max()

    def amplitude_limiting(phases_amplitudes):
        # Note that this only makes sense as a const function, and only for variable amplitudes,
        # so no implementation for complex inputs is needed.
        _, amplitudes, variable_amps = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=False)
        if not variable_amps:
            return 0, np.zeros(num_transducers)
        under_idx = amplitudes[array_mask] < lower_bound
        over_idx = amplitudes[array_mask] > upper_bound
        under = scaling * (lower_bound - amplitudes[under_idx])
        over = scaling * (amplitudes[over_idx] - upper_bound)

        value = (under**order + over**order).sum()
        jacobian = np.zeros(2 * num_transducers)
        jacobian[array_mask][num_transducers + under_idx] = under**(order - 1) * order
        jacobian[array_mask][num_transducers + over_idx] = over**(order - 1) * order

        return value, jacobian
    return amplitude_limiting


def pressure_null(array, location, weights=None, spatial_derivatives=None, array_mask=None):
    num_transducers = array.num_transducers
    if spatial_derivatives is None:
        spatial_derivatives = array.spatial_derivatives(location, orders=1)
    if array_mask is None:
        array_mask = array.num_transducers * [True]
    for key in spatial_derivatives:
        spatial_derivatives[key] = spatial_derivatives[key][array_mask]
    gradient_scale = 1 / array.k**2
    wp, wx, wy, wz = weights

    def calc_values(complex_coeff):
        p = np.sum(complex_coeff * spatial_derivatives[''])
        px = np.sum(complex_coeff * spatial_derivatives['x'])
        py = np.sum(complex_coeff * spatial_derivatives['y'])
        pz = np.sum(complex_coeff * spatial_derivatives['y'])

        return p, px, py, pz

    def calc_jacobian(complex_coeff, values):
        p, px, py, pz = values
        dp = 2 * p * np.conj(complex_coeff * spatial_derivatives[''])
        dpx = 2 * px * np.conj(complex_coeff * spatial_derivatives['x'])
        dpy = 2 * py * np.conj(complex_coeff * spatial_derivatives['y'])
        dpz = 2 * pz * np.conj(complex_coeff * spatial_derivatives['z'])

        return dp, dpx, dpy, dpz

    if weights is None:
        def pressure_null(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=True)
            complex_coeff = amplitudes[array_mask] * np.exp(1j * phases[array_mask])
            return calc_values(complex_coeff)
    else:
        if len(weights) == 4:
            wp, wx, wy, wz = weights
        elif len(weights) == 3:
            wx, wy, wz = weights
            wp = 0
        elif len(weights) == 1:
            wp = weights
            wx = wy = wz = 0

        def pressure_null(phases_amplitudes):
            phases, amplitudes, variable_amplitudes = _phase_and_amplitude_input(phases_amplitudes, num_transducers, allow_complex=False)
            complex_coeff = amplitudes[array_mask] * np.exp(1j * phases[array_mask])

            p, px, py, pz = calc_values(complex_coeff)
            dp, dpx, dpy, dpz = calc_jacobian(complex_coeff, (p, px, py, pz))

            value = wp * np.abs(p)**2 + (wx * np.abs(px)**2 + wy * np.abs(py)**2 + wz * np.abs(pz)**2) * gradient_scale
            jacobian = np.zeros(num_transducers, dtype=np.complex128)
            jacobian[array_mask] = wp * dp + (wx * dpx + wy * dpy + wz * dpz) * gradient_scale
            if variable_amplitudes:
                return value, np.concatenate((jacobian.imag, jacobian.real / amplitudes))
            else:
                return value, jacobian.imag
    return pressure_null
