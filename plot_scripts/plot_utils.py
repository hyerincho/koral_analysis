import numpy as np
import glob
import pickle
import os
import pdb

import pyharm
from matplotlib_settings import *
from ylabel_dictionary import *

def get_spin(D, verbose=False):
    try:
        a = D["spin"]
        if verbose:
            print("Found spin of", D["dump"]["a"])
    except:
        print("ERROR: cant find spin, now using a=0.9")
        a = 0.9  # for now
    return a

def calc_rEH(a):
    return 1.0 + np.sqrt(1.0 - a**2)

def eta_BZ6(a, phib, kappa=0.044):
    # kappa = 0.053 # split-monopole
    # kappa = 0.044 # parabolic
    rEH = calc_rEH(a)
    Omega = a / (2 * rEH)
    return 0.01 * kappa * (4.0 * np.pi) * np.power(phib * Omega, 2.0) * (1.0 + 1.38 * Omega**2 - 9.2 * Omega**4)  # from percentage to decimals

def phi_average(dump,quantity,sum_instead=False,mass_weight=True):
  if isinstance(quantity,str):
    to_average=np.copy(dump[quantity])
  else:
    to_average=np.copy(quantity)
  
  if mass_weight: weight = dump["rho"]
  else: weight = dump["1"]

  if sum_instead:
      return np.sum(to_average, axis=2)
  else:
      if dump['n3']>1:
        return np.sum(to_average * weight * np.sqrt(dump['gcov'][3,3]) * dump['dx3'], axis=2) / np.sum(weight * np.sqrt(dump['gcov'][3,3]) * dump['dx3'],axis=2)
      else:
        return to_average

def extract_quantity_from_dump(dump, quantity, at_r):
    if quantity == "Mdot":
        return -pyharm.shell_sum(dump, "FM", at_r=at_r)
    if quantity == "Edot":
        return -pyharm.shell_sum(dump, "FE", at_r=at_r)
    if quantity == "eta":
        Mdot = extract_quantity_from_dump(dump, "Mdot", at_r)
        Edot = extract_quantity_from_dump(dump, "Edot", at_r)
        return (Mdot - Edot) / Mdot
    if quantity == "Phib":
        return 0.5 * pyharm.shell_sum(dump, "abs_B1", at_r=at_r) * np.sqrt(4.0 * np.pi)
    if quantity == "phib":
        Mdot = extract_quantity_from_dump(dump, "Mdot", at_r)
        Phib = extract_quantity_from_dump(dump, "Phib", at_r)
        return Phib / np.sqrt(Mdot)
    if quantity == "Omega":
        uphi = extract_quantity_from_dump(dump, "u^phi", at_r)
        ut = extract_quantity_from_dump(dump, "u^t", at_r)
        return uphi / ut * np.power(at_r, 3. / 2)
    else:
        return pyharm.shell_sum(dump, dump[quantity] * dump["rho"], at_r=at_r) / pyharm.shell_sum(dump, dump["rho"], at_r=at_r)

def readQuantity(dictionary, quantity):
    invert = False
    if quantity == "beta":
        if "inv_beta" in dictionary["quantities"]:
            quantity = "inv_beta"
            invert = True
        else:
            print("inv_beta doesn't exist, so we will stick with beta.")
        quantity_index = dictionary["quantities"].index(quantity)
        profiles = [list[quantity_index] for list in dictionary["profiles"]]
    elif quantity == "Pg":
        if "Pg" in dictionary["quantities"]:
            quantity_index = dictionary["quantities"].index("Pg")
            profiles = [list[quantity_index] for list in dictionary["profiles"]]
        else:
            try:
                gam = dictionary["gam"]
            except:
                gam = 5.0 / 3.0
            quantity_index = dictionary["quantities"].index("u")
            profiles = [np.array(list[quantity_index]) * (gam - 1.0) for list in dictionary["profiles"]]
    elif quantity == "Pb":
        quantity_index = dictionary["quantities"].index("b")
        profiles = [np.array(list[quantity_index]) ** 2 / 2.0 for list in dictionary["profiles"]]
    else:
        # just reading the pre-calculated quantities
        quantity_index = dictionary["quantities"].index(quantity)
        profiles = [list[quantity_index] for list in dictionary["profiles"]]
    return profiles, invert

def readTimeSeries(D, quantity, radius=100, tmax=None):
    quantity_arr = np.array([])
    radii = D["radii"]
    times = D["times"]
    iRead = np.argmin(abs(radii - radius))
    profiles, _ = readQuantity(D, quantity)
    for i, profile in enumerate(profiles):
        quantity_arr = np.concatenate((quantity_arr, [np.array(profile)[iRead]]))
    if tmax is None:
        return quantity_arr #, times
    else:
        times = np.array(times)
        if times[-1] <= tmax:
            print("the time series not reached tmax of {:.3g} yet".format(tmax))
        i_keep = times < tmax
        return quantity_arr[i_keep], times[i_keep]

def processTimeSeries(D, quantity, use_Mdot_mean=True, average_factor=2.):
    store_Mdot10 = False
    if quantity == "eta" or quantity == "phib":
        store_Mdot10 = True

    if quantity == "eta":
        radius = 10 #5
        quantity_arr = readTimeSeries(D, "Edot", radius)
        quantity_arr2 = readTimeSeries(D, "Mdot", radius)
    elif quantity == "eta_EM":
        radius = 5
        quantity_arr = readTimeSeries(D, "Edot_EM", radius)
        quantity_arr2 = readTimeSeries(D, "Mdot", radius)
    elif quantity == "phib":
        try:
            a = get_spin(D)
        except:
            a = 0.5
            print("ERROR: cant find spin, now using a=0.5")
        rEH = calc_rEH(a)
        quantity_arr = readTimeSeries(D, "Phib", rEH)
    elif "Omega" in quantity:
        temp = quantity.replace("Omega", "")
        if len(temp) > 0:
            radius = float(temp)
        else:
            radius = 5  # 10 #50
        quantity_arr = readTimeSeries(D, "Omega", radius)
        quantity_arr *= np.power(radius, 3.0 / 2)
    else:
        radius = 5
        if "u^r" in quantity or "u^th" in quantity or "u^phi" in quantity: radius = 10
        quantity_arr = readTimeSeries(D, quantity, radius)

    if store_Mdot10:
        if use_Mdot_mean or 'radius' not in vars(): radius = 10
        Mdot_save = readTimeSeries(D, "Mdot", radius)

    if store_Mdot10 and use_Mdot_mean:
        Mdot_save = np.mean(Mdot_save[int(float(len(Mdot_save)) / average_factor) :])  # TODO: change this to time criterion by getting indices over t_half
    if quantity == "eta":
        quantity_arr = (quantity_arr2 - quantity_arr) / Mdot_save
    elif quantity == "eta_EM":
        quantity_arr = (-quantity_arr) / Mdot_save
    elif quantity == "phib":
        quantity_arr /= np.sqrt(Mdot_save)

    return quantity_arr
