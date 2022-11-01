import pickle
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
from mps_to_tags import mps_to_tags


def classification_tags(tags):
    if tags == "large":
        return "large"
    tags_arr = np.array([list(tags.values())])
    with open("PCA_model.pkl", 'rb') as f:
        pca_mod = pickle.load(f)
    with open("kmeans_model.pkl", 'rb') as f:
        kmeans_mod = pickle.load(f)
    tags_arr = pca_mod.transform(tags_arr)
    cluster = kmeans_mod.predict(tags_arr)
    return cluster


def classification(path, count_large: bool = False):
    tags = mps_to_tags(path, count_large)
    cluster = classification_tags(tags)
    return cluster
