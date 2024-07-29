# Typress

[![Open Source License](https://img.shields.io/github/license/paran3xus/typress?logo=github)](https://opensource.org/license/mit)
[![Hugging Face Weights](https://img.shields.io/badge/Weights-TypressOCR-yellow.svg?logo=huggingface)](https://huggingface.co/paran3xus/typress_ocr)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/paran3xus/typress_ocr_space)


Typst Mathematical Expression OCR based on [TrOCR](https://github.com/microsoft/unilm/tree/master/trocr).

## Install
### Clone the Repository

Clone this repo and enter it:

```sh
git clone https://github.com/ParaN3xus/typress
cd typress
```

Install dependencies:

We use [Poetry](https://python-poetry.org/) to manage project dependencies. If you don't have Poetry installed, please follow the instructions on the [Poetry installation page](https://python-poetry.org/docs/).
```sh
poetry install
poetry shell
```

### TODO: PyPI

## Run

### Development Run

#### Run Typress Web server
Ensure you are in the repo root directory and execute

```sh
python -m typress
```

### Production Run

#### Set Up .env

Create a .env file in the repo root directory with the following content:

```sh
MODEL_PATH=path/to/your/model
API_ROOT_URL=https://api.example.com/typress
```

#### Run WSGI

To run the application in production mode, it is recommended to use a production-grade WSGI server such as `gunicorn`:

```sh
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

## TODO
- [ ] Improve the tex2typ reconstruction strategy for `mat`, `delimsizing`, and `spacing`.
- [ ] Fix memory leaks in normalized formulas
- [ ] Add formula detection
- [ ] Explore using LoRA to fine-tune the OCR model for TeX
- [ ] Publish to PyPI
- [ ] Document the complete dataset construction process
- [ ] Train using `seq2seqtrainer`

## Contributing

### Data Contribution
If you have a collection of Typst mathematical formula text (which can be included in Typst documents), you can create a dataset by running the following command in the Typst workspace root:

```bash
python -m typress.dataset extract
```
    
Then, submit the generated `out.json` file to us via email at paran3xus007@gmail.com. By submitting your data to us, you agree to make your dataset publicly available.

### Code Contribution
We welcome any code contributions, including bug fixes, feature additions, etc. If you're unsure where to start, you can refer to our Todo list.

## License

This repository is published under an MIT License. See [LICENSE](https://github.com/ParaN3xus/typress/blob/main/LICENSE) file


## Credits

This project makes use of the following open-source projects or datasets:

- [TrOCR](https://github.com/microsoft/unilm/tree/master/trocr): Transformer-based Optical Character Recognition with Pre-trained Models.
- [tramsformers](https://github.com/huggingface/transformers): State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.
- [evaluate](https://github.com/huggingface/evaluate): A library for easily evaluating machine learning models and datasets.
- [eq_query_rec](https://github.com/sjfhsjfh/eq_query_rec): Query equations from Typst source file and reconstruct normalized equation from querying result.
- [typst.ts](https://github.com/Myriad-Dreamin/typst.ts): Run Typst in JavaScriptWorld.
- [fusion-image-to-latex-datasets](https://huggingface.co/datasets/hoang-quoc-trung/fusion-image-to-latex-datasets): The largest dataset to date from online sources.
- [latex-formulas](https://huggingface.co/datasets/OleehyO/latex-formulas): TexTeller previous dataset.

Thanks to the developers and contributors of these projects for their hard work and dedication.

Thanks to @sjfhsjfh, @Naptie, @mivik for providing Typst mathematical formula data.
