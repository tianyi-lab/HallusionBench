import csv
import json
from tqdm import tqdm
import numpy as np
from prettytable import PrettyTable
import os
import time
import openai

api_key = ''


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

def check_same_by_chatgpt(data, output_entry, gpt_model="gpt-4", load_json=False, save_json_path="./hallusion_output.json"):

    orig_response = {}

    for r in data:
        if str(r["figure_id"]) == "0":
            key = "_".join([r["category"], r["subcategory"], str(r["set_id"])])
            orig_response[key] = r[output_entry]

    for sample in tqdm(data):
        if "same" not in sample.keys():
            key = "_".join([sample["category"], sample["subcategory"], str(sample["set_id"])])
            response2 = orig_response[key]
            prompt = 'Imagine you are an intelligent teacher. Thoroughly read the two responses to two different questions. Assess the consistency of the information provided within those two responses. '
            prompt += 'You do not know the specific questions, but you can asssess the consistency among the two responses by checking for logical conflicts if both responses are correct. '
            prompt += 'If response1 does not conflict with response2, please generate “same”. Otherwise, generate "different". \n\n response1:'
            prompt += sample[output_entry]
            prompt += '\nresponse2: '
            prompt += response2
            prompt += '\nOutput:'

            response = openai.ChatCompletion.create(model=gpt_model, messages=[{"role": "user", "content": prompt}], api_key=api_key)

            output_text = response['choices'][0]['message']['content']

            gpt_same = "0"

            if 'same' in output_text.lower(): 
                gpt_same = "1"

            elif 'different' in output_text.lower():
                gpt_same = "0"


            sample["same"] = gpt_same

            with open(save_json_path, 'w') as f:
                json.dump(data, f)

    return data

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

def get_eval_pair_all(data): # per question pair

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


