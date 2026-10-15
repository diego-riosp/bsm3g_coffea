import warnings
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import f as f_dist


def poly_func(x, *coefs):
    return np.polyval(coefs, x)


def fit_polynomial(x, y, yerr, degree):
    p0 = np.ones(degree + 1)
    popt, pcov = curve_fit(
        poly_func, x, y, p0=p0, sigma=yerr, absolute_sigma=True, maxfev=10000
    )
    residuals = y - poly_func(x, *popt)
    chisq = np.sum((residuals / yerr) ** 2)
    ndof = len(x) - len(popt)
    return popt, pcov, chisq, ndof


def find_optimal_tf_poly(x, y, yerr, max_degree=5, alpha=0.05):
    n = len(x)
    
    if n == 0:
        warnings.warn(
            "No valid points for the fitting. Assigned grad = 0."
        )
        return 0, np.array([0.0]), np.array([[1.0]])

    if n == 1:
        popt = np.array([y[0]])
        pcov = np.array([[yerr[0] ** 2]])
        return 0, popt, pcov

    max_degree_possible = min(max_degree, n - 1)
    current_degree = 1

    try:
        popt1, pcov1, chisq1, ndof1 = fit_polynomial(x, y, yerr, current_degree)
    except Exception:
        mean_y = np.mean(y) if len(y) > 0 else 0.0
        return 0, np.array([mean_y]), np.array([[1.0]])

    for next_degree in range(2, max_degree_possible + 1):
        try:
            popt2, pcov2, chisq2, ndof2 = fit_polynomial(x, y, yerr, next_degree)
        except (RuntimeError, TypeError):
            break

        p1 = current_degree + 1
        p2 = next_degree + 1

        if (n - p2) <= 0:
            break

        numerator = (chisq1 - chisq2) / (p2 - p1)
        denominator = chisq2 / (n - p2)

        if denominator <= 0 or numerator < 0:
            break

        F_stat = numerator / denominator
        p_val = f_dist.sf(F_stat, p2 - p1, n - p2)

        if p_val < alpha:
            current_degree = next_degree
            popt1, pcov1, chisq1, ndof1 = popt2, pcov2, chisq2, ndof2
        else:
            break

    return current_degree, popt1, pcov1