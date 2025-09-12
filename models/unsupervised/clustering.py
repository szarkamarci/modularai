import numpy as np
import pandas as pd

import mlflow.pyfunc 

from sklearn.cluster import KMeans, DBSCAN, HDBSCAN 
from sklearn.metrics import silhouette_score 

class Clustering_Classifier(mlflow.pyfunc.PythonModel): 

	self.model_catalog = { 'kmeans' : Kmeans, 'dbscan' : DBSCAN, 'hdbscan' : HDBSCAN } 
	self.train_function_catalog = { 'silhouette' : self.train_silhouette, 'train_inertia' : self.train_inertia } 
	
	def __init__(self, train_data : list | pd.DataFrame,
					   model_type : str, hyper_params: dict, 
					   score_type : str, score_limit : float, max_iter : int = 100, 
					   print_info = False):
					   
		self.model_type = model_type 
		self.model = None 
		self.train_data = train_data 
		self.hyper_params = hyper_params 
		self.score_type = score_type 
		self.score_limit = score_limit 
		self.final_score = None
		self.print_info = print_info 
		self.train_model() 
		
	def train_silhouette(self, Model, data):
	
		silhouette = -1
		iter = 0 
		best_score = -1 
		best_model = None 
		
		while (silhouette < self.score_limit) and (iter < max_iter): 
			model = Model(**self.hyper_params) 
			labels = model.fit_predict(data) 
			silhouette = silhouette_score(data, labels) 
			
			if best_score < silhouette: 
				best_score = silhouette
				best_model = model 
				
			if print_info: 
				print(f"silhouette = {silhouette}") 
				
			iter += 1 
		
		self.final_score = best_score
		self.model = best_model
					
	def train_inertia(self, Model, data): 
		inertia = float('inf') 
		iter = 0 best_score = -1
		best_model = None 
		
		while (inertia > self.score_limit) and (iter < max_iter): 
			model = Model(**self.hyper_params)
			labels = model.fit_predict(data)
			inertia = model.inertia_ 
			
			if best_score > inertia: 
				best_score = inertia 
				best_model = model 
			
			if print_info: 
				print(f"inertia = {inertia}") 
				
			iter += 1
			
		self.final_score = best_score
		self.model = best_model
		
	def train_model(self): 
	
		if isinstance(self.train_data, pd.DataFrame):
			data = self.train_data.values
		elif isinstance(self.train_data, list): 
			data = np.array(self.train_data) 
		else: raise ValueError("train_data is required")
		
		Model = self.model_catalog[self.model_type] 
		train_function = self.train_function_catalog[self.score_type] 
		train_function(Model, data) 
		
	def predict(self, predict_data: pd.DataFrame | list[any]): 
		# MLflow passes a pandas DataFrame # Convert to numpy for sklearn 
		
		if isinstance(predict_data, str): 
			data = json.loads(predict_data)['inputs']
		elif isinstance(predict_data, dict):
			data = predict_data['inputs']
		elif isinstance(predict_data, pd.DataFrame): 
			data = predict_data.values 
		else: 
			data = input # fallback (e.g., local testing with list of lists) 
			
		res = self.kmeans.predict(data)
		
		return res.tolist()