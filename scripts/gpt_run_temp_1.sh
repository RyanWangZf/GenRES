#!/bin/bash

# Define the model names and datasets in arrays
# model_names=("gpt-3.5-turbo-1106", "gpt-3.5-turbo-instruct" "text-davinci-003" "gpt-4")
model_names=("gpt-4-1106-preview")
datasets=("cdr_rand_200" "docred_rand_200" "nyt10m_rand_500" "wiki20m_rand_500" "tacred_rand_800" "wiki80_rand_800")

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
