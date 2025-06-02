from plot_utils import *

def plotIC(ax, dictionary, quantity):
    radii = dictionary["radii"]
    profile, invert = readQuantity(dictionary, quantity)
    init_profile = profile[0]
    if invert:
        init_profile = 1.0 / init_profile
    valid_radii = radii > dictionary["r_eh"]
    ax.plot(radii[valid_radii], init_profile[valid_radii], "k:", lw=1)

def setTimeBins(dictionary, num_time_chunk=4, time_bin_factor=2, tmax=None):
    times = dictionary["times"]
    t_first = times[0]
    t_last = times[-1]

    # list initialization
    binNumList = [None for _ in range(len(times))]  # np.full(len(times), np.nan)

    if tmax is not None:
        if t_last > tmax:
            t_last = tmax
        else:
            print("The run hasn't reached {}tg. Instead using {:.3g}tg".format(tmax, t_last))

    tDivList = np.array([t_first + (t_last - t_first) / np.power(time_bin_factor, i + 1) for i in range(num_time_chunk)])
    tDivList = tDivList[::-1]  # in increasing time order
    tDivList = np.append(tDivList, t_last)

    for i, time in enumerate(times):
        bin_num = np.argwhere((time >= tDivList[:-1]) & (time < tDivList[1:]))
        if len(bin_num) > 1:
            print("ERROR: one profile sorted into more than 1 time bins")
        elif len(bin_num) < 1:
            continue
        else:
            binNumList[i] = int(bin_num[0, 0])

    return tDivList, binNumList

def timeAvgPerBin(dictionary, tDivList, binNumList, quantity):
    """
    Calculate time averages for each time bin. This only works when there is no need for combining more than one averaged quantities.
    """
    # basic parsing
    times = dictionary["times"]

    profiles, invert = readQuantity(dictionary, quantity)
    num_time_chunk = len(tDivList) - 1

    # list initialization
    sortedProfiles = [[] for _ in range(num_time_chunk)]  # (num_time_chunk) dimension
    avgedProfiles = [[] for _ in range(num_time_chunk)]  # (num_time_chunk) dimension
    deltBin = [[] for _ in range(num_time_chunk)]  # (num_time_chunk) dimension

    for i, profile in enumerate(profiles):
        bin_num = binNumList[i]
        if bin_num is not None:
            sortedProfiles[bin_num].append(profile)
    
    for b in range(num_time_chunk):
        if len(sortedProfiles[b]) == 0:
            # empty
            continue
        else:
            avgedProfiles[b] = np.mean(sortedProfiles[b], axis=0)

    return avgedProfiles, invert

def calcFinalTimeAvg(dictionary, tDivList, binNumList, quantity, flatten_rho=False):
    """
    Put together the final time averages. If needed, do extra operations.
    """
    radii = dictionary["radii"]
    num_time_chunk = len(tDivList) - 1

    # list initialization
    avgedProfiles = [[] for _ in range(num_time_chunk)]  # (num_time_chunk) dimension

    if "eta" in quantity or quantity == "u^r" or quantity == "phib":
        avgedProfiles_Mdot, _ = timeAvgPerBin(dictionary, tDivList, binNumList, "Mdot")
        i10 = np.argmin(abs(radii - 10))

    if quantity == "eta":
        avgedProfiles_Edot, invert = timeAvgPerBin(dictionary, tDivList, binNumList, "Edot")
        for b in range(num_time_chunk):
            if len(avgedProfiles_Mdot[b]) > 0:
                Mdot10 = avgedProfiles_Mdot[b][i10]  # Mdot at r = 10
            else:
                continue
            if len(avgedProfiles_Edot[b]) > 0:
                avgedProfiles[b] = (avgedProfiles_Mdot[b] - avgedProfiles_Edot[b]) / Mdot10
    elif quantity == "eta_Fl":
        avgedProfiles_EdotFl, invert = timeAvgPerBin(dictionary, tDivList, binNumList, "Edot_Fl")
        for b in range(num_time_chunk):
            if len(avgedProfiles_Mdot[b]) > 0:
                Mdot10 = avgedProfiles_Mdot[b][i10]  # Mdot at r = 10
            else:
                continue
            if len(avgedProfiles_EdotFl[b]) > 0:
                avgedProfiles[b] = (avgedProfiles_Mdot[b] - avgedProfiles_EdotFl[b]) / Mdot10
    elif quantity == "eta_EM":
        avgedProfiles_EdotEM, invert = timeAvgPerBin(dictionary, tDivList, binNumList, "Edot_EM")
        for b in range(num_time_chunk):
            if len(avgedProfiles_Mdot[b]) > 0:
                Mdot10 = avgedProfiles_Mdot[b][i10]  # Mdot at r = 10
            else:
                continue
            if len(avgedProfiles_EdotEM[b]) > 0:
                avgedProfiles[b] = -avgedProfiles_EdotEM[b] / Mdot10
    elif quantity == "etaMdot":
        avgedProfiles_Edot, invert = timeAvgPerBin(dictionary, tDivList, binNumList, "Edot")
        for b in range(num_time_chunk):
            if len(avgedProfiles_Edot[b]) > 0:
                avgedProfiles[b] = avgedProfiles_Mdot[b] - avgedProfiles_Edot[b]
    elif quantity == "u^r":
        avgedProfiles_rho, invert = timeAvgPerBin(dictionary, tDivList, binNumList, "rho")
        for b in range(num_time_chunk):
            if len(avgedProfiles_Mdot[b]) > 0:
                avgedProfiles[b] = avgedProfiles_Mdot[b] / (avgedProfiles_rho[b] * (4.0 * np.pi * radii**2))
    elif quantity == "phib":
        avgedProfiles_Phib, invert = timeAvgPerBin(dictionary, tDivList, binNumList, "Phib")
        for b in range(num_time_chunk):
            if len(avgedProfiles_Mdot[b]) > 0:
                Mdot10 = avgedProfiles_Mdot[b][i10]  # Mdot at r = 10
            else:
                continue
            if len(avgedProfiles_Phib[b]) > 0:
                avgedProfiles[b] = avgedProfiles_Phib[b] / np.sqrt(Mdot10)
    else:
        avgedProfiles, invert = timeAvgPerBin(dictionary, tDivList, binNumList, quantity)

    # any final operations
    ## normalization
    if "Omega" in quantity:
        try:
            avgedProfiles = [avgedProfiles[b] * np.power(radii, 3.0 / 2) for b in range(num_time_chunk)]  # normalize by Omega_K
        except:
            avgedProfiles = [avgedProfiles[b] * np.power(radii[: len(avgedProfiles[b])], 3.0 / 2) for b in range(num_time_chunk)]
    
    ## invert
    if invert:
        # Flip the quantity upside-down, usually for inv_beta.
        avgedProfiles = [1.0 / avgedProfiles[b] if (len(avgedProfiles[b]) > 0) else avgedProfiles[b] for b in range(num_time_chunk)]
    return radii, avgedProfiles

def plotProfileQuantity(ax, radii, profile, tDivList, colors=None, label=None, linestyle="-", legend=True):
    num_time_chunk = len(profile)
    if colors is None:
        colors = plt.cm.gnuplot(np.linspace(0.9, 0.3, num_time_chunk))
    for b in range(num_time_chunk):
        if label is None:
            label_use = "t={:.5g} - {:.5g}".format(tDivList[b], tDivList[b + 1])
        else:
            label_use = label
        if len(profile[b]) > 0:
            ax.plot(radii, profile[b], color=colors[b], lw=2, label=label_use, ls=linestyle)
    if legend:
        ax.legend()

def plotProfiles(
    pkl_name,
    quantity_list,
    plot_dir="../plots/test",
    fig_ax=None,
    color_list=None,
    label=None,
    linestyle=None,
    formatting=True,
    figsize=(8, 6),
    flip_sign=False,
    show_divisions=True,
    show_init=False,
    num_time_chunk=4,
    time_bin_factor=2,
    tmax=None,
    flatten_rho=False,
    legend_all=True,
):
    # Changes some defaults.
    matplotlib_settings()

    # If you want, provide your own figure and axis.  Good for multipanel plots.
    if fig_ax is not None:
        fig, axes = fig_ax
        ax1d = axes.reshape(-1)

    plotrc = {}
    with open(pkl_name, "rb") as openFile:
        D = pickle.load(openFile)

    tDivList, binNumList = setTimeBins(D, num_time_chunk, time_bin_factor=time_bin_factor, tmax=tmax)

    for i, quantity in enumerate(quantity_list):
        if fig_ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        else:
            ax = ax1d[i]  # here we assume that the number of axes passed = number of quantities

        radii, profiles = calcFinalTimeAvg(D, tDivList, binNumList, quantity, flatten_rho=flatten_rho)
        if i == 0:
            for b in range(len(tDivList) - 1):
                print("{}: t={:.3g}-{:.3g}".format(b, tDivList[b], tDivList[b + 1]))

        plotProfileQuantity(ax, radii, profiles, tDivList, colors=color_list, label=label, linestyle=linestyle, legend=(legend_all or (i == 0)))

        if show_init and ((quantity == "rho" and not flatten_rho) or quantity == "T" or quantity == "beta" or quantity == "u^r"):
            plotIC(ax, D, quantity)

        # Formatting
        if formatting:
            ax.set_xlabel("Radius [$r_g$]")
            ylabel = variableToLabel(quantity)
            if flatten_rho and quantity == "rho":
                ylabel = r"$\langle \rho \rangle r^{1.1}$ [arb. units]"
            ax.set_ylabel(ylabel)
            ax.set_xscale("log")
            ax.set_yscale("log")
            if "eta" in quantity and quantity != "beta" and quantity != "etaMdot":
                ax.set_ylim([1e-3, 4])
            elif quantity == "beta":
                ax.set_ylim([1e-3, 10])
            elif quantity == "phib":
                ax.set_ylim([10, 1e6])
            elif quantity == "rho":
                ax.set_ylim([1e-1, 1e2])
            #elif quantity == "Mdot":
            #    ax.set_ylim([3e-4, 5])

            try:
                rEH = D["r_eh"]
            except:
                a = 0  # for now
                rEH = 1.0 + np.sqrt(1.0 - a**2)
            xlim = (rEH, np.power(10,2.5)) #ax.get_xlim()[-1])
            ax.set_xlim(xlim)

        if fig_ax is None:
            output = plot_dir + "/profile_" + quantity + ".png"  # pdf"
            plt.savefig(output, bbox_inches="tight")
            plt.close()
            print("saved to " + output)

    if fig_ax is not None:
        return (fig, axes)

if __name__ == "__main__":
    pkl_name = "../data_products/bigtorus_a.9_l128_g13by9_beta1_profiles_all.pkl"
    #pkl_name = "../data_products/bigtorus_a.9_l192_g13by9_beta100_profiles_all.pkl"

    plot_dir = "../plots/test"  # common directory
    os.makedirs(plot_dir, exist_ok=True)

    quantityList = [
        "rho",
        "Mdot",
        "beta",
        "eta",
        "T",
        "eta_Fl",
        "eta_EM",
        "u^r",
        "abs_u^r",
        "Omega",
        "abs_Omega",
        "phib",
    ]
    print(pkl_name)
    plotProfiles(pkl_name, quantityList, plot_dir=plot_dir, num_time_chunk=6, time_bin_factor=1.2, show_init=False, flatten_rho=False) #, tmax=400)
