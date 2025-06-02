from plot_utils import *

def scatter_q1_q2(dirtag, ax_passed=None, q1='phib', q2='eta', logx=False, logy=False, use_Mdot_mean=False, factor=2., color='k', label='__nolegend__', alpha=1):
    matplotlib_settings()
    plt.rcParams.update({"font.size": 15})
    if ax_passed is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    else:
        ax = ax_passed
    pkl_name = "../data_products/" + dirtag + "_profiles_all.pkl"
    with open(pkl_name, "rb") as openFile:
        D = pickle.load(openFile)

    q1_arr = processTimeSeries(D, q1, use_Mdot_mean=use_Mdot_mean)
    q2_arr = processTimeSeries(D, q2, use_Mdot_mean=use_Mdot_mean)
    q1_arr = q1_arr[int(float(len(q1_arr)) / factor) :]
    q2_arr = q2_arr[int(float(len(q2_arr)) / factor) :]
    ax.scatter(q1_arr, q2_arr, marker=".", color=color, label=label, alpha=alpha)
    
    # plot setting
    if logx: ax.set_xscale('log')
    if logy: ax.set_yscale('log')
    if q1 == 'abs_u^th':
        ax.set_xlim([1e-3, 2e-2])
    if q1 == 'phib':
        ax.set_xlim([5, 150])
    if q2 == 'phib':
        ax.set_ylim([5, 150])
    if q2 == 'eta':
        ax.set_ylim([1e-2, 10])
    ax.set_xlabel(variableToLabel(q1))
    if ax_passed is None:
        ax.set_ylabel(variableToLabel(q2))
        fig.suptitle(dirtag)
        fig.tight_layout()
        output = "../plots/scatter_" + q1 + "_" + q2 + ".png"
        plt.savefig(output, bbox_inches="tight")
        print("saved to " + output)
        plt.close(fig)

def scatter_q1_q2_comparison(dirtags, q1='phib', q2='eta', logx=False, logy=False, use_Mdot_mean=False, factor=2.):
    matplotlib_settings()
    plt.rcParams.update({"font.size": 15})
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    colors = ['k', 
            'grey', 
            'r', 
            'pink', 
            'g', 
            'palegreen', 
            'b', 
            'c']#plt.cm.jet(np.linspace(1, 0, len(dirtags)))
    labels = [r"$a0\beta100$", 
            r"$a0\beta1$", 
            r"$a.5\beta100$", 
            r"$a.5\beta1$", 
            r"$a.9\beta100$", 
            r"$a.9\beta1$", 
            r"$a-.9\beta100$", 
            r"$a-.9\beta1$"]
    spinList = []
    for i, dirtag in enumerate(dirtags):
        scatter_q1_q2(dirtag, ax, q1, q2, logx, logy, use_Mdot_mean, factor, colors[i], labels[i], 0.3)

        if q1 == 'phib' and q2 == 'eta':
            pkl_name = "../data_products/" + dirtag + "_profiles_all.pkl"
            with open(pkl_name, "rb") as openFile:
                D = pickle.load(openFile)
            a = D["spin"]
            if a not in spinList and a > 0:
                spinList += [a]
                xlim = ax.get_xlim()
                phib_xaxis = np.linspace(xlim[0], xlim[1], 10)
                if a == 0.5: color = 'r'
                if a == 0.9: color = 'g'
                ax.plot(phib_xaxis, eta_BZ6(a, phib_xaxis, 0.03), color=color, ls=":") #, 0.03))

    ax.set_ylabel(variableToLabel(q2))
    ax.legend()
    fig.tight_layout()
    output = "../plots/scatter_" + q1 + "_" + q2 + "_comparison.png"
    plt.savefig(output, bbox_inches="tight")
    print("saved to " + output)
    plt.close(fig)


if __name__ == "__main__":
    dirtag = "bigtorus_a.9_l128_g13by9_beta1"
    dirtag = "bigtorus_a.9_l192_g13by9_beta100"
    #scatter_q1_q2(dirtag, q1='abs_u^th', q2='phib', logx=True, logy=True)
    #scatter_q1_q2(dirtag, q1='phib', q2='eta', logx=True, logy=True)
    #scatter_q1_q2(dirtag, q1='Omega10', q2='eta', logx=False, logy=True)
    dirtags = ["bigtorus_a0_l192_g13by9_beta100",
            #"bigtorus_a0_l64_g13b9_beta100",
            "bigtorus_a0_l128_g13by9_beta1",
            "bigtorus_a.5_l192_g13by9_beta100",
            #"bigtorus_a.5_l64_g13by9_beta100",
            "bigtorus_a.5_l128_g13by9_beta1",
            "bigtorus_a.9_l192_g13by9_beta100",
            #"bigtorus_a.9_l64_g13b9_beta100",
            "bigtorus_a.9_l128_g13by9_beta1",
            "bigtorus_am9_l192_g13by9_beta100",
            "bigtorus_am9_l128_g13by9_beta1",
            ]
    #dirtags = ["save_wrong_r/" + dirtag for dirtag in dirtags]
    scatter_q1_q2_comparison(dirtags, q1='phib', q2='eta', logx=True, logy=True)
    scatter_q1_q2_comparison(dirtags, q1='abs_u^th', q2='phib', logx=True, logy=True)
    scatter_q1_q2_comparison(dirtags, q1='abs_u^th', q2='eta', logx=True, logy=True)
