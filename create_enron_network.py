from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk

stop_words = set(stopwords.words('english'))
numbers = set('0123456789')

def tokenize_text(t):
    ps = PorterStemmer()
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    return [ps.stem(w) for w in tokenizer.tokenize(t) if w.lower() not in stop_words \
            and len(w) >= 3 and not w.isdigit() and not set(w).intersection(numbers)]

def get_labels(s):
    return set(tokenize_text(s))

if __name__ == "__main__":
    from edgelabelgraph import EdgeLabelGraph
    import os

    data_dir = "../maildir/"
    mail_folder = "sent"

    G = EdgeLabelGraph()

    for folder in os.listdir(data_dir):
        mail_path = os.path.join(data_dir, folder, mail_folder)
        if not os.path.exists(mail_path):
            print(f"{mail_path} not found")
            continue
        print(mail_path)
        for mail in os.listdir(mail_path):
            labels = set()
            with open(os.path.join(mail_path, mail), encoding="utf8", errors='ignore') as f:
                header_read = False
                for line in f.readlines():
                    if not header_read:
                        if line.startswith("X-From: "):
                            sender = line[len("X-From: "):-1]
                        elif line.startswith("X-To: "):
                            receivers = line[len("X-To: "):-1].split(", ")
                        elif line.startswith("Subject: "):
                            subject = line[len("Subject: "):-1]
                            labels = get_labels(subject)
                        elif line.startswith("X-FileName: "):
                            header_read = True
                    else:
                        continue
                else:
                    for receiver in receivers:
                        if sender != receiver:
                            G.add_edge_with_labels((sender,receiver), labels)

    import pickle
    with open("enron_graph_subject_only.pkl", "wb") as file:
        pickle.dump(G, file)
