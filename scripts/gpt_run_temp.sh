#!/bin/bash

# Define the model names and datasets in arrays
model_names=("gpt-4-turbo")

datasets=("wiki20m_rand_500")

# Loop over each dataset and model and call the script with the parameters
for dataset in "${datasets[@]}"; do
  for model_name in "${model_names[@]}"; do
    python3 gre_run.py \
      --model_family gpt \
      --model_name "$model_name" \
      --dataset "$dataset" \
      --prompt bio_bag \
      --exp_id 1
  done
done
