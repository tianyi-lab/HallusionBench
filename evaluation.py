import csv
import json
from tqdm import tqdm
import numpy as np
from prettytable import PrettyTable
import os
import time
from utils import *

import openai


### to evaluate your method, implement and run generate_answer function!

root_dir = "."
input_file_name = "HallusionBench_result.json"
save_json_path_vd = "./hallusion_output_vd_model.json"
save_json_path_vs = "./hallusion_output_vs_model.json"
# load_json = False
load_json = True
model_output_entry = "model_prediction"
model_correctness_entry = "gpt4v_output_gpt_check"


def generate_answer(data, model_output_entry):

    ## TODO
    ## implement this section with yout model!
    ## your_function(img_filename, question) -> "0" (No), "1" (Yes), "2" (Uncertain)
    # for r in data:
        # r[model_output_entry] = your_function(r["filename"], r["question"])

    return data


if __name__ == "__main__":

    data_vd = []
    data_vs = []
    with open(input_file_name) as json_file:
        datas = json.load(json_file)

    for data in tqdm(datas):
        if data['category'] == 'VD':
            data_vd.append(data)
        if data['category'] == 'VS':
            data_vs.append(data)
                      
    data_vd = evaluate_by_chatgpt(data_vd, model_output_entry, model_correctness_entry, load_json=load_json, save_json_path=save_json_path_vd)
    #time.sleep(60) #
    try:
        data_vs = evaluate_by_chatgpt(data_vs, model_output_entry, model_correctness_entry, load_json=load_json, save_json_path=save_json_path_vs)
        data_vs = check_same_by_chatgpt(data_vs, model_output_entry, load_json=load_json, save_json_path=save_json_path_vs)
    except:
        time.sleep(60)
        data_vs = evaluate_by_chatgpt(data_vs, model_output_entry, model_correctness_entry, load_json=load_json, save_json_path=save_json_path_vs)
        data_vs = check_same_by_chatgpt(data_vs, model_output_entry, load_json=load_json, save_json_path=save_json_path_vs)
        
    print("##### GPT Evaluate #####")

    data_vd = assign_correctness(data_vd, correctness_entry=model_correctness_entry)
    data_vs = assign_correctness(data_vs, correctness_entry=model_correctness_entry)
    data = data_vd + data_vs

    all_data = get_eval_all(data)
    all_vd = get_eval_all(data_vd)
    all_vs = get_eval_all(data_vs)

    table1 = [["per question", "Total"], 
              ["VD", round(100 * all_vd["correct"]/all_vd["total"], 4)], 
              ["VS", round(100 * all_vs["correct"]/all_vs["total"], 4)], 
              ["Overall", round(100 * all_data["correct"]/all_data["total"], 4)]]
    tab1 = PrettyTable(table1[0])
    tab1.add_rows(table1[1:])


    q_acc_gpt = round(100 * all_data["correct"]/all_data["total"], 4)

    all_data = get_eval_pair_all(data)
    easy = get_eval_pair_easy(data)
    hard = get_eval_pair_hard(data)
    all_vd = get_eval_pair_all(data_vd)
    easy_vd = get_eval_pair_easy(data_vd)
    hard_vd = get_eval_pair_hard(data_vd)
    all_vs = get_eval_pair_all(data_vs)
    easy_vs = get_eval_pair_easy(data_vs)
    hard_vs = get_eval_pair_hard(data_vs)
    # question pair level
    table3 = [["per question pair", "Easy", "Hard", "Total"], 
              ["VD", round(100 * easy_vd["correct"]/easy_vd["total"], 4), round(100 * hard_vd["correct"]/hard_vd["total"], 4), round(100 * all_vd["correct"]/all_vd["total"], 4)], 
              ["VS", round(100 * easy_vs["correct"]/easy_vs["total"], 4), round(100 * hard_vs["correct"]/hard_vs["total"], 4), round(100 * all_vs["correct"]/all_vs["total"], 4)], 
              ["Overall", round(100 * easy["correct"]/easy["total"], 4), round(100 * hard["correct"]/hard["total"], 4), round(100 * all_data["correct"]/all_data["total"], 4)]]
    tab3 = PrettyTable(table3[0])
    tab3.add_rows(table3[1:])
    #print(tab3)


    fig_all = get_eval_fig(data)
    fig_vd = get_eval_fig(data_vd)
    fig_vs = get_eval_fig(data_vs)

    # image level 
    table2 = [["per figure", "Correct", "Wrong", "Score"], 
              ["VD", round(100 * fig_vd["correct"]/fig_vd["total"], 4), round(100 * fig_vd["inconsistent"]/fig_vd["total"], 4) + round(100 * fig_vd["wrong"]/fig_vd["total"], 4), round(fig_vd["score"], 4)], 
              ["VS", round(100 * fig_vs["correct"]/fig_vs["total"], 4), round(100 * fig_vs["inconsistent"]/fig_vs["total"], 4) + round(100 * fig_vs["wrong"]/fig_vs["total"], 4), round(fig_vs["score"], 4)], 
              ["Overall", round(100 * fig_all["correct"]/fig_all["total"], 4), round(100 * fig_all["inconsistent"]/fig_all["total"], 4) + round(100 * fig_all["wrong"]/fig_all["total"], 4), round(fig_all["score"], 4)]]
    tab2 = PrettyTable(table2[0])
    tab2.add_rows(table2[1:])

    pair_acc_gpt = round(100 * all_data["correct"]/all_data["total"], 4)
    figure_acc_gpt = round(100 * fig_all["correct"]/fig_all["total"], 4)
    easy_acc_gpt = round(100 * easy["correct"]/easy["total"], 4)
    hard_acc_gpt = round(100 * hard["correct"]/hard["total"], 4)



    print("##### Question Stats #####")
    print("Easy Questions: " + str(easy_vd["total"]) + "(Visual Dependent) + " + str(easy_vs["total"]) + "(Visual Supplement)")
    print("Hard Questions: " + str(hard_vd["total"]) + "(Visual Dependent) + " + str(hard_vs["total"]) + "(Visual Supplement)")
    print("Total Questions: " + str(all_data["total"]))


    print("##### Figure Stats #####")
    print("Visual Dependent Figures: " + str(fig_vd["total"]))
    print("Visual Supplement Figures: " + str(fig_vs["total"]))
    print("Total Figures: " + str(fig_all["total"]))

    print("##### Leaderboard Stats #####")

    table = [["", "Acc per question pair", "Acc per figure", "Acc per easy question", "Acc per hard question", "Acc per question"], 
              ["GPT Eval", pair_acc_gpt, figure_acc_gpt, easy_acc_gpt, hard_acc_gpt, q_acc_gpt]]
    leaderboard = PrettyTable(table[0])
    leaderboard.add_rows(table[1:])
    print(leaderboard)
