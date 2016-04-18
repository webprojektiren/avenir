#!/Users/pranab/Tools/anaconda/bin/python

# Package imports
import os
import sys
#import matplotlib.pyplot as plt
import numpy as np
import sklearn as sk
#import sklearn.linear_model
from sklearn.cluster import KMeans
#import matplotlib
import random
import jprops
from sklearn.externals import joblib
from sklearn.ensemble import BaggingClassifier
from random import randint
sys.path.append(os.path.abspath("../lib"))
from support import *

if len(sys.argv) < 2:
	print "usage: ./cluster.py <config_properties_file>"
	sys.exit()

# kmeans cluster finding
def train_kmeans():
	print "starting kmeans clustering..."
	model = KMeans(n_clusters=num_clusters, init=init_strategy, n_init=num_inits, 
	max_iter=num_iters, precompute_distances=precom_dist)
	model.fit(X)
	
	#persist model
	if persist_model:
		model_file = model_file_directory + "/" + model_file_prefix + ".mod"
		print "saving model file " +  model_file
		joblib.dump(model, model_file) 
	
	clusters = model.cluster_centers_
	print clusters
	cohesion = model.inertia_ / len(X)
	print "cohesion:  %.3f" %(cohesion) 

# finds belonging clusters
def predict():
	X = extract_data("pred.data.file", "pred.data.feature.fields")
	model_file_directory = configs["common.model.directory"]
	model_file_prefix = configs["common.model.file.prefix"]
	model_file = model_file_directory + "/" + model_file_prefix + ".mod"
	print "loading model file " +  model_file
	model = joblib.load(model_file) 	
	cluster_index = model.predict(X)
	print cluster_index

def explore():
	print "calculating hopkins stats to detect if the data set has clusters..."
	X = extract_data("train.data.file", "train.data.feature.fields")	
	XR = extract_data("expl.data.file", "expl.data.feature.fields")
	split_size = int(configs["expl.sample.size"])
	num_iters = int(configs["expl.num.iters"])
	hopkins_stats = []
	
	for i in range(0, num_iters):
		(X_spl, X_tra) = split_data_random(X, split_size)
		(X_ran, X_rem) = split_data_random(XR, split_size)
	
		min_dist_ran = find_min_distances(X_ran, X_tra)
		min_dist_spl = find_min_distances(X_spl, X_tra)
	
		print "random"
		#print min_dist_ran
		ran_sum = min_dist_ran.sum()
		print "sum %.3f" %(ran_sum)
		
		print "split"
		#print min_dist_spl
		spl_sum = min_dist_spl.sum()
		print "sum %.3f" %(spl_sum)
	
		hopkins_stat = spl_sum / (ran_sum + spl_sum)
		print "hopkins stats %.3f" %(hopkins_stat)
		hopkins_stats.append(hopkins_stat)
		
	av_hopkins_stat = np.mean(hopkins_stats)
	print "average hopkins stat %.3f" %(av_hopkins_stat)

# loads file and extracts specific columns
def extract_data(file_name_param, field_indices_param):
	X = extract_table_from_file(configs, file_name_param, field_indices_param)	
	#preprocess features
	if (preprocess == "scale"):
		X = sk.preprocessing.scale(X)
	return X
	
# main
configs = getConfigs(sys.argv[1])
mode = configs["common.mode"]

preprocess = configs["common.preprocessing"]

if mode == "train":
	#train
	print "running in training mode..."
	algo = configs["train.algo"]	
	num_clusters = int(configs["train.num.clusters"])
	num_iters = int(configs["train.num.iters"])
	if num_iters == -1:
		num_iters = 300
	num_inits = int(configs["train.num.inits"])
	if num_inits == -1:
		num_inits = 10
	init_strategy = configs["train.init.strategy"]
	if init_strategy == "default":
		init_strategy = "k-means++"
	precom_dist = configs["train.precompute.distance"].lower()
	if precom_dist == "true":
		precom_dist = True
	elif precom_dist == "false":
		precom_dist = False
	elif not precom_dist == "auto":
		print "ivalid parameter for train.precompute.distance"
		sys.exit()
	persist_model = configs["train.persist.model"].lower() == "true"

	X = extract_data("train.data.file", "train.data.feature.fields")
	model_file_directory = configs["common.model.directory"]
	model_file_prefix = configs["common.model.file.prefix"]
	
	if algo == "kmeans":
		train_kmeans()
	else:
		print "invalid cluster algorithm"
		sys.exit()

elif mode == "predict":
	print "running in prediction mode..."
	predict()
			
elif mode == "explore":
	#calculate hopkins stats
	print "running in explore mode..."
	explore()	
	
	
	
	
	
			