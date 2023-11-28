export CUDA_VISIBLE_DEVICES=5,6

python3 gre_run.py \
    --model_family llama \
    --model_name mistral \
    --model_cache_dir /data/pj20/.cache \
    --dataset nyt10m_rand_500 \
    --prompt general_bag \
    --exp_id 1 \