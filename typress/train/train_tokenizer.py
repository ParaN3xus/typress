from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers, processors
from .dataset import get_dataset_df
import tqdm


def train_tokenizer(dataset_path, vocab_size):
    df = get_dataset_df(dataset_path)
    texts = df["text"].tolist()
    texts = tqdm(texts)

    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)

    special_tokens = [
        {
            "id": 0,
            "content": "<pad>",
            "single_word": False,
            "lstrip": False,
            "rstrip": False,
            "normalized": False,
            "special": True,
        },
        {
            "id": 1,
            "content": "<s>",
            "single_word": False,
            "lstrip": False,
            "rstrip": False,
            "normalized": False,
            "special": True,
        },
        {
            "id": 2,
            "content": "</s>",
            "single_word": False,
            "lstrip": False,
            "rstrip": False,
            "normalized": False,
            "special": True,
        },
        {
            "id": 3,
            "content": "<unk>",
            "single_word": False,
            "lstrip": False,
            "rstrip": False,
            "normalized": False,
            "special": True,
        },
        {
            "id": 4,
            "content": "<mask>",
            "single_word": False,
            "lstrip": True,
            "rstrip": False,
            "normalized": False,
            "special": True,
        },
    ]

    tokenizer.post_processor = processors.RobertaProcessing(
        ("</s>", 2),
        ("<s>", 1),
    )

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        special_tokens=[token["content"] for token in special_tokens],
    )

    tokenizer.train_from_iterator(texts, trainer)
    tokenizer.decoder = decoders.ByteLevel(add_prefix_space=True)

    tokenizer.save(f"${dataset_path}/tokenizer/tokenizer.json")
    print(f"Tokenizer saved to f{dataset_path}/tokenizer/tokenizer.json")
