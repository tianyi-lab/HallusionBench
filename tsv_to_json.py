import json
from tqdm import tqdm
import os

def get_image_file_location(root, row):
    if int(row['visual_input']) == 0:
        return None
    img_file = row['set_id'] + "_" + row['figure_id'] + ".png"
    return os.path.join(root, row['category'], row['subcategory'], img_file)
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
    # 'gpt4v_output':10,
    # 'gpt4v_output_human_check': 11,
    # 'llava_1_5_output':12,
    # 'llava_1_5_output_human_check': 13,
}
import csv
import json
data_vd = []
data_vs = []
root_dir = "."
input_file_name = 'HallusionBench.tsv'
with open(input_file_name) as file:
    tsv_file = csv.reader(file, delimiter="\t")
    flag = 0
    for line in tsv_file:
        # if line[0] not in ["VD", "VS"]:
        # if line[0] in ["NOTE", "category"]:
        if "VD" not in line[0] and "VS" not in line[0]:
            continue
        data_dict = {}
        try:
            for k, v in col_idx.items():
                data_dict[k] = line[v]
                assert int(line[col_idx["gt_answer"]]) == 0 or int(line[col_idx["gt_answer"]]) == 1 or int(line[col_idx["gt_answer"]]) == 2
                # assert int(line[col_idx["gpt4v_output_human_check"]]) == 0 or int(line[col_idx["gpt4v_output_human_check"]]) == 1 or int(line[col_idx["gpt4v_output_human_check"]]) == 2
                # assert int(line[col_idx["llava_1_5_output_human_check"]]) == 0 or int(line[col_idx["llava_1_5_output_human_check"]]) == 1 or int(line[col_idx["llava_1_5_output_human_check"]]) == 2
        except:
            from IPython import embed;embed()

        data_dict["filename"] = get_image_file_location(root_dir, data_dict)
        if line[0] == "VD":
            data_vd.append(data_dict)
        else:
            data_vs.append(data_dict)

result = data_vs + data_vd
print(len(result))
result1 = []

for re in result:
    result1.append({"category": re['category'], "subcategory": re['subcategory'], "visual_input": re['visual_input'], "set_id": re['set_id'], "figure_id": re['figure_id'], "sample_note": re['sample_note'], "question_id": re['question_id'], "question": re['question'], "gt_answer": re['gt_answer'], "gt_answer_details": re["gt_answer_details"], "filename": re['filename']})

print(len(result))
with open('./HallusionBench.json', 'w') as f:
    json.dump(result, f)