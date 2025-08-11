MODEL_NAME_OR_PATH=dmis-lab/biosyn-biobert-ncbi-disease

python demo.py \
  --model_name_or_path ${MODEL_NAME_OR_PATH} \
  --use_cuda \
  --dictionary_path ./datasets/ncbi-disease/test_dictionary.txt
