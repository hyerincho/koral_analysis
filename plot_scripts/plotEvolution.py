from plot_utils import *

def plot_evolution_quantity_from_dump(dirtag, quantity, num_files, ax_passed=None, logx=False, logy=False, color='k'):
    matplotlib_settings()
    plt.rcParams.update({"font.size": 15})
    if ax_passed is None:
        _, ax = plt.subplots(1, 1, figsize=(8, 6))
    else:
        ax = ax_passed
    times = []
    q_arr = []
    
    fnames = sorted(glob.glob('../data/' + dirtag + '/*.h5'))

    dump0 = pyharm.load_dump(fnames[0])
    if quantity == "phib":
        at_r = dump0["r_eh"]
    elif quantity == "Omega":
        at_r = 10
    else:
        at_r = 5

    for fname in fnames[-num_files:]:
        dump = pyharm.load_dump(fname)
        times += [dump["t"]]
        q_arr += [extract_quantity_from_dump(dump, quantity, at_r)]

    if logx: times = np.log10(times)
    if logy: q_arr = np.log10(q_arr)
    ax.plot(times, q_arr, color=color)
    ax.set_xlabel('t')
    ax.set_ylabel(variableToLabel(quantity))

    if ax_passed is None:
        output = "../plots/plot_evolution_" + quantity + ".png"
        plt.savefig(output, bbox_inches="tight")
        print("saved to " + output)
    else:
        return ax

def plot_evolution(dirtag, quantities, ax_passed=None):
    matplotlib_settings()
    plt.rcParams.update({"font.size": 15})
    if ax_passed is None:
        _, ax = plt.subplots(1, 1, figsize=(8, 6))
    else:
        ax = ax_passed
    
    fnames = sorted(glob.glob('../data/' + dirtag + '/*.h5'))
    dump0 = pyharm.load_dump(fnames[0])
    pkl_name = "../data_products/" + dirtag + "_profiles_all.pkl"
    with open(pkl_name, "rb") as openFile:
        D = pickle.load(openFile)
    times = D["times"]
    
    colors = ['k', 'g', 'r', 'b']
    for i, quantity in enumerate(quantities):
        quantity_arr = processTimeSeries(D, quantity, use_Mdot_mean=False)
        
        label = variableToLabel(quantity)
        if quantity in ["Mdot", "eta", "phib"]:
            logy = True
            quantity_arr = np.log10(quantity_arr)
            label = r"$log_{\rm 10}($" + label + ")"

        ax.plot(times, quantity_arr, color=colors[i], label=label)

    ax.set_xlabel('t')
    ax.set_ylim([-2,4])
    #ax.set_xlim([150000, 250000])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol=4, fontsize=10)
    plt.suptitle(dirtag)

    if ax_passed is None:
        output = "../plots/plot_evolution.png"
        plt.savefig(output, bbox_inches="tight")
        print("saved to " + output)
    else:
        return ax

if __name__ == "__main__":
    dirtag = "bigtorus_a.9_l128_g13by9_beta1"
    #dirtag = "bigtorus_a.5_l192_g13by9_beta100"
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    num_files = 100
    plot_evolution(dirtag, ['Mdot', "eta", "phib", "Omega10"])
    #plot_evolution_quantity(dirtag, "Mdot", num_files, ax_passed=ax, logy=True)
    #plot_evolution_quantity(dirtag, "eta", num_files, ax_passed=ax, logy=True, color='g')
    #plot_evolution_quantity(dirtag, "phib", num_files, ax_passed=ax, logy=True, color='r')
    #plot_evolution_quantity(dirtag, "Omega", num_files, ax_passed=ax, logy=False, color='b')
    #output = "../plots/plot_evolution.png"
    #plt.savefig(output, bbox_inches="tight")
    #print("saved to " + output)
