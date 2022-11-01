import pickle
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np


if __name__ == "__main__":
    log_dict = []
    large = "large"
    with open("log") as log:
        for line in log:
            temp_dict = None
            if line.split()[1] == "True":
                exec("temp_dict = " + " ".join(line.split()[3:]))
                log_dict.append([line.split()[0], temp_dict])
    log_dict = dict(log_dict)
    main_log_dict = []
    for name in log_dict.keys():
        if log_dict[name] != "large":
            main_log_dict.append([name, log_dict[name]])
    main_log_dict = dict(main_log_dict)
    X = np.array([list(main_log_dict[name].values()) for name in main_log_dict.keys()])
    PCA_model = PCA(n_components=5)
    reduced_data = PCA_model.fit_transform(X)
    kmeans = KMeans(init="k-means++", n_clusters=10, n_init=4)
    kmeans.fit(reduced_data)
    kmeans.predict(reduced_data)
    with open("PCA_model.pkl", 'wb') as f:
        pickle.dump(PCA_model, f)
    with open("kmeans_model.pkl", 'wb') as f:
        pickle.dump(kmeans, f)

