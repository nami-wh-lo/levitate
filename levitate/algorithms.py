"""A collection of levitation related mathematical implementations."""

import numpy as np
from . import materials
from ._algorithm import algorithm, requires


@algorithm
def gorkov_gradient(array, radius_sphere=1e-3, sphere_material=materials.Styrofoam):
    """
    Create gorkov gradient calculation functions.

    Creates functions which calculates the gorkov gradient and the jacobian of
    the field specified using spaial derivatives of the pressure.

    Parameters
    ----------
    array : TransducerArray
        The object modeling the array.
    radius_sphere : float, default 1e-3
        Radius of the spherical beads.
    sphere_material : Material
        The material of the sphere, default Styrofoam.
    """
    V = 4 / 3 * np.pi * radius_sphere**3
    monopole_coefficient = 1 - sphere_material.compressibility / array.medium.compressibility  # f_1 in H. Bruus 2012
    dipole_coefficient = 2 * (sphere_material.rho / array.medium.rho - 1) / (2 * sphere_material.rho / array.medium.rho + 1)   # f_2 in H. Bruus 2012
    preToVel = 1 / (array.omega * array.medium.rho)  # Converting velocity to pressure gradient using equation of motion
    pressure_coefficient = V / 4 * array.medium.compressibility * monopole_coefficient
    gradient_coefficient = V * 3 / 8 * dipole_coefficient * preToVel**2 * array.medium.rho

    @requires(pressure_derivs_summed=2)
    def calc_values(pressure_derivs_summed):
        values = np.real(pressure_coefficient * np.conj(pressure_derivs_summed[0]) * pressure_derivs_summed[1:4])  # Pressure parts
        values -= np.real(gradient_coefficient * np.conj(pressure_derivs_summed[1]) * pressure_derivs_summed[[4, 7, 8]])  # Vx parts
        values -= np.real(gradient_coefficient * np.conj(pressure_derivs_summed[2]) * pressure_derivs_summed[[7, 5, 9]])  # Vy parts
        values -= np.real(gradient_coefficient * np.conj(pressure_derivs_summed[3]) * pressure_derivs_summed[[8, 9, 6]])  # Vz parts
        return values * 2

    @requires(pressure_derivs_summed=2, pressure_derivs_individual=2)
    def calc_jacobians(pressure_derivs_summed, pressure_derivs_individual):
        jacobians = pressure_coefficient * (np.conj(pressure_derivs_summed[0]) * pressure_derivs_individual[1:4] + np.conj(pressure_derivs_summed[1:4, None]) * pressure_derivs_individual[0])  # Pressure parts
        jacobians -= gradient_coefficient * (np.conj(pressure_derivs_summed[1]) * pressure_derivs_individual[[4, 7, 8]] + np.conj(pressure_derivs_summed[[4, 7, 8], None]) * pressure_derivs_individual[1])  # Vx parts
        jacobians -= gradient_coefficient * (np.conj(pressure_derivs_summed[2]) * pressure_derivs_individual[[7, 5, 9]] + np.conj(pressure_derivs_summed[[7, 5, 9], None]) * pressure_derivs_individual[2])  # Vy parts
        jacobians -= gradient_coefficient * (np.conj(pressure_derivs_summed[3]) * pressure_derivs_individual[[8, 9, 6]] + np.conj(pressure_derivs_summed[[8, 9, 6], None]) * pressure_derivs_individual[3])  # Vz parts
        return jacobians * 2
    return calc_values, calc_jacobians


@algorithm
def gorkov_laplacian(array, radius_sphere=1e-3, sphere_material=materials.Styrofoam):
    """
    Create gorkov laplacian calculation functions.

    Creates functions which calculates the laplacian of the gorkov potential
    and the jacobian of the field specified using spaial derivatives of the pressure.

    Parameters
    ----------
    array : TransducerArray
        The object modeling the array.
    radius_sphere : float, default 1e-3
        Radius of the spherical beads.
    sphere_material : Material
        The material of the sphere, default Styrofoam.
    """
    V = 4 / 3 * np.pi * radius_sphere**3
    monopole_coefficient = 1 - sphere_material.compressibility / array.medium.compressibility  # f_1 in H. Bruus 2012
    dipole_coefficient = 2 * (sphere_material.rho / array.medium.rho - 1) / (2 * sphere_material.rho / array.medium.rho + 1)   # f_2 in H. Bruus 2012
    preToVel = 1 / (array.omega * array.medium.rho)  # Converting velocity to pressure gradient using equation of motion
    pressure_coefficient = V / 4 * array.medium.compressibility * monopole_coefficient
    gradient_coefficient = V * 3 / 8 * dipole_coefficient * preToVel**2 * array.medium.rho

    @requires(pressure_derivs_summed=3)
    def calc_values(pressure_derivs_summed):
        values = np.real(pressure_coefficient * (np.conj(pressure_derivs_summed[0]) * pressure_derivs_summed[[4, 5, 6]] + pressure_derivs_summed[[1, 2, 3]] * np.conj(pressure_derivs_summed[[1, 2, 3]])))
        values -= np.real(gradient_coefficient * (np.conj(pressure_derivs_summed[1]) * pressure_derivs_summed[[10, 15, 17]] + pressure_derivs_summed[[4, 7, 8]] * np.conj(pressure_derivs_summed[[4, 7, 8]])))
        values -= np.real(gradient_coefficient * (np.conj(pressure_derivs_summed[2]) * pressure_derivs_summed[[13, 11, 18]] + pressure_derivs_summed[[7, 5, 9]] * np.conj(pressure_derivs_summed[[7, 5, 9]])))
        values -= np.real(gradient_coefficient * (np.conj(pressure_derivs_summed[3]) * pressure_derivs_summed[[14, 16, 12]] + pressure_derivs_summed[[8, 9, 6]] * np.conj(pressure_derivs_summed[[8, 9, 6]])))
        return values * 2

    @requires(pressure_derivs_summed=3, pressure_derivs_individual=3)
    def calc_jacobians(pressure_derivs_summed, pressure_derivs_individual):
        jacobians = pressure_coefficient * (np.conj(pressure_derivs_summed[0]) * pressure_derivs_individual[[4, 5, 6]] + np.conj(pressure_derivs_summed[[4, 5, 6], None]) * pressure_derivs_individual[0] + 2 * np.conj(pressure_derivs_summed[[1, 2, 3], None]) * pressure_derivs_individual[[1, 2, 3]])
        jacobians -= gradient_coefficient * (np.conj(pressure_derivs_summed[1]) * pressure_derivs_individual[[10, 15, 17]] + np.conj(pressure_derivs_summed[[10, 15, 17], None]) * pressure_derivs_individual[1] + 2 * np.conj(pressure_derivs_summed[[4, 7, 8], None]) * pressure_derivs_individual[[4, 7, 8]])
        jacobians -= gradient_coefficient * (np.conj(pressure_derivs_summed[2]) * pressure_derivs_individual[[13, 11, 18]] + np.conj(pressure_derivs_summed[[13, 11, 18], None]) * pressure_derivs_individual[2] + 2 * np.conj(pressure_derivs_summed[[7, 5, 9], None]) * pressure_derivs_individual[[7, 5, 9]])
        jacobians -= gradient_coefficient * (np.conj(pressure_derivs_summed[3]) * pressure_derivs_individual[[14, 16, 12]] + np.conj(pressure_derivs_summed[[14, 16, 12], None]) * pressure_derivs_individual[3] + 2 * np.conj(pressure_derivs_summed[[8, 9, 6], None]) * pressure_derivs_individual[[8, 9, 6]])
        return jacobians * 2
    return calc_values, calc_jacobians


@algorithm
def second_order_force(array, radius_sphere=1e-3, sphere_material=materials.Styrofoam):
    """
    Create second order radiation force calculation functions.

    Creates functions which calculates the radiation force on a sphere generated
    by the field specified using spaial derivatives of the pressure, and the
    corresponding jacobians.

    This is more suitable than the Gor'kov formulation for use with progressive
    wave fiends, e.g. single sided arrays, see https://doi.org/10.1121/1.4773924.

    Parameters
    ----------
    array : TransducerArray
        The object modeling the array.
    radius_sphere : float, default 1e-3
        Radius of the spherical beads.
    sphere_material : Material
        The material of the sphere, default Styrofoam.
    """
    f_1 = 1 - sphere_material.compressibility / array.medium.compressibility  # f_1 in H. Bruus 2012
    f_2 = 2 * (sphere_material.rho / array.medium.rho - 1) / (2 * sphere_material.rho / array.medium.rho + 1)   # f_2 in H. Bruus 2012

    ka = array.k * radius_sphere
    k_square = array.k**2
    psi_0 = -2 * ka**6 / 9 * (f_1**2 + f_2**2 / 4 + f_1 * f_2) - 1j * ka**3 / 3 * (2 * f_1 + f_2)
    psi_1 = -ka**6 / 18 * f_2**2 + 1j * ka**3 / 3 * f_2
    force_coeff = -np.pi / array.k**5 * array.medium.compressibility

    # Including the j factors from the paper directly in the coefficients.
    psi_0 *= 1j
    psi_1 *= 1j

    @requires(pressure_derivs_summed=2)
    def calc_values(pressure_derivs_summed):
        values = np.real(k_square * psi_0 * pressure_derivs_summed[0] * np.conj(pressure_derivs_summed[[1, 2, 3]]))
        values += np.real(k_square * psi_1 * pressure_derivs_summed[[1, 2, 3]] * np.conj(pressure_derivs_summed[0]))
        values += np.real(3 * psi_1 * pressure_derivs_summed[1] * np.conj(pressure_derivs_summed[[4, 7, 8]]))
        values += np.real(3 * psi_1 * pressure_derivs_summed[2] * np.conj(pressure_derivs_summed[[7, 5, 9]]))
        values += np.real(3 * psi_1 * pressure_derivs_summed[3] * np.conj(pressure_derivs_summed[[8, 9, 6]]))
        return values * force_coeff

    @requires(pressure_derivs_summed=2, pressure_derivs_individual=2)
    def calc_jacobians(pressure_derivs_summed, pressure_derivs_individual):
        jacobians = k_square * (psi_0 * pressure_derivs_individual[0] * np.conj(pressure_derivs_summed[[1, 2, 3], None]) + np.conj(psi_0) * np.conj(pressure_derivs_summed[0]) * pressure_derivs_individual[[1, 2, 3]])
        jacobians += k_square * (psi_1 * pressure_derivs_individual[[1, 2, 3]] * np.conj(pressure_derivs_summed[0]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[[1, 2, 3], None]) * pressure_derivs_individual[0])
        jacobians += 3 * (psi_1 * pressure_derivs_individual[1] * np.conj(pressure_derivs_summed[[4, 7, 8], None]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[1]) * pressure_derivs_individual[[4, 7, 8]])
        jacobians += 3 * (psi_1 * pressure_derivs_individual[2] * np.conj(pressure_derivs_summed[[7, 5, 9], None]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[2]) * pressure_derivs_individual[[7, 5, 9]])
        jacobians += 3 * (psi_1 * pressure_derivs_individual[3] * np.conj(pressure_derivs_summed[[8, 9, 6], None]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[3]) * pressure_derivs_individual[[8, 9, 6]])
        return jacobians * force_coeff
    return calc_values, calc_jacobians


@algorithm
def second_order_stiffness(array, radius_sphere=1e-3, sphere_material=materials.Styrofoam):
    """
    Create second order radiation stiffness calculation functions.

    Creates functions which calculates the radiation stiffness on a sphere
    generated by the field specified using spaial derivatives of
    the pressure, and the corresponding jacobians.

    This is more suitable than the Gor'kov formulation for use with progressive
    wave fiends, e.g. single sided arrays, see https://doi.org/10.1121/1.4773924.

    Parameters
    ----------
    array : TransducerArray
        The object modeling the array.
    radius_sphere : float, default 1e-3
        Radius of the spherical beads.
    sphere_material : Material
        The material of the sphere, default Styrofoam.
    """
    f_1 = 1 - sphere_material.compressibility / array.medium.compressibility  # f_1 in H. Bruus 2012
    f_2 = 2 * (sphere_material.rho / array.medium.rho - 1) / (2 * sphere_material.rho / array.medium.rho + 1)   # f_2 in H. Bruus 2012

    ka = array.k * radius_sphere
    k_square = array.k**2
    psi_0 = -2 * ka**6 / 9 * (f_1**2 + f_2**2 / 4 + f_1 * f_2) - 1j * ka**3 / 3 * (2 * f_1 + f_2)
    psi_1 = -ka**6 / 18 * f_2**2 + 1j * ka**3 / 3 * f_2
    force_coeff = -np.pi / array.k**5 * array.medium.compressibility

    # Including the j factors from the paper directly in the coefficients.
    psi_0 *= 1j
    psi_1 *= 1j

    @requires(pressure_derivs_summed=3)
    def calc_values(pressure_derivs_summed):
        values = np.real(k_square * psi_0 * (pressure_derivs_summed[0] * np.conj(pressure_derivs_summed[[4, 5, 6]]) + pressure_derivs_summed[[1, 2, 3]] * np.conj(pressure_derivs_summed[[1, 2, 3]])))
        values += np.real(k_square * psi_1 * (pressure_derivs_summed[[4, 5, 6]] * np.conj(pressure_derivs_summed[0]) + pressure_derivs_summed[[1, 2, 3]] * np.conj(pressure_derivs_summed[[1, 2, 3]])))
        values += np.real(3 * psi_1 * (pressure_derivs_summed[1] * np.conj(pressure_derivs_summed[[10, 15, 17]]) + pressure_derivs_summed[[4, 7, 8]] * np.conj(pressure_derivs_summed[[4, 7, 8]])))
        values += np.real(3 * psi_1 * (pressure_derivs_summed[2] * np.conj(pressure_derivs_summed[[13, 11, 18]]) + pressure_derivs_summed[[7, 5, 9]] * np.conj(pressure_derivs_summed[[7, 5, 9]])))
        values += np.real(3 * psi_1 * (pressure_derivs_summed[3] * np.conj(pressure_derivs_summed[[14, 16, 12]]) + pressure_derivs_summed[[8, 9, 6]] * np.conj(pressure_derivs_summed[[8, 9, 6]])))
        return values * force_coeff

    @requires(pressure_derivs_summed=3, pressure_derivs_individual=3)
    def calc_jacobians(pressure_derivs_summed, pressure_derivs_individual):
        jacobians = k_square * (psi_0 * pressure_derivs_individual[0] * np.conj(pressure_derivs_summed[[4, 5, 6], None]) + np.conj(psi_0) * np.conj(pressure_derivs_summed[0]) * pressure_derivs_individual[[4, 5, 6]] + (psi_0 + np.conj(psi_0)) * np.conj(pressure_derivs_summed[[1, 2, 3], None]) * pressure_derivs_individual[[1, 2, 3]])
        jacobians += k_square * (psi_1 * pressure_derivs_individual[[4, 5, 6]] * np.conj(pressure_derivs_summed[0]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[[4, 5, 6], None]) * pressure_derivs_individual[0] + (psi_1 + np.conj(psi_1)) * np.conj(pressure_derivs_summed[[1, 2, 3], None]) * pressure_derivs_individual[[1, 2, 3]])
        jacobians += 3 * (psi_1 * pressure_derivs_individual[1] * np.conj(pressure_derivs_summed[[10, 15, 17], None]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[1]) * pressure_derivs_individual[[10, 15, 17]] + (psi_1 + np.conj(psi_1)) * np.conj(pressure_derivs_summed[[4, 7, 8], None]) * pressure_derivs_individual[[4, 7, 8]])
        jacobians += 3 * (psi_1 * pressure_derivs_individual[2] * np.conj(pressure_derivs_summed[[13, 11, 18], None]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[2]) * pressure_derivs_individual[[13, 11, 18]] + (psi_1 + np.conj(psi_1)) * np.conj(pressure_derivs_summed[[7, 5, 9], None]) * pressure_derivs_individual[[7, 5, 9]])
        jacobians += 3 * (psi_1 * pressure_derivs_individual[3] * np.conj(pressure_derivs_summed[[14, 16, 12], None]) + np.conj(psi_1) * np.conj(pressure_derivs_summed[3]) * pressure_derivs_individual[[14, 16, 12]] + (psi_1 + np.conj(psi_1)) * np.conj(pressure_derivs_summed[[8, 9, 6], None]) * pressure_derivs_individual[[8, 9, 6]])
        return jacobians * force_coeff
    return calc_values, calc_jacobians


@algorithm
def pressure_squared_magnitude(array=None):
    """
    Create pressure squared magnitude calculation functions.

    Creates functions which calculates the squared pressure magnitude,
    and the corresponding jacobians.
    The main use of this is to use as a cost function.

    Parameters
    ----------
    array : TransducerArray
        The object modeling the array, optional.
    """
    @requires(pressure_derivs_summed=0)
    def calc_values(pressure_derivs_summed):
        return np.real(pressure_derivs_summed[0] * np.conj(pressure_derivs_summed[0]))[None, ...]

    @requires(pressure_derivs_summed=0, pressure_derivs_individual=0)
    def calc_jacobians(pressure_derivs_summed, pressure_derivs_individual):
        return (2 * np.conj(pressure_derivs_summed[0]) * pressure_derivs_individual[0])[None, ...]
    return calc_values, calc_jacobians


@algorithm
def velocity_squared_magnitude(array):
    """
    Create velocity squared magnitude calculation functions.

    Creates functions which calculates the squared velocity magnitude,
    as a vector, and the corresponding jacobians.
    The main use of this is to use as a cost function.

    Parameters
    ----------
    array : TransducerArray
        The object modeling the array.
    """
    pre_grad_2_vel_squared = 1 / (array.medium.rho * array.omega)**2

    @requires(pressure_derivs_summed=1)
    def calc_values(pressure_derivs_summed):
        return np.real(pre_grad_2_vel_squared * pressure_derivs_summed[1:4] * np.conj(pressure_derivs_summed[1:4]))

    @requires(pressure_derivs_summed=1, pressure_derivs_individual=1)
    def calc_jacobians(pressure_derivs_summed, pressure_derivs_individual):
        return 2 * pre_grad_2_vel_squared * np.conj(pressure_derivs_summed[1:4, None]) * pressure_derivs_individual[1:4]
    return calc_values, calc_jacobians
