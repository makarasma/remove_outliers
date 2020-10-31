import argparse
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


def remove_outliers(datafile):
    #setting file names and paths
    dir_name = os.path.dirname(os.path.realpath(datafile))
    name_split = datafile.split(".")
    log_filename = "outliers.log"
    backup_filename = ".".join(name_split[:-1]) + "-backup." + name_split[-1]
    data = pd.read_csv(datafile, delim_whitespace=True)
    result_folder = os.path.join(dir_name, "outliers")
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    logfile = open(os.path.join(result_folder, log_filename), 'w')
    #looking for outliers
    logfile.write(f"Removing outliers from the file: {os.path.realpath(datafile)}\n\n")
    print("Removing outliers...")
    df_new = data.copy(deep=True)
    ids = df_new.columns[0]
    columns = df_new.columns[1:]
    for col in columns:
        phen_name = col
        logfile.write(f"Phenotype: {phen_name}\n")
        df_phen = pd.DataFrame()
        df_phen["ids"] = data[ids]
        df_phen["phen"] = data[col]
        df_phen = df_phen.dropna()
        true_phens = df_phen["phen"].values
        before_count = len(df_phen['phen'].values)
        #normalizing
        try:
            df_phen["norm"] = (df_phen["phen"] - df_phen["phen"].mean()) / df_phen["phen"].std()
        except TypeError:
            logfile.write("Cannot convert values to float. Skipping.\n")
            continue
        points = df_phen["norm"].values.reshape(-1, 1)
        #clustering and outlier filtering
        try:
            db = DBSCAN(eps=1, min_samples=3).fit(points)
        except ValueError:
            logfile.write("Failed to normalize values. Skipping.\n")
            continue
        labels = list(db.labels_)
        df_phen["label"] = labels
        selected_labels = [label for label in set(labels) if labels.count(label)/len(labels) > 0.1]
        std = df_phen.loc[df_phen["label"] == selected_labels[0]].std()[1]
        df_phen = df_phen.loc[df_phen["label"].isin(selected_labels)]
        unique_vals = len(pd.unique(df_phen["phen"]))
        if unique_vals < 10 or std == 0:
            logfile.write("Categorical phenotype. Skipping\n")
            continue
        after_count = len(df_phen['phen'])
        logfile.write(f"Before removal:{before_count}\tRemoved:{before_count-after_count}\tAfter removal:{after_count}\n")
        selected_ids = df_phen["ids"].values
        df_new.loc[~df_new[ids].isin(selected_ids), col] = np.nan
        #creating visual with phenotype values
        palette = sns.color_palette("mako_r", len(set(labels)))
        plt.scatter(range(len(labels)), true_phens, c=labels, cmap=matplotlib.colors.ListedColormap(palette))
        plt.title(phen_name)
        plt.ylabel("Phenotype Value")
        plt.xlabel("List index")
        plot_name = phen_name+".png"
        plt.savefig(os.path.join(result_folder, plot_name),  bbox_inches='tight')
        plt.close()
    df_new.to_csv(datafile, sep="\t", index=False, na_rep='NA')
    data.to_csv(backup_filename, sep="\t", index=False, na_rep='NA')
    print(f"Original file saved as: {backup_filename}")
    print(f"New filtered file saved as: {datafile}")
    logfile.write(f"\nOriginal file saved as: {backup_filename}\n")
    logfile.write(f"New filtered file saved as: {datafile}\n")
    logfile.close()
    print("Finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="File containing phenotype values with headers")
    args = parser.parse_args()
    remove_outliers(datafile=args.file)
