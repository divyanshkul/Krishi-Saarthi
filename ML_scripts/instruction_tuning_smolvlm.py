#!/usr/bin/env python3
# Dataset: https://huggingface.co/Agri-LLaVA-Anonymous

import os
import torch
import wandb
from PIL import Image
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from transformers import (
    AutoProcessor, 
    BitsAndBytesConfig, 
    Idefics3ForConditionalGeneration,
    TrainingArguments, 
    Trainer
)
from transformers.models.idefics3.modeling_idefics3 import Idefics3VisionEmbeddings

USE_LORA = False
USE_QLORA = True
SMOL = True
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model_id = "HuggingFaceTB/SmolVLM-Base" if SMOL else "HuggingFaceM4/Idefics3-8B-Llama3"
model_name = "SMOL-vlm"

WANDB_PROJECT = "smolvlm-agriculture-finetuning"
WANDB_RUN_NAME = f"{model_name}-qlora-agri-pests"

def patch_idefics3_vision_embeddings():
    original_forward = Idefics3VisionEmbeddings.forward
    
    def fixed_forward(self, pixel_values: torch.FloatTensor, patch_attention_mask: torch.BoolTensor) -> torch.Tensor:
        batch_size, _, max_im_h, max_im_w = pixel_values.shape
        patch_embeds = self.patch_embedding(pixel_values)
        embeddings = patch_embeds.flatten(2).transpose(1, 2)
        max_nb_patches_h, max_nb_patches_w = max_im_h // self.patch_size, max_im_w // self.patch_size
        boundaries = torch.arange(1 / self.num_patches_per_side, 1.0, 1 / self.num_patches_per_side)
        boundaries = boundaries.to(embeddings.device)
        position_ids = torch.full(size=(batch_size, max_nb_patches_h * max_nb_patches_w), fill_value=0)
        position_ids = position_ids.to(embeddings.device)
        for batch_idx, p_attn_mask in enumerate(patch_attention_mask):
            p_attn_mask = p_attn_mask.to(embeddings.device)
            nb_patches_h = p_attn_mask[:, 0].sum()
            nb_patches_w = p_attn_mask[0].sum()
            nb_patches_h = nb_patches_h.to(dtype=torch.float32, device=embeddings.device)
            nb_patches_w = nb_patches_w.to(dtype=torch.float32, device=embeddings.device)
            h_indices = torch.arange(nb_patches_h.item(), device=embeddings.device, dtype=torch.float32)
            w_indices = torch.arange(nb_patches_w.item(), device=embeddings.device, dtype=torch.float32)
            fractional_coords_h = h_indices / nb_patches_h * (1 - 1e-6)
            fractional_coords_w = w_indices / nb_patches_w * (1 - 1e-6)
            bucket_coords_h = torch.bucketize(fractional_coords_h, boundaries, right=True)
            bucket_coords_w = torch.bucketize(fractional_coords_w, boundaries, right=True)
            pos_ids = (bucket_coords_h[:, None] * self.num_patches_per_side + bucket_coords_w).flatten()
            mask_flat = p_attn_mask.view(-1)
            position_ids[batch_idx][mask_flat] = pos_ids.to(position_ids.dtype)
        position_ids = position_ids.to(self.position_embedding.weight.device)
        embeddings = embeddings + self.position_embedding(position_ids)
        return embeddings
    
    Idefics3VisionEmbeddings.forward = fixed_forward
    print("Idefics3VisionEmbeddings patched successfully!")

def simple_collate_fix(examples, processor, image_token_id):
    texts = []
    images = []
    for example in examples:
        image_filename = example["image"]
        image_path = os.path.join("/data/azfarm/siddhant/capOne-Hack/Img/Img", image_filename)
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        messages = []
        conversations = example["conversations"]
        for i, conv in enumerate(conversations):
            if conv["from"] == "human":
                text_content = conv["value"].replace("<image>", "").strip()
                if i == 0:
                    content = [
                        {"type": "image"},
                        {"type": "text", "text": text_content}
                    ]
                else:
                    content = [{"type": "text", "text": text_content}]
                messages.append({
                    "role": "user",
                    "content": content
                })
            elif conv["from"] == "gpt":
                messages.append({
                    "role": "assistant", 
                    "content": [{"type": "text", "text": conv["value"]}]
                })
        text = processor.apply_chat_template(messages, add_generation_prompt=False)
        texts.append(text.strip())
        images.append([image])
    batch = processor(text=texts, images=images, return_tensors="pt", padding=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    for key, value in batch.items():
        if isinstance(value, torch.Tensor):
            batch[key] = value.to(device)
    labels = batch["input_ids"].clone()
    labels[labels == processor.tokenizer.pad_token_id] = -100
    labels[labels == image_token_id] = -100
    batch["labels"] = labels
    return batch

def main():
    print("Starting SmolVLM fine-tuning...")
    wandb.init(
        project=WANDB_PROJECT,
        name=WANDB_RUN_NAME,
        config={
            "model_id": model_id,
            "use_lora": USE_LORA,
            "use_qlora": USE_QLORA,
            "smol_model": SMOL,
            "device": DEVICE,
            "dataset": "Agricultural_pests_and_diseases_instruction_tuning_data",
            "subset_size": 1000,
            "epochs": 2,
            "batch_size": 1,
            "gradient_accumulation_steps": 4,
            "learning_rate": 1e-4,
            "weight_decay": 0.01,
            "warmup_steps": 25,
            "lora_r": 8,
            "lora_alpha": 8,
            "lora_dropout": 0.1,
        },
        tags=["smolvlm", "agriculture", "vision-language", "qlora", "finetuning"]
    )
    wandb.log({
        "system/gpu_count": torch.cuda.device_count(),
        "system/gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "system/cuda_available": torch.cuda.is_available(),
        "system/torch_version": torch.__version__,
    })
    patch_idefics3_vision_embeddings()
    print(f"Loading processor from {model_id}...")
    processor = AutoProcessor.from_pretrained(model_id)
    image_token_id = processor.tokenizer.additional_special_tokens_ids[
        processor.tokenizer.additional_special_tokens.index("<image>")]
    if USE_QLORA or USE_LORA:
        lora_config = LoraConfig(
            r=8,
            lora_alpha=8,
            lora_dropout=0.1,
            target_modules=['down_proj','o_proj','k_proj','q_proj','gate_proj','up_proj','v_proj'],
            use_dora=False if USE_QLORA else True,
            init_lora_weights="gaussian"
        )
        lora_config.inference_mode = False
        if USE_QLORA:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
    print(f"Loading model from {model_id}...")
    if USE_QLORA or USE_LORA:
        model = Idefics3ForConditionalGeneration.from_pretrained(
            model_id,
            quantization_config=bnb_config if USE_QLORA else None,
            device_map="auto"
        )
        model.add_adapter(lora_config)
        model.enable_adapters()
        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, lora_config)
        trainable_params, total_params = model.get_nb_trainable_parameters()
        print(f"Trainable parameters: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
        wandb.log({
            "model/trainable_parameters": trainable_params,
            "model/total_parameters": total_params,
            "model/trainable_percentage": 100 * trainable_params / total_params,
            "model/quantization": "4bit" if USE_QLORA else "none",
            "model/lora_rank": 8,
        })
    else:
        model = Idefics3ForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            _attn_implementation="flash_attention_2",
        ).to(DEVICE)
        frozen_params = 0
        total_params = 0
        for param in model.model.vision_model.parameters():
            param.requires_grad = False
            frozen_params += param.numel()
        for param in model.parameters():
            total_params += param.numel()
        trainable_params = total_params - frozen_params
        print(f"Trainable parameters: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
        wandb.log({
            "model/trainable_parameters": trainable_params,
            "model/total_parameters": total_params,
            "model/trainable_percentage": 100 * trainable_params / total_params,
            "model/quantization": "none",
            "model/vision_frozen": True,
        })
    print("Loading dataset...")
    ds = load_dataset("Agri-LLaVA-Anonymous/Agricultural_pests_and_diseases_instruction_tuning_data")
    train_subset = ds['train'].shuffle(seed=42).select(range(1000))
    print(f"Original dataset size: {len(ds['train'])}")
    print(f"Subset size: {len(train_subset)}")
    wandb.log({
        "dataset/original_size": len(ds['train']),
        "dataset/subset_size": len(train_subset),
        "dataset/subset_ratio": len(train_subset) / len(ds['train']),
    })
    sample_data = []
    for i in range(min(5, len(train_subset))):
        example = train_subset[i]
        try:
            image_filename = example["image"]
            image_path = os.path.join("/data/azfarm/siddhant/capOne-Hack/Img/Img", image_filename)
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            conversation_text = ""
            for conv in example["conversations"]:
                role = "Human" if conv["from"] == "human" else "Assistant"
                text = conv["value"].replace("<image>", "[IMAGE]")
                conversation_text += f"{role}: {text}\n"
            sample_data.append([
                wandb.Image(image, caption=f"Sample {i+1}: {image_filename}"),
                conversation_text[:500] + "..." if len(conversation_text) > 500 else conversation_text
            ])
        except Exception as e:
            print(f"Could not log sample {i}: {e}")
    if sample_data:
        wandb.log({
            "samples": wandb.Table(
                columns=["Image", "Conversation"],
                data=sample_data
            )
        })
    def collate_fn(examples):
        return simple_collate_fix(examples, processor, image_token_id)
    training_args = TrainingArguments(
        num_train_epochs=2, 
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4, 
        warmup_steps=25,  
        learning_rate=1e-4,
        weight_decay=0.01,
        logging_steps=10, 
        save_strategy="steps",
        save_steps=100,  
        save_total_limit=2,
        optim="paged_adamw_8bit",
        bf16=True,
        output_dir=f"./{model_name}-vqav2-subset",
        hub_model_id=f"{model_name}-vqav2-subset",
        remove_unused_columns=False,
        gradient_checkpointing=True,
        dataloader_pin_memory=False,
        max_grad_norm=1.0,
        dataloader_num_workers=0,
        report_to="wandb",
        logging_dir=f"./{model_name}-vqav2-subset/logs",
        run_name=WANDB_RUN_NAME,
    )
    print("Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_subset,  
        data_collator=collate_fn,  
        processing_class=processor.tokenizer,
    )
    print("Starting training...")
    trainer.train()
    final_metrics = {
        "training/completed": True,
        "training/final_epoch": 2,
        "training/total_steps": len(trainer.state.log_history),
    }
    if trainer.state.log_history:
        final_loss = trainer.state.log_history[-1].get('train_loss', None)
        if final_loss:
            final_metrics["training/final_loss"] = final_loss
    wa
