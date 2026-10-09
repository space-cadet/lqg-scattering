"""Shared numerical summaries for research studies."""
import numpy as np

def fit_power(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = y > 0
    alpha, logc = np.polyfit(np.log(x[m]), np.log(y[m]), 1)
    yp = alpha * np.log(x[m]) + logc
    ss_res = float(np.sum((np.log(y[m]) - yp) ** 2))
    ss_tot = float(np.sum((np.log(y[m]) - np.log(y[m]).mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    lx, ly = np.log(x[m]), np.log(y[m])
    slopes = ((ly[1:] - ly[:-1]) / (lx[1:] - lx[:-1])).tolist()
    return {"alpha": float(alpha), "prefactor": float(np.exp(logc)),
            "r2": float(r2), "local_slopes": [float(s) for s in slopes]}

