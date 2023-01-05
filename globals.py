import argparse
from ops.utils import str2bool

parser = argparse.ArgumentParser()
#model
parser.add_argument("--mode", type=str, default='group',help='[group, sc]')
parser.add_argument("--stride", type=int, dest="stride", help="stride size", default=1)
parser.add_argument("--num_filters", type=int, dest="num_filters", help="Number of filters", default=256)
parser.add_argument("--kernel_size", type=int, dest="kernel_size", help="The size of the kernel", default=9)
parser.add_argument("--noise_level", type=int, dest="noise_level", help="Should be an int in the range [0,255]", default=25)
parser.add_argument("--unfoldings", type=int, dest="unfoldings", help="Number of LISTA step unfolded", default=24)
parser.add_argument("--patch_size", type=int, dest="patch_size", help="Size of image blocks to process", default=56)
parser.add_argument("--rescaling_init_val", type=float, default=1.0)
parser.add_argument("--lmbda_prox", type=float, default=0.02, help='intial threshold value of lista')
parser.add_argument("--spams_init", type=str2bool, default=1, help='init dict with spams dict')
parser.add_argument("--nu_init", type=float, default=1, help='convex combination of correlation map init value')
parser.add_argument("--corr_update", type=int, default=3, help='choose update method in [2,3] without or with patch averaging')
parser.add_argument("--multi_theta", type=str2bool, default=1, help='wether to use a sequence of lambda [1] or a single vector during lista [0]')
parser.add_argument("--diag_rescale_gamma", type=str2bool, default=0,help='diag rescaling code correlation map')
parser.add_argument("--diag_rescale_patch", type=str2bool, default=1,help='diag rescaling patch correlation map')
parser.add_argument("--freq_corr_update", type=int, default=6, help='freq update correlation_map')
parser.add_argument("--mask_windows", type=int, default=1,help='binarym, quadratic mask [1,2]')
parser.add_argument("--center_windows", type=str2bool, default=1, help='compute correlation with neighboors only within a block')
parser.add_argument("--multi_std", type=str2bool, default=0)

#training
parser.add_argument("--lr", type=float, dest="lr", help="ADAM Learning rate", default=6e-4)
parser.add_argument("--lr_step", type=int, dest="lr_step", help="ADAM Learning rate step for decay", default=80)
parser.add_argument("--lr_decay", type=float, dest="lr_decay", help="ADAM Learning rate decay (on step)", default=0.35)
parser.add_argument("--backtrack_decay", type=float, help='decay when backtracking',default=0.8)
parser.add_argument("--eps", type=float, dest="eps", help="ADAM epsilon parameter", default=1e-3)
parser.add_argument("--validation_every", type=int, default=10, help='validation frequency on training set (if using backtracking)')
parser.add_argument("--backtrack", type=str2bool, default=1, help='use backtrack to prevent model divergence')
parser.add_argument("--num_epochs", type=int, dest="num_epochs", help="Total number of epochs to train", default=300)
parser.add_argument("--train_batch", type=int, default=25, help='batch size during training')
parser.add_argument("--aug_scale", type=int, default=0)
parser.add_argument("--test_batch", type=int, default=10, help='batch size during eval')

#save
parser.add_argument("--model_name", type=str, dest="model_name", help="The name of the model to be saved.", default=None)
parser.add_argument("--data_path", type=str, dest="data_path", help="Path to the dir containing the training and testing datasets.", default="./datasets/")

#inference
parser.add_argument("--stride_test", type=int, default=12, help='stride of overlapping image blocks [4,8,16,24,48] kernel_//stride')
parser.add_argument("--stride_val", type=int, default=48, help='stride of overlapping image blocks for validation [4,8,16,24,48] kernel_//stride')
parser.add_argument("--test_every", type=int, default=100, help='report performance on test set every X epochs')
parser.add_argument("--pad_image", type=str2bool, default=0)
parser.add_argument("--pad_block", type=str2bool, default=1)
parser.add_argument("--pad_patch", type=str2bool, default=0)
parser.add_argument("--no_pad", type=str2bool, default=False)
parser.add_argument("--custom_pad", type=int, default=None)
parser.add_argument("--testpath", type=str, default='./datasets/testing')
parser.add_argument("--testidx", type=int, default=0)
parser.add_argument("--verbose", type=str2bool, default=0)

#var reg
parser.add_argument("--nu_var", type=float, default=0.01)
parser.add_argument("--freq_var", type=int, default=3)
parser.add_argument("--var_reg", type=str2bool, default=False)

parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")

args = parser.parse_args()