
#传入测试集的路径
export DATASET_PATH="/home/test/test03/minicpm-a/model_evaluation/aitw/filter_with_picture"

#传入预测的json文件
export INPUT_PATH="/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main_kun/test.json" 

#大致结果会输出在控制台上，详细结果可以在此文件夹中查看
export OUTPUT_PATH="/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main_kun/api/"

#模型名称
export MODEL="minicpm"

#这一步是把pred转成aitz的评估形式
python coat/aitw2aitz.py

#这一步是执行评估
python run_coat.py --task "eval" --num-threads 1
