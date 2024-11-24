import os
import json
import yaml
import time
import random
import pandas as pd
from collections import defaultdict
from yacs.config import CfgNode as CN
from tqdm import tqdm

from coat.evaluate import ActionEvaluator
from run_coat import AITZDataset
import threading

def evaluate_coat(cfg, screen_mode="tag"):
    evaluator = ActionEvaluator(cfg.DEMO_MODE, screen_mode)
    aitz = AITZDataset(cfg.DATA.SPLIT, cfg.DATA.DATA_DIR, ratio=0.1, double_sample=False)
    print(len(aitz), len(aitz.episode_data))
    save_dir = os.path.join(cfg.OUTPUT_DIR, cfg.MODEL.NAME)
    pbar = tqdm(aitz.data)
    episode_results = []
    for idx, step_data in enumerate(pbar):
        subset, episode_id = step_data['subset'], step_data['episode_id']
        prev_step_id, step_id = step_data['prev_step_id'], step_data['step_id']

        save_dir_ep = os.path.join(save_dir, f"{subset}-{episode_id}")
        
        cur_save_path = os.path.join(save_dir_ep, f"{subset}-{episode_id}_{step_id}.json")
        pred = json.load(open(cur_save_path, "r"))
        episode_results.append(evaluator(step_data, pred))
    with open(os.path.join(save_dir, "result.json"), "w") as f:
        json.dump(episode_results, f, indent=4, ensure_ascii=False)




# ==========================================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CoAT Demo")
    parser.add_argument("--config-file", default="/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main/coat/config.yaml", metavar="FILE",  help="path to config file",)
    parser.add_argument("--task", default="eval", type=str, choices=['try', 'flow', 'predict', 'eval'])
    parser.add_argument("--num-threads", default=1, type=int, help="number of threads")
    parser.add_argument("--seed", default=2020, type=int, help="random seed")
    parser.add_argument("opts", help="Modify config options using the command-line",
                        default=None, nargs=argparse.REMAINDER, )
    args = parser.parse_args()
    print(args)
    random.seed(args.seed)

    cfg = CN(yaml.safe_load(open(args.config_file)))    
    cfg.merge_from_list(args.opts)

    if args.task == "try": 
        try_model(cfg)
    if args.task in ['flow', 'predict']: 
        collect(cfg, num_threads=args.num_threads, task=args.task)
    