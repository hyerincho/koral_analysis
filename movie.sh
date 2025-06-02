## These are the parameters to control
tag="bigtorus_a.9_l192_g13by9_beta100" #"bigtorus_a.9_l128_g13by9_beta1" #
quantity="symlog_FE_Fl_A" #"log_rho" #"log_Pb" #"symlog_u^th_over_uK" #"log_beta" #"symlog_u^phi_over_uK" #"log_K" #"blob_analyses" #"symlog_FE_norho_A" #"log_Theta" #"feedback_analyses" #"floors" #"fails" #"vecs_prim" #"electric_field" #"log_abs_divB" #"ismr_test" #"symlog_E3" #"symlog_B3_A" #"symlog_FE_Fl_norho_A" #"log_bsq" #"symlog_u^r_over_uff" #"log_sigma" #"symlog_u^r_over_uchar" #"symlog_FL_A" #_prims" #"B2" #_prims" #"log_b" #_rel" #"log_Gamma" # #"conservation" #"symlog_FE_PAKE_A" #"symlog_FM_A" #"symlog_Beb_over_uff2" #"log_u" #"symlog_u^r" #
ghostzone=false #true #
native=false #true #  
embed_label=false #true
overlay_field=false # true #
overlay_streamline=false # true #
overlay_grid=false #true #
log_r=false # true #
FIGURES=false #true # 

DATA_DIR="/n/holylfs05/LABS/bhi/Users/rnarayan/koral_lite/GRMHD_jetcoords/ipole_bigtorus/"

## Add arguments
args=()
filetype=h5 #phdf #rhdf #

if [ $ghostzone == true ]; then
  args+=( '-g' )
fi
if [ $native == true ]; then
  args+=( '--native' )
fi
if [ $log_r == true ]; then
  args+=( '--log_r' )
fi
if [ $embed_label == true ]; then
  args+=( '--embed_label' )
fi
if [ "$overlay_field" == "true" ] ; then
  args+=( '--overlay_field' )
fi
if [ "$overlay_streamline" == "true" ] ; then
  args+=( '--overlay_streamline' )
fi
if [ "$overlay_grid" == "true" ] ; then
  args+=( '--overlay_grid' )
fi
if [[ "$quantity" == *"beta"* ]]; then
    args+=( '--vmin=-1 --vmax=3 --cmap=plasma' )
fi
if [[ "$quantity" == *"symlog_u^r_over"* ]]; then
args+=( '--vmin=-50 --vmax=50' )
fi
if [[ "$quantity" == *"symlog_u^th_over"* ]]; then
args+=( '--vmin=-50 --vmax=50' )
fi
if [[ "$quantity" == *"symlog_u^phi_over"* ]]; then
args+=( '--vmin=-50 --vmax=50' )
fi
if [[ "$quantity" == *"symlog_FL_A"* ]]; then
    args+=( '--vmin=-1 --vmax=1')
fi
if [[ "$quantity" == *"symlog_FE_EM_A"* ]]; then
    args+=( '--vmin=-1e2 --vmax=1e2')
    #args+=( '--vmin=-1e-2 --vmax=1e-2')
fi
if [[ "$quantity" == *"symlog_FE_Fl_A"* ]]; then
    args+=( '--vmin=-1e2 --vmax=1e2')
fi
if [[ "$quantity" == *"symlog_FE_Fl_norho_A"* ]]; then
    args+=( '--vmin=-1 --vmax=1')
fi
if [[ "$quantity" == *"symlog_FE_norho_A"* ]]; then
    args+=( '--vmin=-1 --vmax=1')
fi
if [[ "$quantity" == *"log_rho"* ]]; then
    #args+=( '--vmin=-8 --vmax=-1')
    args+=( '--vmin=-4 --vmax=1')
fi
if [[ "$quantity" == *"log_Theta"* ]]; then
    args+=( '--vmin=-4 --vmax=2')
fi
if [[ "$quantity" == *"log_sigma"* ]]; then
    args+=( '--vmin=-6 --vmax=1' )
fi
if [[ "$quantity" == *"log_K"* ]]; then
    args+=( '--vmin=-1 --vmax=5' )
fi
if [[ "$quantity" == *"log_Pb"* ]]; then
    args+=( '--vmin=-3 --vmax=1' )
fi
if [[ "$quantity" == *"log_Pg"* ]]; then
    args+=( '--vmin=-3 --vmax=1' )
fi
if [[ "$quantity" == *"log_Ptot"* ]]; then
    args+=( '--vmin=-3 --vmax=1' )
fi

dir=""
odir="./movies/${tag}/frames_${quantity}"
  
if [ $native == true ]; then
odir="${odir}_native"
fi
if [ $log_r == true ]; then
odir="${odir}_logr"
fi

#args+=( '--vmin=1e-9 --vmax=1 ' )
echo "HYERIN: movie for $tag"
pyharm-movie $quantity ${DATA_DIR}/${tag}/${dir}/*.${filetype} --output_dir=$odir ${args[@]} --at=0 -sz=50 #--numeric_fnames
#pyharm-movie $quantity ${DATA_DIR}/${tag}/${dir}/bondi.out0.01*.${filetype} --output_dir=$odir ${args[@]} --at=0 #--numeric_fnames
#pyharm-movie $quantity ${DATA_DIR}/${tag}/${dir}/*0.02*.${filetype} --output_dir=$odir ${args[@]} --at=0 --numeric_fnames
