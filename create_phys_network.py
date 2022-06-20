if __name__ == "__main__":
    from create_enron_network import tokenize_text, get_labels
    from edgelabelgraph import EdgeLabelGraph
    from collections import Counter
    import os

    data_dir = "../Physics Theory Citation Network/"

    G = EdgeLabelGraph()

    id_to_authors = dict()
    author_names = dict()
    with open(os.path.join(data_dir, "AuthorNodes.csv"), encoding="utf8", errors='ignore') as f:
        for line in f.readlines():
            id, authors = line.split(",")
            authors = authors[:-1]
            if authors.endswith(" and"):
                authors = authors[:-4]
            if " & " in authors:
                authors = authors.split(" & ")
            else:
                authors = authors.split(" and ")
            for author in authors:
                author_name = author
                name_parts = []
                for part in author.split(" "):
                    for part2 in part.split("."):
                        if part2:
                             # Split two-part first names that cointain a hyphen but not surnames since surnames are never shortened
                            if not name_parts:
                                for part3 in part2.split("-"):
                                    if part3:
                                        name_parts.append(part2)
                            else:
                                name_parts.append(part2)
                surname = name_parts[-1]
                firstname_parts = name_parts[:-1]
                if not surname in author_names:
                    author_names[surname] = []
                    author_names[surname].append((firstname_parts, author))
                else:
                    match_index = 0
                    for namesake_firstname_parts, _ in author_names[surname]:
                        for i_part in range(min(len(firstname_parts), len(namesake_firstname_parts))):
                            if not namesake_firstname_parts[i_part].startswith(firstname_parts[i_part]) \
                            and not firstname_parts[i_part].startswith(namesake_firstname_parts[i_part]):
                                break
                        else:
                            break
                        match_index += 1
                    if match_index >= len(author_names[surname]):
                        author_names[surname].append((firstname_parts, author))
                    else:
                        author_name = author_names[surname][match_index][1]

                if not id in id_to_authors:
                    id_to_authors[id] = set()
                id_to_authors[id].add(author_name)

    edges_to_add = []
    papers_with_label = Counter()
    author_edges = Counter()
    n_papers = 0
    with open(os.path.join(data_dir, "ArticleNodes.csv"), encoding="utf8", errors='ignore') as f:
        for line in f.readlines():
            id, title, year, journal, abstract = line.split(",")
            if not id in id_to_authors:
                print(f"No authors for {id}")
                continue
            authors = tuple(id_to_authors[id])
            if len(authors) <= 1: # Ignore papers with only one author
                continue
            n_papers += 1
            title = title.strip()
            labels = get_labels(title)

            for label in labels:
                papers_with_label[label] += 1

            for i_author in range(len(authors)-1):
                for j_author in range(i_author+1, len(authors)):
                    edges_to_add.append(((authors[i_author],authors[j_author]), labels.copy()))
                    author_edges[(authors[i_author],authors[j_author])] += 1

    min_papers_with_label = int(0.005*n_papers)
    min_shared_papers_for_edge = 2

    for edge, labels in edges_to_add:
        for label in tuple(labels):
            if papers_with_label[label] < min_papers_with_label:
                labels.remove(label)
        if len(labels) > 0 and author_edges[edge] >= min_shared_papers_for_edge:
            G.add_edge_with_labels(edge, labels)

    import pickle
    with open(f"phys_graph_title_min_{min_papers_with_label}_shared_{min_shared_papers_for_edge}.pkl", "wb") as file:
        pickle.dump(G, file)
