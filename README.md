# HallusionBench: You See What You Think? Or You Think What You See? An Image-Context Reasoning Benchmark Challenging for GPT-4V(ision), LLaVA-1.5, and Other Multi-modality Models

[Fuxiao Liu*](https://fuxiaoliu.github.io/), [Tianrui Guan*](https://tianruiguan.phd), Zongxia Li, Lichang Chen, Yaser Yacoob, Dinesh Manocha, Tianyi Zhou

🔥🔥🔥
## We welcome everyone to contribute the failure cases of Large Multimodal Models (GPT-4V) to our community!
🔥🔥🔥

Large language models (LLMs), after being aligned with vision models and integrated into vision-language models (VLMs), can bring impressive improvement in image reasoning tasks. This was shown by the recently released GPT-4V(ison), LLaVA-1.5, etc. However, the strong language prior in these SOTA LVLMs can be a double-edged sword: they may ignore the image context and solely rely on the (even contradictory) language prior for reasoning. In contrast, the vision modules in VLMs are weaker than LLMs and may result in misleading visual representations, which are then translated to confident mistakes by LLMs. To study these two types of VLM mistakes, i.e., language hallucination and visual illusion, we curated HallusionBench, an image-context reasoning benchmark that is still challenging to even GPT-4V and LLaVA-1.5. We provide a detailed analysis of examples in HallusionBench, which sheds novel insights on the illusion or hallucination of VLMs and how to improve them in the future. 

If you find our paper useful, please cite our paper:
```bibtex
@misc{liu2023hallusionbench,
      title={HallusionBench: You See What You Think? Or You Think What You See? An Image-Context Reasoning Benchmark Challenging for GPT-4V(ision), LLaVA-1.5, and Other Multi-modality Models}, 
      author={Fuxiao Liu and Tianrui Guan and Zongxia Li and Lichang Chen and Yaser Yacoob and Dinesh Manocha and Tianyi Zhou},
      year={2023},
      eprint={2310.14566},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```

## Updates
- [-/-] 🔥 Evaluation result on LLaVA-1.5 will be updated this week. More model results to come!
- [10/27] 🔥 The leaderboard and evaluation code is released! **Welcome to update your model on our leaderboard!**
- [10/24] 🔥 The early report with case analysis and insights is available [here](https://arxiv.org/abs/2310.14566).
- [10/23] 🔥 Please check our previous work on mitigating hallucinations of LMMs ["Mitigating Hallucination in Large Multi-Modal Models via Robust Instruction Tuning"](https://github.com/FuxiaoLiu/LRV-Instruction).

## Dataset Download

To keep evaluation simple, we only provide the question in form of yes/no questions.

| Updated on      | Questions and Annotations | Figures | Question Count | Figure Count |
| ----------- | :----: | :----: | :----: | :----: |
| Oct 27, 2023     | [HallusionBench.json](./HallusionBench.json) | [hallusion_bench.zip](https://drive.google.com/file/d/1sAXmVg3I3A6gjb8JnA6HWjSv1ntrSBki/view?usp=drive_link)         | 254  | 69 |

### Evaluation

1. git the repo
```
git clone https://github.com/tianyi-lab/HallusionBench.git
cd ./HallusionBench
```

2. Download the images [hallusion_bench.zip](https://drive.google.com/file/d/1sAXmVg3I3A6gjb8JnA6HWjSv1ntrSBki/view?usp=drive_link) and unzip the folder in the same directory.
   
3. The Questions and image locations are saved in `./HallusionBench.json`. The data sample are as follows:
```
{'category': 'VD', 'subcategory': 'illusion', 'visual_input': '1', 'set_id': '0', 'figure_id': '0', 'sample_note': 'circle', 'question_id': '0', 'question': 'Is the right orange circle the same size as the left orange circle?', 'gt_answer_details': 'The right orange circle is the same size as the left orange circle.', 'gt_answer': '1', 'filename': './hallusion_bench/VD/illusion/0_0.png'}
```
The key `visual_input`means whether the question needs visual input like images. If `visual_input=1`, it means the question need visual input. If `visual_input=0`, it means the question doesn't need visual input. It's the text-only question.

4. Run your model on `./HallusionBench.json` and save the ouput file as `./HallusionBench_result.json`. You need to add the output of your model in the key `'model_prediction'`. We provide an sample result [here](./HallusionBench_result_sample.json).
5. Finally, run the following code for evaluation:
```
python evaluation.py
```

We provide the API key in the script for convenience. You can also use your own API key for GPT4 evaluation by editing the code [here](./evaluation.py#L9)



## Leaderboard


### Definition
* **Visual Dependent (VD) Questions**: questions that do not have an affirmative answer without the visual context. 
  * **Easy**: Original images that are obtained from Internet.
  * **Hard**: Edited images from the original images.
* **Visual Supplement (VS) Questions**: questions that can be answered without the visual input; the visual component merely provides supplemental information.
  * **Easy**: No visual input. Uncertain answer without hallucination is also considered correct response.
  * **Hard**: With visual input. The answer must follow the provided figure and visual context.

### Metric


* **Accuracy per Figure (Consistency Test)**: Accuracy based on each figure. To make sure the mode truly understand image, we ask variant of questions based on the same knowledge on the same figure, and consider it correct if the model can answer all questions correctly. For example, the model should not give inconsistent responses on the questions "Is A bigger than B?" and "Is B smaller A?".
* **Accuracy per Question**: Accuracy of all questions, including easy and hard questions.
* **Accuracy per Question Pair**: We ask the same questions on similar images (or, with and without images). We consider the same question text on different visual contexts a **question pair** (usually they come in with an *easy* question and a corresponding *hard* question). This metric calculate accuracy of all question pairs.

| Model | Question Pair Acc | Figure Acc | Easy Question Acc | Hard Question Acc | Question Acc | Json |
| ----- | :----: | :----: | :----: | :----: | :----: | :----: |
| GPT4V <br />Sep 25, 2023 Version <br />(Human Eval) | 12.5984 | 30.4348 | 84.6154 | 30.6569 | 63.3858 | [VD](https://drive.google.com/file/d/1uQosejzzz8jsnk_pvowhU5aK-BHbu_Ny/view?usp=sharing), [VS](https://drive.google.com/file/d/1C7O9x26Fc29axdN7W4pQ-0hRmPOp1E6x/view?usp=sharing) |
| GPT4V <br />Sep 25, 2023 Version <br />(GPT Eval) | 12.2047 | 27.5362 | 83.7607 | 29.1971 | 61.0236 | [VD](https://drive.google.com/file/d/1uQosejzzz8jsnk_pvowhU5aK-BHbu_Ny/view?usp=sharing), [VS](https://drive.google.com/file/d/1C7O9x26Fc29axdN7W4pQ-0hRmPOp1E6x/view?usp=sharing) |
| LLaVA-1.5 <br />(Human Eval) | 2.7559 | 8.6957 | 40.1709 | 27.7372 | 38.189 | [VD](https://drive.google.com/file/d/1U3cS3I0Lpglz8Ej-NW6cp957GHT-T6yy/view?usp=sharing), [VS](https://drive.google.com/file/d/1hIvFqJFO0OVmPVfeq79_IUijt9mugOMV/view?usp=sharing) |
| LLaVA-1.5 <br />(GPT Eval) | 4.3307 | 7.2464 | 48.7179 | 26.2774 | 41.3386 | [VD](https://drive.google.com/file/d/1U3cS3I0Lpglz8Ej-NW6cp957GHT-T6yy/view?usp=sharing), [VS](https://drive.google.com/file/d/1hIvFqJFO0OVmPVfeq79_IUijt9mugOMV/view?usp=sharing) |
| etc. | TBD | TBD | TBD | TBD | TBD | TBD |


### Reproduce GPT4V results on leaderboard

1. We saved the ouput of GPT4V with our annotation. Put `HallusionBench.tsv` in the root directory of this repo, or set `input_file_name` in [benchmark.py](./benchmark.py) to the location of the [HallusionBench.tsv](https://drive.google.com/file/d/1p9BJw09l0ZXhv-owIEkXithLLAQrG60U/view?usp=sharing) file.

2. (Optional) If you don't have access to GPT API, you don't need to run it since we have saved evaluation results. They can be downloaded for [Visual Dependent](https://drive.google.com/file/d/1uQosejzzz8jsnk_pvowhU5aK-BHbu_Ny/view?usp=sharing) and [Visual Supplement](https://drive.google.com/file/d/1C7O9x26Fc29axdN7W4pQ-0hRmPOp1E6x/view?usp=sharing). Put the json files in the root directory of this repo, or set `save_json_path_vd` and `save_json_path_vd` in [benchmark.py](./benchmark.py) to their respective locations.

3. Run `python benchmark.py`.

## Examples and Analysis
<p align="center" >
      <img src="./examples/f-01.png" alt="Example 1" class="center" width="800"/> 
      <img src="./examples/f-02.png" alt="Example 2" class="center" width="800"/> 
      <img src="./examples/f-04.png" alt="Example 3" class="center" width="800"/> 
      <img src="./examples/f-05.png" alt="Example 4" class="center" width="800"/> 
      <img src="./examples/f-08.png" alt="Example 5" class="center" width="800"/> 
      <img src="./examples/f-15.png" alt="Example 6" class="center" width="800"/> 
      <img src="./examples/f-10.png" alt="Example 7" class="center" width="800"/> 
      <img src="./examples/f-12.png" alt="Example 8" class="center" width="800"/> 
      <img src="./examples/f-17.png" alt="Example 9" class="center" width="800"/> 
</p>

## License
This repository is under [BSD 3-Clause License](LICENSE.md). 
