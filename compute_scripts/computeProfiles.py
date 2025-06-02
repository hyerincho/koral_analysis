import os
import numpy as np
import glob
import h5py
import pdb
import pickle
import pyharm


def shellAverage(dump, quantity, imin=0, density_weight=True, pole_pad=1):
    """
    Starting with a pyharm dump object, average some quantity with respect to phi and theta.
    Includes some smart parsing of quantities that are not keys in the dump object.
    """

    # Many quantities we want are already keys, but some are not.  For those, we must come up with our own formula.

    ## quantities to be summed over all theta
    if quantity == "Mdot":
        return -pyharm.shell_sum(dump, "FM")
    elif quantity == "Mdot_in":
        to_sum = np.copy(dump["FM"])
        to_sum[to_sum > 0] = 0
        return -pyharm.shell_sum(dump, to_sum)
    elif quantity == "Mdot_out":
        to_sum = np.copy(dump["FM"])
        to_sum[to_sum < 0] = 0
        return -pyharm.shell_sum(dump, to_sum)
    elif quantity == "Edot":
        return -pyharm.shell_sum(dump, "FE")
    elif quantity == "Edot_Fl":
        return -pyharm.shell_sum(dump, "FE_Fl")
    elif quantity == "Edot_EM":
        return -pyharm.shell_sum(dump, "FE_EM")
    elif quantity == "pdot":
        return pyharm.shell_sum(dump, "Fp")
    elif quantity == "Phib":
        return 0.5 * pyharm.shell_sum(dump, "abs_B1") * np.sqrt(4.0 * np.pi)
    elif quantity == "Etot":
        return pyharm.shell_sum(dump, "JE0")
    elif quantity == "Ldot":
        return pyharm.shell_sum(dump, "FL")

    ## quantities to be averaged over all theta except near the poles
    if quantity == "T":
        to_average = dump["Theta"]  # dump['u'] / dump['rho'] * (dump['gam']-1)
    else:
        to_average = dump[quantity]

    ## TODO: quantities to be only averaged over phi

    # Weighting for the average.
    volumetric_weight = dump["gdet"]
    if density_weight and quantity != "rho":
        density = dump["rho"]
    else:
        density = dump["1"]

    if dump["n3"] > 1:  # 3d
        if pole_pad > 1:
            print("using pole_pad ", pole_pad)
        return np.sum(
            (to_average * volumetric_weight * density)[imin:, pole_pad:-pole_pad, :], axis=(1, 2)
        ) / np.sum((volumetric_weight * density)[imin:, pole_pad:-pole_pad, :], axis=(1, 2))
    else:
        return np.sum(to_average[imin:, :] * volumetric_weight * density, axis=1) / np.sum(
            volumetric_weight * density, axis=1
        )


def computeProfileSet(
    dump,
    quantities=["Mdot", "rho", "u", "T", "u^r", "u^phi"],
    imin=0,
    density_weight=True,
    pole_pad=1,
):
    """
    Open one dump, then compute various profiles from it.  Return a list of profiles.
    """

    output = []
    for quantity in quantities:
        #print(f"   {quantity}")
        try:
            output.append(
                shellAverage(
                    dump, quantity, imin=imin, density_weight=density_weight, pole_pad=pole_pad
                )
            )
        except:
            continue

    return output


def computeAllProfiles(
    runName,
    outPickleName,
    quantities=["Mdot", "rho", "u", "T", "u^r", "u^phi"],
    density_weight=True,
):
    """
    Loop through every file of a given run.  Compute profiles, then save a dictionary to a pickle.
    """

    print("calculating " + runName)

    allFiles = glob.glob(os.path.join(runName, "*ipole*.h5"))
    if len(allFiles) < 1:
        print("WARNING: phdf files don't exist, trying out rhdf files.")
        allFiles = glob.glob(os.path.join(runName, "*.rhdf"))
    
    runIndices = np.array([int(fname.split("/")[-1].replace(".h5","").replace("ipole","")) for fname in allFiles])
    order = np.argsort(runIndices)
    allFiles = np.array(allFiles)[order]
    allFiles_calc = np.copy(allFiles)

    # zone-independent information from h5py
    f = h5py.File(allFiles[0], "r")
    dump = pyharm.load_dump(allFiles[0])
    f.close()

    # initialization of lists
    listOfProfiles = []
    listOfTimes = []
    #listOfCycles = []

    # if file exists, don't do the whole calculation but continue from the last computed dump
    if os.path.isfile(outPickleName):
        # here it is assumed that no phdf files are deleted
        with open(outPickleName, "rb") as openFile:
            D_read = pickle.load(openFile)

        # initialize the list with previously calculated data
        listOfProfiles = D_read["profiles"]
        listOfTimes = D_read["times"]
        #listOfCycles = D_read["cycles"]

        # make a shorter list of dumps to be calculated
        num_saved = len(listOfTimes)
        allFiles_calc = allFiles_calc[num_saved:]

        # check the assumption
        dump = pyharm.load_dump(allFiles[num_saved - 1])
        #if listOfCycles[-1] != dump["n_step"]:
        #    print(
        #        "WARNING! There has been a change of list of output dumps! Please check the list of dumps again."
        #    )
        #    return
        print("Calculation exists and starting from dump # {}".format(num_saved))

    for file in allFiles_calc:
        f = h5py.File(file, "r")
        dump = pyharm.load_dump(file)

        listOfProfiles.append(
            computeProfileSet(dump, quantities=quantities, density_weight=density_weight)
        )
        print(dump["t"])
        listOfTimes.append(dump["t"])
        #listOfCycles.append(dump["n_step"])

        f.close()

    # save
    D = {}
    D["runName"] = runName
    D["quantities"] = quantities
    D["radii"] = dump["r1d"]
    D["gam"] = dump["gam"]
    D["spin"] = dump["a"]
    D["r_eh"] = dump["r_eh"]
    #D["dump"] = dump  # it will have all access to dump's info
    ## time-dependent quantities
    D["profiles"] = listOfProfiles
    D["times"] = listOfTimes
    #D["cycles"] = listOfCycles

    save_path = "/".join(outPickleName.split("/")[:-1])
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(outPickleName, "wb") as openFile:
        pickle.dump(D, openFile, protocol=2)
    print(f"Output saved to {outPickleName}.")


if __name__ == "__main__":
    # Input and output locations.
    grmhdLocation = "../data"
    dataLocation = "../data_products"

    # For example...
    # python computeProfiles.py bondi_multizone_121322_gizmo_3d_ext_g
    import sys

    run = sys.argv[1]

    inName = os.path.join(grmhdLocation, run)
    outName = os.path.join(dataLocation, run + "_profiles_all.pkl")
    quantityList = [
        "Ldot",
        "Edot",
        "Edot_Fl",
        "Edot_EM",
        "Mdot",
        "Mdot_in",
        "Mdot_out",
        "rho",
        "u",
        "T",
        "abs_u^r",
        "u^phi",
        "u^th",
        "u^r",
        "abs_u^th",
        "abs_u^phi",
        "b",
        "inv_beta",
        "beta",
        "Omega",
        "abs_Omega",
        "K",
        "Phib",
    ]  #'Etot', 'u^t',
    #import time
    #start_time = time.time()
    computeAllProfiles(inName, outName, quantities=quantityList)
    #end_time = time.time()
    #print(end_time-start_time)
