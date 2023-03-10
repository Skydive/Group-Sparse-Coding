import dataloaders
import torch
import numpy as np
from tqdm import tqdm
import argparse
import os
import time
from ops.utils_blocks import block_module
from ops.utils import  str2bool

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

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
parser.add_argument("--testpath", type=str, default='./datasets/BSD68')
parser.add_argument("--testidx", type=int, default=0)
parser.add_argument("--verbose", type=str2bool, default=0)

#var reg
parser.add_argument("--nu_var", type=float, default=0.01)
parser.add_argument("--freq_var", type=int, default=3)
parser.add_argument("--var_reg", type=str2bool, default=False)

args = parser.parse_args()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'
capability = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else os.cpu_count()

test_path = [args.testpath]
print(f'test data : {test_path}')
train_path = val_path = []

noise_std = args.noise_level / 255

loaders = dataloaders.get_dataloaders(train_path, test_path, train_path, crop_size=args.patch_size,
    batch_size=args.train_batch, downscale=args.aug_scale, concat=1,grey=True)

from model import ListaParams
from model import groupLista as Lista

params = ListaParams(kernel_size=args.kernel_size, num_filters=args.num_filters, stride=args.stride,
    unfoldings=args.unfoldings, freq=args.freq_corr_update, corr_update=args.corr_update,
    lmbda_init=args.lmbda_prox, h=args.rescaling_init_val, spams=args.spams_init,
    multi_lmbda=args.multi_theta,
    center_windows=args.center_windows, std_gamma=args.diag_rescale_gamma,
    std_y=args.diag_rescale_patch, block_size=args.patch_size, nu_init=args.nu_init,
    mask=args.mask_windows, multi_std=args.multi_std, freq_var=args.freq_var, var_reg=args.var_reg,nu_var=args.nu_var)

model = Lista(params).to(device=device)
pytorch_total_params = sum(p.numel() for p in model.parameters())
print(f'Arguments: {vars(args)}')
print('Nb tensors: ',len(list(model.named_parameters())), "; Trainable Params: ", pytorch_total_params, "; device: ", device,
      "; name : ", device_name)

model_name = args.model_name
out_dir = os.path.join(model_name)
ckpt_path = os.path.join(out_dir)
config_dict = vars(args)

if os.path.isfile(ckpt_path):
    try:
        print('\n existing ckpt detected')
        checkpoint = torch.load(ckpt_path, map_location=device)
        start_epoch = checkpoint['epoch']
        psnr_validation = checkpoint['psnr_validation']
        model.load_state_dict(checkpoint['state_dict'],strict=True)
        print(f"=> loaded checkpoint '{ckpt_path}' (epoch {start_epoch})")
    except Exception as e:
        print(e)
        print(f'ckpt loading failed @{ckpt_path}, exit ...')
        exit()

l = args.kernel_size // 2
tic = time.time()
phase = 'test'
print(f'\nstarting eval on test set with stride {args.stride_test}...')
model.eval()  # Set model to evaluate mode, we don't want to calculate gradients

num_iters = 0
psnr_tot = 0
stride_test = args.stride_test

loader = loaders['test']
batch = list(loader)[args.testidx]
batch = batch.to(device=device)

noise = torch.randn_like(batch) * noise_std
noisy_batch = batch + noise

f, axs = plt.subplots(1, 2, constrained_layout=True);
axs[0].imshow(batch[0,0], cmap='gray');
axs[0].set_title("Original Image");
axs[1].imshow(noisy_batch[0,0], cmap='gray');
axs[1].set_title("Noised Image");
axs[0].axis('off');
axs[1].axis('off');
plt.show();

# Disable pytorch gradient calculations (we're in test mode)
with torch.set_grad_enabled(False):
    params = {
        'crop_out_blocks': 0,
        'ponderate_out_blocks': 1,
        'sum_blocks': 0,
        'pad_even': 1,  # otherwise pad with 0 for las
        'centered_pad': 0,  # corner pixel have only one estimate
        'pad_block': args.pad_block,  # pad so each pixel has S**2 estimate
        'pad_patch': args.pad_patch,  # pad so each pixel from the image has at least S**2 estimate from 1 block
        'no_pad': args.no_pad,
        'custom_pad': args.custom_pad,
        'avg': 1}

    # Split input image into N separate patch, with some stride
    block = block_module(args.patch_size, stride_test, args.kernel_size, params)
    batch_noisy_blocks = block._make_blocks(noisy_batch)
    patch_loader = torch.utils.data.DataLoader(batch_noisy_blocks, batch_size=args.test_batch, drop_last=False)

    # Run each patch through the neural network to denoise it
    batch_out_blocks = torch.zeros_like(batch_noisy_blocks)
    for i, inp in enumerate(tqdm(patch_loader)):  # if it doesnt fit in memory
        id_from, id_to = i * patch_loader.batch_size, (i + 1) * patch_loader.batch_size
        batch_out_blocks[id_from:id_to] = model(inp)

    # Take a mean of our blocks, recombine them into our output image
    output = block._agregate_blocks(batch_out_blocks)
    
    f, axs = plt.subplots(1, 3, constrained_layout=True);
    axs[0].imshow(batch[0,0], cmap='gray');
    axs[0].set_title("Original Image");
    axs[1].imshow(noisy_batch[0,0], cmap='gray');
    axs[1].set_title("Noised Image");
    axs[2].imshow(output[0,0], cmap='gray');
    axs[2].set_title("Output Image");
    axs[0].axis('off');
    axs[1].axis('off');
    axs[2].axis('off');
    plt.show();