import json
import os
import argparse
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import pdist, squareform
from openai_emb import embedding_retriever
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tqdm import tqdm
import concurrent

num_workers = 16

# File path for storing embeddings
embedding_file_path = '/data/pj20/grescore/triple_embeddings.json'

def load_embeddings():
    """Load embeddings from the JSON file."""
    if os.path.exists(embedding_file_path):
        with open(embedding_file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_embeddings(embeddings):
    """Save embeddings to the JSON file."""
    with open(embedding_file_path, 'w') as file:
        json.dump(embeddings, file)

def get_triple_embedding(triple, embeddings):
    """Get the embedding for a triple, using the API if not already in the file."""
    triple_str = ' '.join(triple)
    if triple_str not in embeddings:
        embeddings[triple_str] = embedding_retriever(triple_str)
    return embeddings[triple_str]

# def calculate_uniqueness(vectors):
#     """Calculate the Uniqueness Score using vectorized operations."""
#     similarity_matrix = cosine_similarity(vectors)
#     # Subtract the similarity matrix from an identity matrix to get dissimilarity
#     dissimilarity_matrix = 1 - similarity_matrix
#     # Zero out the diagonal since we don't consider self-similarity
#     np.fill_diagonal(dissimilarity_matrix, 0)
#     # Sum only the upper triangle since the matrix is symmetric
#     score = np.sum(np.triu(dissimilarity_matrix, k=1))
#     total_pairs = len(vectors) * (len(vectors) - 1) / 2
#     return score / total_pairs if total_pairs > 0 else 0

# from scipy.spatial.distance import pdist, squareform

# def calculate_uniqueness(vectors):
#     """Calculate the Uniqueness Score using Euclidean distance."""
#     distance_matrix = squareform(pdist(vectors, 'euclidean'))
#     # Convert distances to a similarity measure (larger distances = more unique)
#     similarity_matrix = 1 / (1 + distance_matrix)
#     np.fill_diagonal(similarity_matrix, 0)  # Ignore self-similarity
#     score = np.sum(np.triu(similarity_matrix, k=1))
#     total_pairs = len(vectors) * (len(vectors) - 1) / 2
#     return score / total_pairs if total_pairs > 0 else 0


def calculate_uniqueness(vectors):
    """Calculate the Uniqueness Score using adjusted cosine similarity."""
    similarity_matrix = cosine_similarity(vectors)
    np.fill_diagonal(similarity_matrix, 0)  # Ignore self-similarity
    
    # Apply non-linear scaling
    adjusted_similarity = np.square(similarity_matrix)

    score = np.sum(np.triu(adjusted_similarity, k=1))
    total_pairs = len(vectors) * (len(vectors) - 1) / 2
    return score / total_pairs if total_pairs > 0 else 0


def calculate_uniqueness_for_text(triples, embeddings):
    """Calculate the uniqueness score for a batch of texts."""
    vectors = [get_triple_embedding(triple, embeddings) for triple in triples]
    return calculate_uniqueness(np.array(vectors))


def calculate_uniqueness_score(data_to_evaluate):
    """Calculate the Uniqueness Score for a dataset using multi-threading."""
    scores = []
    num_threads = 16
    embeddings = load_embeddings()  # Load existing embeddings

    def process_triples(triples):
        if len(triples) == 0:
            return 0
        return calculate_uniqueness_for_text(triples, embeddings)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        tasks = [executor.submit(process_triples, triples) for _, triples in data_to_evaluate.items()]
        for future in tqdm(concurrent.futures.as_completed(tasks), total=len(tasks)):
            scores.append(future.result())

    # Save all embeddings after processing
    save_embeddings(embeddings)

    avg_score = np.mean(scores)
    return avg_score


def construct_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', type=str, default='false')
    parser.add_argument('--model_name', type=str, default='mistral')
    parser.add_argument('--dataset', type=str, default='nyt10m')
    parser.add_argument('--exp_id', type=str, default='1')
    
    args = parser.parse_args()
    return args


def main():
    args = construct_args()
    
    if args.all == 'true':
        all_scores = defaultdict(dict)
        
        model_names = [
            'vicuna-1.5-7b',
            'vicuna-1.3-33b', 
            'llama-2-7b',
            'llama-2-70b',
            'wizardlm-70b'
            'text-davinci-003',
            'gpt-3.5-turbo-instruct',
            'gpt-3.5-turbo-1106',
            'gpt-4',
            'mistral',
            'galactica-30b',
            'openchat'
            ]
        
        dataset_names = [
            'cdr_rand_200',
            'docred_rand_200',
            'nyt10m_rand_500',
            'wiki20m_rand_500',
            'tacred_rand_800',
            'wiki80_rand_800',
        ]
        with open(f'./results/US.json', 'r') as f:
            all_scores = json.load(f)
            
        for model_name in model_names:
            for dataset_name in dataset_names:
                if model_name in all_scores[dataset_name]:
                    continue
                try:
                    file_to_evaluate = f'../processed_results/{dataset_name}_{model_name}_{args.exp_id}.json'
                    with open(file_to_evaluate, 'r') as f:
                        data_to_evaluate = json.load(f)
                    
                    print(f"Calculating US score for model {model_name} on dataset {dataset_name}...")
                    us_score = calculate_uniqueness_score(data_to_evaluate)
                    print(f"US score for model {model_name} on dataset {dataset_name}: {us_score}")
                    
                    all_scores[dataset_name][model_name] = us_score
                except Exception as e:
                    print(f"Error calculating US score for model {model_name} on dataset {dataset_name}: {e}")
                    continue
                
        with open(f'./results/US.json', 'w') as f:
            json.dump(all_scores, f, indent=6)
            
    else:
        file_to_evaluate = f'../processed_results/{args.dataset}_{args.model_name}_{args.exp_id}.json'
        with open(file_to_evaluate, 'r') as f:
            data_to_evaluate = json.load(f)
        
        print(f"Calculating US score for model {args.model_name} on dataset {args.dataset}...")
        us_score = calculate_uniqueness_score(data_to_evaluate)
        print(f"US score for model {args.model_name} on dataset {args.dataset}: {us_score}")
    
if __name__ == '__main__':
    main()
