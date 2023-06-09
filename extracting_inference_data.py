import os, time, sys, json, os, argparse, torch
import config, utils, spsa, ee_nn, temperature_scaling
from early_exit_dnn import Early_Exit_DNN
import numpy as np
import pandas as pd



def main(args):

	n_classes = 257

	DIR_NAME = os.path.dirname(__file__)

	device = torch.device('cuda' if (torch.cuda.is_available() and args.cuda) else 'cpu')

	model_path = os.path.join("models", "ee_mobilenet_1_branches_id_1.pth")	

	dataset_path = os.path.join(DIR_NAME, "caltech256")

	no_calib_temperature = np.ones(args.n_branches)

	result_path = os.path.join(DIR_NAME, "inference_data")
	if (not os.path.exists(result_path)):
		os.makedirs(result_path)

	inf_data_path = os.path.join(result_path, "inference_data_mobilenet_1_branches_1.csv")

	model_dict = torch.load(model_path, map_location=device)

	val_idx, test_idx = model_dict["val"], model_dict["test"]

	indices = test_idx if (args.test_indices) else val_idx

	#Load Early-exit DNN model.	
	ee_model = ee_nn.Early_Exit_DNN(args.model_name, n_classes, args.pretrained, args.n_branches, args.dim, device, args.exit_type, args.distribution)
	ee_model.load_state_dict(model_dict["model_state_dict"])
	ee_model = 	ee_model.to(device)
	ee_model.eval()

	#Load Dataset 
	test_loader = utils.load_caltech256_test_inference(args, dataset_path, indices)

	df = utils.extracting_ee_inference_data(test_loader, ee_model, no_calib_temperature, args.n_branches, device, mode="no_calib")

	df.to_csv(inf_data_path, mode='a', header=not os.path.exists(inf_data_path))



if (__name__ == "__main__"):
	# Input Arguments to configure the early-exit model .
	parser = argparse.ArgumentParser(description="Learning the Temperature driven for offloading.")

	#We here insert the argument dataset_name. 
	#The initial idea is this novel calibration method evaluates three dataset for image classification: cifar10, cifar100 and
	#caltech256. First, we implement caltech256 dataset.
	parser.add_argument('--dataset_name', type=str, default=config.dataset_name, 
		choices=["caltech256"], help='Dataset name (default: Caltech-256)')

	#We here insert the argument model_name. 
	#We evalue our novel calibration method Offloading-driven Temperature Scaling in four early-exit DNN:
	#MobileNet, ResNet18, ResNet152, VGG16
	parser.add_argument('--model_name', type=str, choices=["mobilenet", "resnet18", "resnet152", "vgg16"], default="mobilenet",
		help='DNN model name (default: mobilenet)')

	#This argument defines the ratio to split the Traning Set, Val Set, and Test Set.
	parser.add_argument('--split_ratio', type=float, default=config.split_ratio, help='Split Ratio')

	# This argument defines the seed for random operations.
	parser.add_argument('--seed', type=int, default=config.seed, 
		help='Seed. Default: %s'%(config.seed))

	# This argument defines the backbone DNN is pretrained.
	parser.add_argument('--pretrained', type=bool, default=config.pretrained, 
		help='Is backbone DNN pretrained? Default: %s'%(config.pretrained))

	# This argument defines Offloading-drive TS uses GPU board.
	parser.add_argument('--cuda', type=bool, default=config.cuda, 
		help='Cuda? Default: %s'%(config.cuda))

	parser.add_argument('--exit_type', type=str, default=config.exit_type, 
		help='Exit Type. Default: %s'%(config.exit_type))

	parser.add_argument('--distribution', type=str, default=config.distribution, 
		help='Distribution. Default: %s'%(config.distribution))

	parser.add_argument('--n_branches', type=int, default=1, 
		help='Number of side branches. Default: %s'%(config.n_branches))

	parser.add_argument('--test_indices', type=bool, default=True, 
		help='Use Test indices Default: True')

	parser.add_argument('--input_dim', type=int, default=330, help='Input Dim. Default: %s'%config.input_dim)

	parser.add_argument('--dim', type=int, default=300, help='Dim. Default: %s')


	args = parser.parse_args()

	main(args)






