from plot_utils import *

def plotOmegaFieldvsTh(dirtag, ax_passed=None, num_files=-1):
    matplotlib_settings()
    plt.rcParams.update({"font.size": 25})
    if ax_passed is None:
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))  # 8
    else:
        ax = ax_passed
    
    F01 = 0.
    F13 = 0.
    num_sum = 0
    fnames = sorted(glob.glob('../data/' + dirtag + '/*ipole*.h5'))
    dump = pyharm.load_dump(fnames[0], ghost_zones=False)
    rEH = dump["r_eh"]
    i_rEH = np.argmin(abs(dump["r1d"] - rEH))
    
    if num_files == -1: num_files = len(fnames)//2
    for fname in fnames[-num_files:]:
        dump = pyharm.load_dump(fname, ghost_zones=False)
        F01 += phi_average(dump, 'F_0_1') #, mass_weight=False)#[i_rEH]
        F13 += phi_average(dump, 'F_1_3') #, mass_weight=False)#[i_rEH]
        num_sum += 1
    
    omegaF = ((F01 / F13) * 2. * rEH / dump["a"])
    colors=['k', 'b', 'g', 'c']
    for i, radius in enumerate([rEH]):
        i_r = np.argmin(abs(dump["r1d"] - radius))
        ax.plot(dump["th1d"], omegaF[i_r], marker='.', color=colors[i])
    ax.axhline(0.5, color='k', ls=':')

    ax.set_ylim([0, 1])
    ax.set_xlabel(r"$\theta$")
    ylabel = variableToLabel(r"$\Omega_F/\Omega_H$")
    ax.set_ylabel(ylabel)
    plt.suptitle(dirtag)

    if ax_passed is None:
        fig.tight_layout()
        output = "../plots/plot_omega_field_vs_th.png"
        plt.savefig(output, bbox_inches="tight")
        print("saved to " + output)
        plt.close(fig)
    else:
        return ax

if __name__ == "__main__":
    dirtag = "bigtorus_a.9_l128_g13by9_beta1"
    dirtag = "bigtorus_am9_l192_g13by9_beta100"

    plotOmegaFieldvsTh(dirtag, num_files=100)
