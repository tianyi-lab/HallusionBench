import csv
import json
from tqdm import tqdm
import numpy as np
from prettytable import PrettyTable
import os
from utils import *

import openai

### to evaluate your method, implement and run generate_answer function!

root_dir = "."
llava = False
# llava = True
# load_json = False
load_json = True
input_file_name = "HallusionBench.tsv"

save_json_path_vd = "./hallusion_output_vd.json"
save_json_path_vs = "./hallusion_output_vs.json"
model_output_entry = "gpt4v_output"
model_correctness_entry = "gpt4v_output_gpt_check"
model_correctness_entry_human = "gpt4v_output_human_check"

if llava:
    save_json_path_vd = "./hallusion_output_vd_llava.json"
    save_json_path_vs = "./hallusion_output_vs_llava.json"
    model_output_entry = "llava_1_5_output"
    model_correctness_entry = "llava_1_5_output_gpt_check"
    model_correctness_entry_human = "llava_1_5_output_human_check"


col_idx = {
    'category':0,
    'subcategory':1, 
    'visual_input':2, 
    'set_id':3, 
    'figure_id':4, 
    'sample_note':5, 
    'question_id':6, 
    'question':7, 
    'gt_answer_details':8,
    'gt_answer':9, 
    'gpt4v_output':10,
    'gpt4v_output_human_check': 11,
    'llava_1_5_output':12,
    'llava_1_5_output_human_check': 13,
}



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
    with open(input_file_name) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        flag = 0
        for line in tsv_file:
            if line[0] not in ["VD", "VS"]:
                continue
            data_dict = {}
            for k, v in col_idx.items():
                data_dict[k] = line[v]

            data_dict["filename"] = get_image_file_location(root_dir, data_dict)
            if line[0] == "VD":
                data_vd.append(data_dict)
            else:
                data_vs.append(data_dict)

    ## TODO
    data_vd = generate_answer(data_vd, model_output_entry)
    data_vs = generate_answer(data_vs, model_output_entry)
    ## END

    data_vd = evaluate_by_chatgpt(data_vd, model_output_entry, model_correctness_entry, load_json=load_json, save_json_path=save_json_path_vd)
    data_vd = check_same_by_chatgpt(data_vd, model_output_entry, load_json=load_json, save_json_path=save_json_path_vd)
    data_vs = evaluate_by_chatgpt(data_vs, model_output_entry, model_correctness_entry, load_json=load_json, save_json_path=save_json_path_vs)
    data_vs = check_same_by_chatgpt(data_vs, model_output_entry, load_json=load_json, save_json_path=save_json_path_vs)
    
    data_vd = assign_correctness(data_vd, correctness_entry=model_correctness_entry_human)
    data_vs = assign_correctness(data_vs, correctness_entry=model_correctness_entry_human)
    data = data_vd + data_vs

    all_data = get_eval_all(data, model_correctness_entry_human)
    all_vd = get_eval_all(data_vd, model_correctness_entry_human)
    all_vs = get_eval_all(data_vs, model_correctness_entry_human)
    human_check_correctness = [i["correct"] for i in data]

    print("##### Human Evaluate #####")

    # question level
    table1 = [["per question", "Total"], 
              ["VD", round(100 * all_vd["correct"]/all_vd["total"], 4)], 
              ["VS", round(100 * all_vs["correct"]/all_vs["total"], 4)], 
              ["Overall", round(100 * all_data["correct"]/all_data["total"], 4)]]
    tab1 = PrettyTable(table1[0])
    tab1.add_rows(table1[1:])
    print(tab1)
    q_acc_human = round(100 * all_data["correct"]/all_data["total"], 4)


    all_data = get_eval_pair_all(data, model_correctness_entry_human)
    easy = get_eval_pair_easy(data)
    hard = get_eval_pair_hard(data)
    all_vd = get_eval_pair_all(data_vd, model_correctness_entry_human)
    easy_vd = get_eval_pair_easy(data_vd)
    hard_vd = get_eval_pair_hard(data_vd)
    all_vs = get_eval_pair_all(data_vs, model_correctness_entry_human)
    easy_vs = get_eval_pair_easy(data_vs)
    hard_vs = get_eval_pair_hard(data_vs)
    # question pair level
    table3 = [["per question pair", "Easy", "Hard", "Total"], 
              ["VD", round(100 * easy_vd["correct"]/easy_vd["total"], 4), round(100 * hard_vd["correct"]/hard_vd["total"], 4), round(100 * all_vd["correct"]/all_vd["total"], 4)], 
              ["VS", round(100 * easy_vs["correct"]/easy_vs["total"], 4), round(100 * hard_vs["correct"]/hard_vs["total"], 4), round(100 * all_vs["correct"]/all_vs["total"], 4)], 
              ["Overall", round(100 * easy["correct"]/easy["total"], 4), round(100 * hard["correct"]/hard["total"], 4), round(100 * all_data["correct"]/all_data["total"], 4)]]
    tab3 = PrettyTable(table3[0])
    tab3.add_rows(table3[1:])
    print(tab3)


    fig_all = get_eval_fig(data)
    fig_vd = get_eval_fig(data_vd)
    fig_vs = get_eval_fig(data_vs)
    fig_all_human = fig_all
    all_data_human = all_data
    # image level 
    table2 = [["per figure", "Correct", "Inconsistant", "Wrong", "Score"], 
              ["VD", round(100 * fig_vd["correct"]/fig_vd["total"], 4), round(100 * fig_vd["inconsistent"]/fig_vd["total"], 4), round(100 * fig_vd["wrong"]/fig_vd["total"], 4), round(100 * fig_vd["score"], 4)], 
              ["VS", round(100 * fig_vs["correct"]/fig_vs["total"], 4), round(100 * fig_vs["inconsistent"]/fig_vs["total"], 4), round(100 * fig_vs["wrong"]/fig_vs["total"], 4), round(100 * fig_vs["score"], 4)], 
              ["Overall", round(100 * fig_all["correct"]/fig_all["total"], 4), round(100 * fig_all["inconsistent"]/fig_all["total"], 4), round(100 * fig_all["wrong"]/fig_all["total"], 4), round(100 * fig_all["score"], 4)]]
    tab2 = PrettyTable(table2[0])
    tab2.add_rows(table2[1:])
    print(tab2)

    pair_acc_human = round(100 * all_data["correct"]/all_data["total"], 4)
    figure_acc_human = round(100 * fig_all["correct"]/fig_all["total"], 4)
    easy_acc_human = round(100 * easy["correct"]/easy["total"], 4)
    hard_acc_human = round(100 * hard["correct"]/hard["total"], 4)

    stats_human = yes_ratio_stats(data)

    # from IPython import embed;embed()
    ############################################

    print("##### GPT Evaluate #####")

    data_vd = assign_correctness(data_vd, correctness_entry=model_correctness_entry)
    data_vs = assign_correctness(data_vs, correctness_entry=model_correctness_entry)
    data = data_vd + data_vs

    all_data = get_eval_all(data, model_correctness_entry)
    all_vd = get_eval_all(data_vd, model_correctness_entry)
    all_vs = get_eval_all(data_vs, model_correctness_entry)
    gpt_check_correctness = [i["correct"] for i in data]

    # question level
    table1 = [["per question", "Total"], 
              ["VD", round(100 * all_vd["correct"]/all_vd["total"], 4)], 
              ["VS", round(100 * all_vs["correct"]/all_vs["total"], 4)], 
              ["Overall", round(100 * all_data["correct"]/all_data["total"], 4)]]
    tab1 = PrettyTable(table1[0])
    tab1.add_rows(table1[1:])
    print(tab1)

    q_acc_gpt = round(100 * all_data["correct"]/all_data["total"], 4)

    all_data = get_eval_pair_all(data, model_correctness_entry)
    easy = get_eval_pair_easy(data)
    hard = get_eval_pair_hard(data)
    all_vd = get_eval_pair_all(data_vd, model_correctness_entry)
    easy_vd = get_eval_pair_easy(data_vd)
    hard_vd = get_eval_pair_hard(data_vd)
    all_vs = get_eval_pair_all(data_vs, model_correctness_entry)
    easy_vs = get_eval_pair_easy(data_vs)
    hard_vs = get_eval_pair_hard(data_vs)
    # question pair level
    table3 = [["per question pair", "Easy", "Hard", "Total"], 
              ["VD", round(100 * easy_vd["correct"]/easy_vd["total"], 4), round(100 * hard_vd["correct"]/hard_vd["total"], 4), round(100 * all_vd["correct"]/all_vd["total"], 4)], 
              ["VS", round(100 * easy_vs["correct"]/easy_vs["total"], 4), round(100 * hard_vs["correct"]/hard_vs["total"], 4), round(100 * all_vs["correct"]/all_vs["total"], 4)], 
              ["Overall", round(100 * easy["correct"]/easy["total"], 4), round(100 * hard["correct"]/hard["total"], 4), round(100 * all_data["correct"]/all_data["total"], 4)]]
    tab3 = PrettyTable(table3[0])
    tab3.add_rows(table3[1:])
    print(tab3)


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
    print(tab2)

    pair_acc_gpt = round(100 * all_data["correct"]/all_data["total"], 4)
    figure_acc_gpt = round(100 * fig_all["correct"]/fig_all["total"], 4)
    easy_acc_gpt = round(100 * easy["correct"]/easy["total"], 4)
    hard_acc_gpt = round(100 * hard["correct"]/hard["total"], 4)

    ##############################


    print("##### Question Stats #####")
    print("Easy Questions: " + str(easy_vd["total_q"]) + "(Visual Dependent) + " + str(easy_vs["total_q"]) + "(Visual Supplement)")
    print("Hard Questions: " + str(hard_vd["total_q"]) + "(Visual Dependent) + " + str(hard_vs["total_q"]) + "(Visual Supplement)")
    print("Total Questions: " + str(all_data["total_q"]))


    print("##### Figure Stats #####")
    print("Visual Dependent Figures: " + str(fig_vd["total"]))
    print("Visual Supplement Figures: " + str(fig_vs["total"]))
    print("Total Figures: " + str(fig_all["total"]))

    print("##### Leaderboard Stats #####")

    table = [["", "Acc per question pair (qAcc)", "Acc per figure (fAcc)", "Acc per easy question (easy aAcc)", "Acc per hard question (hard aAcc)", "Acc per question (aAcc)"], 
              ["Human Eval", pair_acc_human, figure_acc_human, easy_acc_human, hard_acc_human, q_acc_human], 
              ["GPT Eval", pair_acc_gpt, figure_acc_gpt, easy_acc_gpt, hard_acc_gpt, q_acc_gpt]]
    leaderboard = PrettyTable(table[0])
    leaderboard.add_rows(table[1:])
    print(leaderboard)

    print(all_data["total"], all_data["wrong"], all_data["LH"], all_data["VI"], all_data["Mix"])
    print(all_data["total_q"], all_data["LH_cg"], all_data["VI_cg"], all_data["Mix_cg"])

    print(len(gpt_check_correctness))
    print(len(human_check_correctness))
    print(sum(np.array(human_check_correctness) == np.array(gpt_check_correctness)))
    print(sum(np.array(human_check_correctness) == np.array(gpt_check_correctness)) / len(gpt_check_correctness))


    yes = [int(i["gt_answer"]) for i in data]
    print(sum(yes))
    print(len(yes))
    print(sum(yes)/len(yes))

    stats_gpt = yes_ratio_stats(data)

    table = [["", "Yes/No Bias (Pct Diff)", "Yes/No Bias (FP Ratio)", "Consistency Test (correct)", "Consistency Test (inconsistent)", "Consistency Test (wrong)", "LH", "VI", "Mixed"], 
              ["Human Eval", stats_human["diff"], stats_human["fp"], round(100 * fig_all_human["correct"]/fig_all_human["total"], 4), round(100 * fig_all_human["inconsistent"]/fig_all_human["total"], 4), round(100 * fig_all_human["wrong"]/fig_all_human["total"], 4), round(100 * all_data_human["LH_cg"]/(all_data_human["LH_cg"] + all_data_human["VI_cg"] + all_data_human["Mix_cg"]), 4), round(100 * all_data_human["VI_cg"]/(all_data_human["LH_cg"] + all_data_human["VI_cg"] + all_data_human["Mix_cg"]), 4), round(100 * all_data_human["Mix_cg"]/(all_data_human["LH_cg"] + all_data_human["VI_cg"] + all_data_human["Mix_cg"]), 4)],
              ["GPT Eval", stats_gpt["diff"], stats_gpt["fp"], round(100 * fig_all["correct"]/fig_all["total"], 4), round(100 * fig_all["inconsistent"]/fig_all["total"], 4), round(100 * fig_all["wrong"]/fig_all["total"], 4), round(100 * all_data["LH_cg"]/(all_data["LH_cg"] + all_data["VI_cg"] + all_data["Mix_cg"]), 4), round(100 * all_data["VI_cg"]/(all_data["LH_cg"] + all_data["VI_cg"] + all_data["Mix_cg"]), 4), round(100 * all_data["Mix_cg"]/(all_data["LH_cg"] + all_data["VI_cg"] + all_data["Mix_cg"]), 4)]]
    test = PrettyTable(table[0])
    test.add_rows(table[1:])
    print(test)