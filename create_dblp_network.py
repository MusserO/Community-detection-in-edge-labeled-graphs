from create_enron_network import tokenize_text, get_labels

if __name__ == "__main__":
    from edgelabelgraph import EdgeLabelGraph
    import os, json
    from collections import Counter

    data_dir = "../dblp/"

    G = EdgeLabelGraph()

    edges_to_add = []
    papers_with_label = Counter()
    author_edges = Counter()
    n_papers = 0
    for conference_file in os.listdir(data_dir):
        with open(os.path.join(data_dir, conference_file), encoding="utf8", errors='ignore') as f:
            conference_data = json.load(f)
        for paper in conference_data:
            authors = sorted([author["name"] for author in paper["authors"]])
            title  = paper["title"]
            labels = get_labels(title)

            if len(authors) <= 1: # Ignore papers with only one author
                continue
            n_papers += 1

            for label in labels:
                papers_with_label[label] += 1

            for i_author in range(len(authors)-1):
                for j_author in range(i_author+1, len(authors)):
                    edges_to_add.append(((authors[i_author],authors[j_author]), labels.copy()))
                    author_edges[(authors[i_author],authors[j_author])] += 1
        print(conference_file, n_papers)

    min_papers_with_label = int(0.005*n_papers)
    min_shared_papers_for_edge = 2

    for edge, labels in edges_to_add:
        for label in tuple(labels):
            if papers_with_label[label] < min_papers_with_label:
                labels.remove(label)
        if len(labels) > 0 and author_edges[edge] >= min_shared_papers_for_edge:
            G.add_edge_with_labels(edge, labels)

    import pickle
    with open(f"dblp_graph_title_min_{min_papers_with_label}_shared_{min_shared_papers_for_edge}.pkl", "wb") as file:
        pickle.dump(G, file)
