# BioMedical-Named-Entity-Recognition-Using-LLMs

## Overview
This project explores the applicability of large language models (LLMs) for biomedical named entity recognition (BioNER) tasks. It compares the performance of two prominent LLMs, BLOOM-3b and Gemma-2b, on benchmark BioNER datasets for identifying and classifying biomedical entities such as genes, chemicals, diseases, and species. The goal is to determine the most accurate and robust LLM for BioNER and integrate it with a user interface for better accessibility.

## Large Language Models Used

### BLOOM-3b
- Developed collaboratively by HuggingFace, BigScience, and international academics and institutions
- Transformer-based, decoder-only architecture
- Design focuses on scalable model families, public tools support, and optimizations for smaller models

### Gemma-2b
- Part of Google DeepMind's lightweight Gemma LLM family
- Approximately 2 billion parameters, smaller than BLOOM-3b
- Uses multi-query attention mechanism for efficiency
- Trained on large text and code data, primarily in English

## Methodology
1. Model Selection and System Requirements: Factors like pipeline complexity, resource availability, and parameter understanding were considered for choosing LLMs.
2. Dataset Selection and Pre-processing: Publicly available benchmark BioNER datasets were used, including BC2GM (Gene/Protein), BC5CDR (Chemical, Disease), and BioNLP11ID-species.
3. Training: LLMs were fine-tuned using Parameter-Efficient Fine-Tuning (PEFT) techniques like Low-Rank Adaptation (LoRA) to reduce computational and storage costs.
4. Evaluation: The fine-tuned LLMs were evaluated on the benchmark datasets using precision, recall, and F1-score metrics.

## Results
The results showed that both BLOOM-3b and Gemma-2b performed well on the BioNER datasets, with BLOOM-3b achieving higher overall scores on precision, recall, and F1-score metrics. However, Gemma-2b demonstrated higher precision in some datasets.

