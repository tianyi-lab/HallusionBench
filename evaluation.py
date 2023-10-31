import csv
import json
from tqdm import tqdm
import numpy as np
from prettytable import PrettyTable
import os
import time
import openai
api_key = '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'
#api_key = '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'

### to evaluate your method, implement and run generate_answer function!

root_dir = "."
input_file_name = "HallusionBench.tsv"
save_json_path_vd = "./hallusion_output_vd.json"
save_json_path_vs = "./hallusion_output_vs.json"
# load_json = False
load_json = True
model_output_entry = "model_prediction"
model_correctness_entry = "gpt4v_output_gpt_check"

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
    # 'llava_1_5_output':12,
    # 'llava_1_5_output_human_check': 13,
}



def generate_answer(data, model_output_entry):

    ## TODO
    ## implement this section with yout model!
    ## your_function(img_filename, question) -> "0" (No), "1" (Yes), "2" (Uncertain)
    # for r in data:
        # r[model_output_entry] = your_function(r["filename"], r["question"])

    return data


def get_image_file_location(root, row):
    if int(row['visual_input']) == 0:
        return None
    img_file = row['set_id'] + "_" + row['figure_id'] + ".png"
    return os.path.join(root, row['category'], row['subcategory'], img_file)


def evaluate_by_chatgpt(data, output_entry, correctness_entry, gpt_model="gpt-4", load_json=False, save_json_path="./hallusion_output.json"):
    if load_json and os.path.exists(save_json_path):
        with open(save_json_path, 'r') as f:
            output = json.load(f)
    else:
        output = []
    for sample in tqdm(data[len(output):]):
        prompt = 'Imagine you are an intelligent teacher. Thoroughly read the question, reference answer and the prediction answer to ensure a clear understanding of the information provided. Assess the correctness of the predictions. '
        prompt += 'If the prediction answer does not conflict with the reference answer, please generate “correct”. If the prediction answer conflict with the reference answer, please generate “incorrect”. If the prediction answer is unclear about the answer, please generate "unclear". \n\n Question:'
        prompt += sample['question']
        prompt += '\nReference answer: '
        prompt += sample['gt_answer_details']
        prompt += '\nPrediction answer:'
        prompt += sample[output_entry]
        prompt += '\nOutput:'

        response = openai.ChatCompletion.create(model=gpt_model, messages=[{"role": "user", "content": prompt}], api_key=api_key)

        output_text = response['choices'][0]['message']['content']


        if 'incorrect' in output_text.lower(): 
            gpt_correctness = "0"

        elif 'correct' in output_text.lower():
            gpt_correctness = "1"
        else:
            gpt_correctness = "2"

        sample[correctness_entry] = gpt_correctness

        output.append(sample)

        with open(save_json_path, 'w') as f:
            json.dump(output, f)

    return output


def get_eval_fig(data): # per figure

    eval_fig_dict = dict()

    for r in data:
        if r["category"] == "VS" and str(r["figure_id"]) == "0": # no figure
            continue
        name = "_".join([r["category"], r["subcategory"], str(r["set_id"]), str(r["figure_id"])])
        if name in eval_fig_dict:
            c, t = eval_fig_dict[name]
            eval_fig_dict[name] = (c + r["correct"], t+1)
        else:
            eval_fig_dict[name] = (r["correct"], 1)

    eval_fig_stat = {}
    eval_fig_stat["note"] = "all accuracy per image (consistency test)"
    eval_fig_stat["total"] = len(eval_fig_dict.keys())
    eval_fig_stat["correct"] = 0
    eval_fig_stat["wrong"] = 0
    eval_fig_stat["inconsistent"] = 0
    eval_fig_stat["score"] = 0


    for v in eval_fig_dict.values():
        if v[0] == v[1]:
            eval_fig_stat["correct"] += 1
        elif v[0] == 0:
            eval_fig_stat["wrong"] += 1
        else:
            eval_fig_stat["inconsistent"] += 1
        eval_fig_stat["score"] += (v[0] / v[1])
            
    eval_fig_stat["score"] = eval_fig_stat["score"] / eval_fig_stat["total"]
    return eval_fig_stat

def get_eval_all(data): # per question

    eval_all_dict = dict()

    for r in data:
        name = "_".join([r["category"], r["subcategory"], str(r["set_id"]), str(r["figure_id"]), str(r["question_id"])])
        assert name not in eval_all_dict 
        
        eval_all_dict[name] = r["correct"]

    eval_all_stat = {}
    eval_all_stat["note"] = "all accuracy per question"
    eval_all_stat["total"] = len(eval_all_dict.keys())
    eval_all_stat["correct"] = np.count_nonzero(list(eval_all_dict.values()))
    eval_all_stat["wrong"] = eval_all_stat["total"] - eval_all_stat["correct"]

    return eval_all_stat

def get_eval_pair_all(data):

    get_eval_pair_dict = dict()
    count = 0 

    for r in data:
        name = "_".join([r["category"], r["subcategory"], str(r["set_id"]), str(r["question_id"])])
        if name in get_eval_pair_dict:
            c, t = get_eval_pair_dict[name]
            get_eval_pair_dict[name] = (c + r["correct"], t+1)
        else:
            get_eval_pair_dict[name] = (r["correct"], 1)        
        count += 1
    eval_all_pair_stat = {}
    eval_all_pair_stat["note"] = "all accuracy per question pair"
    eval_all_pair_stat["total"] = count
    eval_all_pair_stat["correct"] = 0
    eval_all_pair_stat["wrong"] = 0

    for v in get_eval_pair_dict.values():
        if v[0] == v[1]:
            eval_all_pair_stat["correct"] += 1
        else:
            eval_all_pair_stat["wrong"] += 1
            
    return eval_all_pair_stat

def get_eval_pair_easy(data):

    get_eval_pair_dict = dict()
    count = 0 
    for r in data:
        if str(r["figure_id"]) != "0":
            continue
        name = "_".join([r["category"], r["subcategory"], str(r["set_id"]), str(r["question_id"])])
        if name in get_eval_pair_dict:
            c, t = get_eval_pair_dict[name]
            get_eval_pair_dict[name] = (c + r["correct"], t+1)
        else:
            get_eval_pair_dict[name] = (r["correct"], 1)        
        count += 1
    eval_all_pair_stat = {}
    eval_all_pair_stat["note"] = "all accuracy per question pair"
    eval_all_pair_stat["total"] = count
    eval_all_pair_stat["correct"] = 0
    eval_all_pair_stat["wrong"] = 0

    for v in get_eval_pair_dict.values():
        if v[0] == v[1]:
            eval_all_pair_stat["correct"] += 1
        else:
            eval_all_pair_stat["wrong"] += 1
            
    return eval_all_pair_stat

def get_eval_pair_hard(data):

    get_eval_pair_dict = dict()
    count = 0

    for r in data:
        if str(r["figure_id"]) == "0":
            continue
        name = "_".join([r["category"], r["subcategory"], str(r["set_id"]), str(r["question_id"])])
        if name in get_eval_pair_dict:
            c, t = get_eval_pair_dict[name]
            get_eval_pair_dict[name] = (c + r["correct"], t+1)
        else:
            get_eval_pair_dict[name] = (r["correct"], 1)       
        count += 1 
    eval_all_pair_stat = {}
    eval_all_pair_stat["note"] = "all accuracy per question pair"
    eval_all_pair_stat["total"] = count
    eval_all_pair_stat["correct"] = 0
    eval_all_pair_stat["wrong"] = 0

    for v in get_eval_pair_dict.values():
        if v[0] == v[1]:
            eval_all_pair_stat["correct"] += 1
        else:
            eval_all_pair_stat["wrong"] += 1
            
    return eval_all_pair_stat

def assign_correctness(data_arr, correctness_entry):
    for r in data_arr:
        if r["category"] == "VS" and int(r["figure_id"]) == 0: # if there is no visual supplement and the model does not know, count it as correct
            r["correct"] = 1 if int(r[correctness_entry]) == 1 or int(r[correctness_entry]) == 2 else 0
        else:
            r["correct"] = 1 if int(r[correctness_entry]) == 1 else 0
    return data_arr

if __name__ == "__main__":

    data_vd = []
    data_vs = []
    with open("HallusionBench_result_sample.json") as json_file:
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
    except:
        time.sleep(60)
        data_vs = evaluate_by_chatgpt(data_vs, model_output_entry, model_correctness_entry, load_json=load_json, save_json_path=save_json_path_vs)
        

    data_vd = assign_correctness(data_vd, correctness_entry=model_correctness_entry)
    data_vs = assign_correctness(data_vs, correctness_entry=model_correctness_entry)
    data = data_vd + data_vs

    all_data = get_eval_all(data)
    all_vd = get_eval_all(data_vd)
    all_vs = get_eval_all(data_vs)


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
