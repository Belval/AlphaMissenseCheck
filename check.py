def main():
    missense_dict = {}
    print("Loading AlphaMissense DB")
    with open("AlphaMissense_hg19.tsv", "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            chromosome, position, ref, alt, _, _, _, _, am_pathogenicity, am_class = line[:-1].split("\t")
            missense_dict[(chromosome[3:], position)] = {
                "ref": ref,
                "alt": alt,
                "pathogenicity": am_pathogenicity,
                "class": am_class
            }
    print("Comparing with your genome")
    normal_count = 0
    mutated_count = 0
    mutation_counts = {
        "benign": 0,
        "ambiguous": 0,
        "pathogenic": 0,
    }
    with open("genome.txt", "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            rsid, chromosome, position, genotype = line[:-1].split("\t")
            if (chromosome, position) in missense_dict:
                pred = missense_dict[(chromosome, position)]
                if pred["alt"] in genotype:
                    mutated_count += 1
                    print(rsid, pred["pathogenicity"], pred["class"])
                    mutation_counts[pred["class"]] += 1
                else:
                    normal_count += 1

    print("Report")
    print(f"% Mutated genes: {round(mutated_count / (mutated_count + normal_count) * 100, 2)}%")
    for mutation, mutation_count in mutation_counts.items():
        print(f"% Mutated genes that are {mutation}: {round(mutation_count / mutated_count * 100, 2)}%")

if __name__ == "__main__":
    main()