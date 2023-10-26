# HallusionBench: You See What You Think? Or You Think What You See? An Image-Context Reasoning Benchmark Challenging for GPT-4V(ision), LLaVA-1.5, and Other Multi-modality Models

[Fuxiao Liu*](https://fuxiaoliu.github.io/), [Tianrui Guan*](https://tianruiguan.phd), Zongxia Li, Lichang Chen, Yaser Yacoob, Dinesh Manocha, Tianyi Zhou

🔥🔥🔥<span style="color:red">We welcome everyone to contribute the failure cases of Large Multimodal Models (GPT-4V) to our community!</span>🔥🔥🔥

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
- [-/-] 🔥 The leaderboard and evaluation code will be released this week!
- [10/24] 🔥 The early report with case analysis and insights is available [here](https://arxiv.org/abs/2310.14566).
- [10/23] 🔥 Please check our previous work on mitigating hallucinations of LMMs ["Mitigating Hallucination in Large Multi-Modal Models via Robust Instruction Tuning"](https://github.com/FuxiaoLiu/LRV-Instruction).

## Dataset

Coming Soon!

## Leaderboard

Coming Soon!

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
