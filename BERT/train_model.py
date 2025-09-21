"""
Train BERT on multi-label classification for: "feeling_pos", "feeling_neg", "music_ref", "external_ref", "phys_react".
Tutorial for multi-label classification used: https://colab.research.google.com/github/NielsRogge/Transformers-Tutorials/blob/master/BERT/Fine_tuning_BERT_(and_friends)_for_multi_label_text_classification.ipynb#scrollTo=KOBosj4UL2tU
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
from datasets import load_from_disk
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score
from transformers import EvalPrediction
import torch
import sys

# pass dataset (dict)
dataset = load_from_disk(sys.argv[1])
out_dir_model = sys.argv[2]


LABEL_NAMES = ["feeling_pos", "feeling_neg", "music_ref", "external_ref", "phys_react"]
labels = ["feeling_pos", "feeling_neg", "music_ref", "external_ref", "phys_react"]
id2label = {idx:label for idx, label in enumerate(labels)}
label2id = {label:idx for idx, label in enumerate(labels)}

# get tokanizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

'''
Preprocess data for training.
'''
def preprocess_data(examples):
  # take a batch of texts
  text = examples["message"]
  # encode them
  encoding = tokenizer(text, padding="max_length", truncation=True, max_length=128)
  # add labels
  labels_batch = {k: examples[k] for k in examples.keys() if k in labels}
  # create numpy array of shape (batch_size, num_labels)
  labels_matrix = np.zeros((len(text), len(labels)))
  # fill numpy array
  for idx, label in enumerate(labels):
    if label in labels_batch:
        labels_matrix[:, idx] = labels_batch[label]
    else:
        print(f"Label {label} not found in batch!")

  encoding["labels"] = labels_matrix.tolist()
  
  return encoding

encoded_dataset = dataset.map(preprocess_data, batched=True, remove_columns=dataset['train'].column_names)
encoded_dataset.set_format("torch")

# choose model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", 
                                                           problem_type="multi_label_classification", 
                                                           num_labels=len(labels),
                                                           id2label=id2label,
                                                           label2id=label2id)

# define batch size and the wanted evaluation metric
batch_size = 8
metric_name = "f1"

# define training arguments
args = TrainingArguments(
    out_dir_model,
    evaluation_strategy = "epoch",
    save_strategy = "epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model=metric_name,
    #push_to_hub=True,
)

'''
Calculate accuaracy and f1 score per label
'''
def single_label_metrics(y_true, y_pred, label_names):
    metrics = {}
    num_labels = y_true.shape[1]
    # iterate through labels
    for i in range(num_labels):
        label = label_names[i] if i < len(label_names) else f"label_{i}"
        # calc accuracy
        acc = accuracy_score(y_true[:, i], y_pred[:, i])
        # calc f1
        f1 = f1_score(y_true[:, i], y_pred[:, i], zero_division=0)
        metrics[f'accuracy_{label}'] = acc
        metrics[f'f1_{label}'] = f1
    return metrics


def multi_label_metrics(predictions, labels, threshold=0.5):
    # first, apply sigmoid on predictions which are of shape (batch_size, num_labels)
    sigmoid = torch.nn.Sigmoid()
    probs = sigmoid(torch.Tensor(predictions))
    # next, use threshold to turn them into integer predictions
    y_pred = np.zeros(probs.shape)
    y_pred[np.where(probs >= threshold)] = 1
    # finally, compute metrics
    y_true = labels

    f1_micro_average = f1_score(y_true=y_true, y_pred=y_pred, average='micro')
    roc_auc = roc_auc_score(y_true, y_pred, average = 'micro')
    accuracy = accuracy_score(y_true, y_pred)
    
    # calculate per-label metric
    per_label = single_label_metrics(np.array(y_true), np.array(y_pred), label_names=LABEL_NAMES)
    
    # put together
    metrics = {
        'f1': f1_micro_average,
        'roc_auc': roc_auc,
        'accuracy': accuracy
    }
    metrics.update(per_label)
    
    return metrics

'''
Helper: compute the metrics.
'''
def compute_metrics(p: EvalPrediction):
    preds = p.predictions[0] if isinstance(p.predictions, 
            tuple) else p.predictions
    result = multi_label_metrics(
        predictions=preds, 
        labels=p.label_ids)
    return result

# forward pass
outputs = model(input_ids=encoded_dataset['train']['input_ids'][0].unsqueeze(0), labels=encoded_dataset['train'][0]['labels'].unsqueeze(0))

# initialize trainer
trainer = Trainer(
    model,
    args,
    train_dataset=encoded_dataset["train"],
    eval_dataset=encoded_dataset["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# train the model
trainer.train()

# evaluate the model
trainer.evaluate()

# ------ example on how to use model -----

""" text = "Let me enjoy this great concert!"

encoding = tokenizer(text, return_tensors="pt")
encoding = {k: v.to(trainer.model.device) for k,v in encoding.items()}

outputs = trainer.model(**encoding)
logits = outputs.logits
# apply sigmoid + threshold
sigmoid = torch.nn.Sigmoid()
probs = sigmoid(logits.squeeze().cpu())
predictions = np.zeros(probs.shape)
predictions[np.where(probs >= 0.5)] = 1
# turn predicted id's into actual label names
predicted_labels = [id2label[idx] for idx, label in enumerate(predictions) if label == 1.0]
print(predicted_labels) """
