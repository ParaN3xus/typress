from typing import List
from tqdm import tqdm
import torch
import evaluate
from torch.utils.data import DataLoader

cer_metric = evaluate.load("cer")


def compute_cer(pred_ids, label_ids, processor):
    pred_str = processor.batch_decode(pred_ids, skip_special_tokens=True)
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    label_str = processor.batch_decode(label_ids, skip_special_tokens=True)

    cer = cer_metric.compute(predictions=pred_str, references=label_str)

    return cer


def eval(model, eval_dataloaders: List[DataLoader], device, logger):
    model.eval()

    logger.log_metrics({"status": "evaluation_started"})
    final_cer = []

    for i, eval_dataloader in enumerate(eval_dataloaders):
        valid_cer = 0.0
        with torch.no_grad():
            for batch in tqdm(eval_dataloader):
                outputs = model.module.generate(
                    batch["pixel_values"].to(device))
                outputs.to(device)

                # compute metrics
                cer = compute_cer(
                    pred_ids=outputs,
                    label_ids=batch["labels"].to(device),
                    processor=eval_dataloader.dataset.processor,
                )
                valid_cer += cer

        final_cer.append(valid_cer / len(eval_dataloader))

    logger.log_metrics({
        "status": "evaluation_completed",
        "final_cers": final_cer,
    })

    return valid_cer
