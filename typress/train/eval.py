from tqdm import tqdm
import torch
import evaluate

cer_metric = evaluate.load("cer")


def compute_cer(pred_ids, label_ids, processor):
    pred_str = processor.batch_decode(pred_ids, skip_special_tokens=True)
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    label_str = processor.batch_decode(label_ids, skip_special_tokens=True)

    cer = cer_metric.compute(predictions=pred_str, references=label_str)

    return cer


def eval(model, processor, eval_dataloader, device):
    model.eval()
    valid_cer = 0.0
    with torch.no_grad():
        for batch in tqdm(eval_dataloader):
            outputs = model.module.generate(batch["pixel_values"].to(device))
            outputs.to(device)

            # compute metrics
            cer = compute_cer(
                pred_ids=outputs,
                label_ids=batch["labels"].to(device),
                processor=processor,
            )
            valid_cer += cer

    return valid_cer
