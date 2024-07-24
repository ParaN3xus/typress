# Typress

Typst Mathematical Expression OCR based on [TrOCR](https://github.com/microsoft/unilm/tree/master/trocr).

## Install
#### Clone the Repository

Clone this repo and enter it:

```sh
git clone https://github.com/ParaN3xus/typress
cd typress
```

Install dependencies
```sh
pip install -r requirements.txt
```

#### TODO: PyPI

## Run

### Development Run



#### Run Typress Web server
Ensure you are in the repo root directory and execute

```sh
python typress
```

### Production Run

#### Set Up .env
Install dependencies
```sh
pip install -r requirements.txt
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