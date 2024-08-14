# Fundus News Scraper Evaluation

This repository contains the evaluation code and dataset to reproduce the results from the [paper](https://arxiv.org/abs/2403.15279) "FUNDUS: A Simple-to-Use News Scraper Optimized for High Quality Extractions".

[Fundus](https://github.com/flairNLP/fundus) is a user-friendly news scraper that enables users to obtain millions of high-quality news articles with just a few lines of code.

In the following sections, we provide instructions to reproduce the comparative evaluation of Fundus against prominent scraping libraries.
Our evaluation shows that Fundus yields significantly higher quality extractions (complete and artifact-free news articles) than comparable news scrapers.
For a more in-depth overview of Fundus, the evaluation practises, and its results, consult the [result summary](https://github.com/dobbersc/fundus-evaluation/tree/master?tab=readme-ov-file#results) and our [paper](https://arxiv.org/abs/2403.15279).

## Prerequisites

Fundus and this evaluation repository require Python 3.8 or later and Java for the Boilerpipe scraper.
*(Note: The evaluation was tested and performed using Python 3.8 and Java JDK 17.0.10.)*

To install the `fundus-evaluation` Python package, including the reference scraper dependencies, clone this GitHub repository and simply install the package using pip:

```bash
git clone https://github.com/dobbersc/fundus-evaluation.git
pip install ./fundus-evaluation
```

This installation also contains the dataset and evaluation results.
If you only are interested in the Python package directly (without the dataset and evaluation results), install the `fundus-evaluation` package directly from GitHub using pip:

```bash
pip install git+https://github.com/dobbersc/fundus-evaluation.git@master
```

Verify the installation by running `evaluate --version`, with the expected output of `evaluate <version>`, where `<version>` specifies the current version of the evaluation package.

#### Development

For development, install the package, including the development dependencies:

```bash
git clone https://github.com/dobbersc/fundus-evaluation.git
pip install -e ./fundus-evaluation[dev]
```

## Reproducing the Evaluation Results

In the following steps, we assume that the current working directory is the root of the repository.

To fully reproduce the evaluation results, only the dataset is required.
Each step in the evaluation pipeline requires the outputs from the previous step (*dataset -> scrape -> score -> analysis*).
To ease the reproducibility, we also provide the artifacts of intermediate steps in the `dataset` folder.
Therefore, the pipeline may be started from any step.

#### Usage

The evaluation results may be reproduced using the package's command line interface (CLI), representing the evaluation pipeline steps:

```console
$ evaluate --help
usage: evaluate [-h] [--version] {complexity,scrape,score,analysis} ...

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

Fundus News Scraper Evaluation:
  select evaluation pipeline step

  {complexity,scrape,score,analysis}
    complexity          calculate page complexity scores
    scrape              scrape extractions on the evaluation dataset
    score               calculate evaluation scores
    analysis            generate tables and plots
```

Each entry point also provides its help page, e.g. with `evaluate scrape --help`.

Alternatively to the CLI, we provide direct Python entry points in `fundus_evaluation.entry_points`.
In the following steps, we will use the CLI.

### (1) Obtaining the Evaluation Dataset

We selected the 16 English-language publishers Fundus currently supports as the data source, and retrieved five articles for each publisher from the respective RSS feeds/sitemaps.
The selection process yielded an evaluation corpus of 80 news articles.
From it, we manually extracted the plain text from each article and stored it together with information on the original paragraph structure. 

The resulting evaluation dataset is included in this repository and consists of the (compressed) HTML [article files](https://github.com/dobbersc/fundus-evaluation/tree/master/dataset/html) and their [ground truth extractions](https://github.com/dobbersc/fundus-evaluation/blob/master/dataset/ground_truth.json) as JSON.

### (2) Generating the Scraper Extractions

Execute the following command to let all supported scrapers extract the plain text of the evaluation dataset's articles:

```bash
evaluate scrape \
  --ground-truth-path dataset/ground_truth.json \
  --html-directory dataset/html/ \
  --output-directory dataset/extractions/
```

To restrict the scrapers that are part of the evaluation, 
  - use the `--scrapers` option to explicitly specify a list of evaluation scrapers, 
  - or use the `--exclude-scrapers` option to exclude scrapers from the evaluation.

E.g. to exclude BoilerNet, as this scraper is very resource intensive, add the `--exclude-scrapers boilernet` argument to the command above.

### (3) Calculating the Evaluation Scores

To evaluate the extraction results with the three supported metrics (paragraph match, ROUGE-LSum and WER), run the following command:

```bash
evaluate score \
  --ground-truth-path dataset/ground_truth.json \
  --extractions-directory dataset/extractions/ \
  --output-directory dataset/scores/
```

#### Calculating the Page Complexity (Optional)

This step is not part of the evaluation in our paper and is thus optional.

Execute the following command to calculate the page complexity scores established in ["An Empirical Comparison of Web Content Extraction Algorithms"](https://downloads.webis.de/publications/papers/bevendorff_2023b.pdf) (Bevendorff et al., 2023):

```bash
evaluate complexity \
  --ground-truth-path dataset/ground_truth.json \
  --html-directory dataset/html/ \
  --output-path dataset/complexity.tsv
```

### (4) Analyzing the Data

Run the following command to produce the paper's tables and plots for the ROUGE-LSum score: 

```bash
evaluate analysis --rouge-lsum-path dataset/scores/rouge_lsum.tsv --output-directory dataset/analysis/
```

To also produce a boxplot of the page complexity, execute:

```bash
evaluate analysis --complexity-path dataset/complexity.tsv --output-directory dataset/analysis/
```

## Results

The following table summarizes the overall performance of Fundus and evaluated scrapers in terms of averaged ROUGE-LSum precision, recall and F1-score and their standard deviation.
In addition, we provide the scrapers' versions at their evaluation time.
The table is sorted in descending order over the F1-score:

#### Fundus-Evaluation v0.2.0 

| **Scraper**                                                                                                     | **Precision**             | **Recall**                | **F1-Score**              | **Version** |
|-----------------------------------------------------------------------------------------------------------------|:--------------------------|---------------------------|---------------------------|-------------|
| [Fundus](https://github.com/flairNLP/fundus)                                                                    | **99.89**<sub>±0.57</sub> | 96.75<sub>±12.75</sub>    | **97.69**<sub>±9.75</sub> | 0.4.1       |
| [Trafilatura](https://github.com/adbar/trafilatura)                                                             | 93.91<sub>±12.89</sub>    | 96.85<sub>±15.69</sub>    | 93.62<sub>±16.73</sub>    | 1.12.0      |
| [news-please](https://github.com/fhamborg/news-please)                                                          | 97.95<sub>±10.08</sub>    | 91.89<sub>±16.15</sub>    | 93.39<sub>±14.52</sub>    | 1.6.13      |
| [BTE](https://github.com/dobbersc/fundus-evaluation/blob/master/src/fundus_evaluation/scrapers/bte.py)          | 81.09<sub>±19.41</sub>    | **98.23**<sub>±8.61</sub> | 87.14<sub>±15.48</sub>    | /           |
| [jusText](https://github.com/miso-belica/jusText)                                                               | 86.51<sub>±18.92</sub>    | 90.23<sub>±20.61</sub>    | 86.96<sub>±19.76</sub>    | 3.0.1       |
| [BoilerNet](https://github.com/dobbersc/fundus-evaluation/tree/master/src/fundus_evaluation/scrapers/boilernet) | 85.96<sub>±18.55</sub>    | 91.21<sub>±19.15</sub>    | 86.52<sub>±18.03</sub>    | /           |
| [Boilerpipe](https://github.com/kohlschutter/boilerpipe)                                                        | 82.89<sub>±20.65</sub>    | 82.11<sub>±29.99</sub>    | 79.90<sub>±25.86</sub>    | 1.3.0       |

<details>
<summary>Previous Results</summary>

#### Fundus-Evaluation v0.1.0 

| **Scraper**                                                                                                     | **Precision**             | **Recall**                | **F1-Score**              | **Version** |
|-----------------------------------------------------------------------------------------------------------------|:--------------------------|---------------------------|---------------------------|-------------|
| [Fundus](https://github.com/flairNLP/fundus)                                                                    | **99.89**<sub>±0.57</sub> | 96.75<sub>±12.75</sub>    | **97.69**<sub>±9.75</sub> | 0.2.2       |
| [Trafilatura](https://github.com/adbar/trafilatura)                                                             | 90.54<sub>±18.86</sub>    | 93.23<sub>±23.81</sub>    | 89.81<sub>±23.69</sub>    | 1.7.0       |
| [BTE](https://github.com/dobbersc/fundus-evaluation/blob/master/src/fundus_evaluation/scrapers/bte.py)          | 81.09<sub>±19.41</sub>    | **98.23**<sub>±8.61</sub> | 87.14<sub>±15.48</sub>    | /           |
| [jusText](https://github.com/miso-belica/jusText)                                                               | 86.51<sub>±18.92</sub>    | 90.23<sub>±20.61</sub>    | 86.96<sub>±19.76</sub>    | 3.0.0       |
| [news-please](https://github.com/fhamborg/news-please)                                                          | 92.26<sub>±12.40</sub>    | 86.38<sub>±27.59</sub>    | 85.81<sub>±23.29</sub>    | 1.5.44      |
| [BoilerNet](https://github.com/dobbersc/fundus-evaluation/tree/master/src/fundus_evaluation/scrapers/boilernet) | 84.73<sub>±20.82</sub>    | 90.66<sub>±21.05</sub>    | 85.77<sub>±20.28</sub>    | /           |
| [Boilerpipe](https://github.com/kohlschutter/boilerpipe)                                                        | 82.89<sub>±20.65</sub>    | 82.11<sub>±29.99</sub>    | 79.90<sub>±25.86</sub>    | 1.3.0       |

</details>

## Cite

Please cite the following [paper](https://arxiv.org/abs/2403.15279) when using Fundus or building upon our work:

```bibtex
@misc{dallabetta2024fundus,
      title={Fundus: A Simple-to-Use News Scraper Optimized for High Quality Extractions}, 
      author={Max Dallabetta and Conrad Dobberstein and Adrian Breiding and Alan Akbik},
      year={2024},
      eprint={2403.15279},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## Acknowledgements
- This repository's architecture has been inspired by the [web content extraction benchmark](https://github.com/chatnoir-eu/web-content-extraction-benchmark) (Bevendorff et al., 2023).
- Since BoilerNet has no Python package on PyPI, we adopted a [stripped-down version](https://github.com/chatnoir-eu/web-content-extraction-benchmark/tree/main/src/extraction_benchmark/extractors/boilernet) of the upstream BoilerNet provided by Bevendorff et al. from their web content extraction benchmark.
- Similarly, BTE has no Python package on PyPI. Here, we used the implementation by Jan Pomikalek found from [this](https://github.com/chatnoir-eu/web-content-extraction-benchmark/blob/221b6503d66bf4faa378e6ae3c3f63ee01d584c6/src/extraction_benchmark/extractors/bte.py) and [this](https://github.com/dalab/web2text/blob/0f9c7b787ff125ce5190784e741c5b453ddf0560/other_frameworks/bte/bte.py) source.
