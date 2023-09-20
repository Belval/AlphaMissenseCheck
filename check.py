import os
import pickle
import pandas as pd
import plotly.express as px

def main():
    print("Loading AlphaMissense DB")
    if os.path.exists("missense.pkl"):
        print("Found existing parsed DB")
        with open("missense.pkl", "rb") as f:
            missense_dict = pickle.load(f)
    else:
        print("Parsing raw AlphaMissense DB")
        missense_dict = {}
        with open("AlphaMissense_hg19.tsv", "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                chromosome, position, ref, alt, _, _, _, _, am_pathogenicity, am_class = line[:-1].split("\t")
                missense_dict[(chromosome[3:], position)] = {
                    "ref": ref,
                    "alt": alt,
                    "pathogenicity": float(am_pathogenicity),
                    "class": am_class
                }
        with open("missense.pkl", "wb") as f:
            pickle.dump(missense_dict, f)

    print("Comparing with your genome")
    normal_count = 0
    mutated_count = 0
    mutation_counts = {
        1: {
            "benign": 0,
            "ambiguous": 0,
            "pathogenic": 0,
        },
        2: {
            "benign": 0,
            "ambiguous": 0,
            "pathogenic": 0,
        }
    }
    applicable_preds = []
    with open("genome.txt", "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            rsid, chromosome, position, genotype = line[:-1].split("\t")
            if (chromosome, position) in missense_dict:
                pred = missense_dict[(chromosome, position)]
                if genotype.count(pred["alt"]) > 0:
                    mutated_count += 1
                    print(rsid, pred["pathogenicity"], pred["class"])
                    mutation_counts[genotype.count(pred["alt"])][pred["class"]] += 1
                    applicable_preds.append({
                        "mutated_allele_count": genotype.count(pred["alt"]),
                        **pred
                    })
                else:
                    normal_count += 1

    print("Report:")
    print(f"\t% Mutated genes: {round(mutated_count / (mutated_count + normal_count) * 100, 2)}%")
    for mutation, count in mutation_counts[1].items():
        print(f"\t% Mutated genes with at least 1 allele classified as {mutation}: {round((count + mutation_counts[2][mutation]) / mutated_count * 100, 2)}%")
    for mutation, count in mutation_counts[2].items():
        print(f"\t% Mutated genes with 2 alleles classified as {mutation}: {round(count / mutated_count * 100, 2)}%")

    with open("preds.pkl", "wb") as f:
        pickle.dump(applicable_preds, f)

    #with open("preds.pkl", "rb") as f:
    #    applicable_preds = pickle.load(f)

    print("Generating plots")
    df = pd.DataFrame.from_dict(applicable_preds)
    fig = px.histogram(df, x="pathogenicity", color="mutated_allele_count", marginal="rug", title="Pathogenicity of your mutations")
    fig.write_image("mutation_distribution.svg")

if __name__ == "__main__":
    main()