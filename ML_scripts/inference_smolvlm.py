#!/usr/bin/env python3
"""
SmolVLM Inference Script
Compare outputs between original SmolVLM and fine-tuned model with agricultural pest/disease adapters
"""

import os
import torch
from PIL import Image
from peft import PeftModel
from transformers import (
    AutoProcessor, 
    BitsAndBytesConfig, 
    Idefics3ForConditionalGeneration
)
from transformers.models.idefics3.modeling_idefics3 import Idefics3VisionEmbeddings

def patch_idefics3_vision_embeddings():
    """
    Apply the same patch as in training to fix device mismatch issues
    """
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
    print("✅ Idefics3VisionEmbeddings patched successfully!")

class SmolVLMInferenceComparator:
    def __init__(self, 
                 base_model_id="HuggingFaceTB/SmolVLM-Base",
                 adapter_path="./SMOL-vlm-final",  # Path to your saved fine-tuned model
                 device="cuda" if torch.cuda.is_available() else "cpu"):
        
        self.base_model_id = base_model_id
        self.adapter_path = adapter_path
        self.device = device
        

        patch_idefics3_vision_embeddings()
        
        print(f"Loading processor from {base_model_id}...")
        self.processor = AutoProcessor.from_pretrained(base_model_id)
        
        # Load original model
        print("Loading original model...")
        self.original_model = self._load_original_model()
        
        # Load fine-tuned model
        print("Loading fine-tuned model...")
        self.finetuned_model = self._load_finetuned_model()
        
    def _load_original_model(self):
        """Load the original SmolVLM model"""
        model = Idefics3ForConditionalGeneration.from_pretrained(
            self.base_model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        model.eval()
        return model
    
    def _load_finetuned_model(self):
        """Load the fine-tuned model with adapters"""
      
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        base_model = Idefics3ForConditionalGeneration.from_pretrained(
            self.base_model_id,
            quantization_config=bnb_config,
            device_map="auto"
        )
        

        model = PeftModel.from_pretrained(base_model, self.adapter_path)
        model.eval()
        return model
    
    def generate_response(self, model, image, question, max_new_tokens=512, temperature=0.1):
        """Generate response from a model given an image and question"""
        
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": question}
                ]
            }
        ]
        
        
        text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        
      
        inputs = self.processor(text=text, images=[image], return_tensors="pt")
        
      
        device = next(model.parameters()).device
        for key, value in inputs.items():
            if isinstance(value, torch.Tensor):
                inputs[key] = value.to(device)
        
     
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                pad_token_id=self.processor.tokenizer.eos_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
            )
        
    
        generated_text = self.processor.batch_decode(
            generated_ids[:, inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        )[0]
        
        return generated_text.strip()
    
    def compare_responses(self, image_path, question):
        """Compare responses from both models"""
        

        print(f"Loading image: {image_path}")
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        print(f"Question: {question}")
        print("=" * 80)
        
       
        print("🔹 ORIGINAL MODEL RESPONSE:")
        try:
            original_response = self.generate_response(self.original_model, image, question)
            print(original_response)
        except Exception as e:
            print(f"Error with original model: {e}")
            original_response = "Error generating response"
        
        print("\n" + "=" * 80)
   
        print("🔸 FINE-TUNED MODEL RESPONSE:")
        try:
            finetuned_response = self.generate_response(self.finetuned_model, image, question)
            print(finetuned_response)
        except Exception as e:
            print(f"Error with fine-tuned model: {e}")
            finetuned_response = "Error generating response"
        
        print("=" * 80)
        
        return {
            'image_path': image_path,
            'question': question,
            'original_response': original_response,
            'finetuned_response': finetuned_response
        }
    
    def batch_compare(self, test_cases):
        """Run comparison on multiple test cases"""
        results = []
        
        for i, (image_path, question) in enumerate(test_cases, 1):
            print(f"\n{'='*20} TEST CASE {i}/{len(test_cases)} {'='*20}")
            result = self.compare_responses(image_path, question)
            results.append(result)
        
        return results

def load_sample_from_dataset():
    """Load a sample from the same dataset used in training"""
    from datasets import load_dataset
    
    print("Loading sample from training dataset...")
    ds = load_dataset("Agri-LLaVA-Anonymous/Agricultural_pests_and_diseases_instruction_tuning_data")
    

    import random
    sample_idx = random.randint(0, min(100, len(ds['train']) - 1))
    sample = ds['train'][sample_idx]
    
    print(f"Selected sample index: {sample_idx}")
    print(f"Image filename: {sample['image']}")
    

    human_question = None
    expected_answer = None
    
    for conv in sample['conversations']:
        if conv['from'] == 'human':
            human_question = conv['value'].replace('<image>', '').strip()
        elif conv['from'] == 'gpt':
            expected_answer = conv['value']
    
    image_path = os.path.join("/data/azfarm/siddhant/capOne-Hack/Img/Img", sample['image'])
    
    return {
        'image_path': image_path,
        'question': human_question,
        'expected_answer': expected_answer,
        'image_filename': sample['image']
    }

def main():
    adapter_path = "./SMOL-vlm-final" 
    base_model_id = "HuggingFaceTB/SmolVLM-Base"
    
    print("SmolVLM Model Comparison Tool")
    print("Comparing Original vs Fine-tuned Agricultural Model")
    print("Using sample from training dataset")
    print("=" * 60)
    
    try:
        sample_data = load_sample_from_dataset()
        
        print(f"Sample Image: {sample_data['image_filename']}")
        print(f"Question: {sample_data['question']}")
        print(f"Expected Answer: {sample_data['expected_answer'][:200]}...")
        print("=" * 60)
        
        if not os.path.exists(sample_data['image_path']):
            print(f"Image not found at: {sample_data['image_path']}")
            print("Please ensure the image directory path is correct.")
            return
        
        comparator = SmolVLMInferenceComparator(
            base_model_id=base_model_id,
            adapter_path=adapter_path
        )
        
        result = comparator.compare_responses(
            sample_data['image_path'], 
            sample_data['question']
        )
        
        with open("inference_comparison_results.txt", "w") as f:
            f.write("SmolVLM Model Comparison Results\n")
            f.write("=" * 60 + "\n")
            f.write(f"Sample Image: {sample_data['image_filename']}\n")
            f.write(f"Image Path: {sample_data['image_path']}\n")
            f.write(f"Question: {sample_data['question']}\n\n")
            
            f.write("EXPECTED ANSWER (from training data):\n")
            f.write("-" * 40 + "\n")
            f.write(sample_data['expected_answer'] + "\n\n")
            
            f.write("ORIGINAL MODEL RESPONSE:\n")
            f.write("-" * 40 + "\n")
            f.write(result['original_response'] + "\n\n")
            
            f.write("FINE-TUNED MODEL RESPONSE:\n")
            f.write("-" * 40 + "\n")
            f.write(result['finetuned_response'] + "\n\n")
            
            f.write("ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            f.write("Compare how well each model's response matches the expected answer.\n")
            f.write("The fine-tuned model should show better agricultural domain knowledge.\n")
            f.write("=" * 60 + "\n")
        
        print(f"\n✅ Results saved to: inference_comparison_results.txt")
        
        print(f"\n📋 QUICK COMPARISON:")
        print(f"Expected length: {len(sample_data['expected_answer'])} chars")
        print(f"Original response length: {len(result['original_response'])} chars")
        print(f"Fine-tuned response length: {len(result['finetuned_response'])} chars")
        
    except Exception as e:
        print(f"Error loading sample from dataset: {e}")
        print("\nFalling back to manual example...")
        
        example_image = "/data/azfarm/siddhant/capOne-Hack/Img/Img"  # Directory path
        if os.path.exists(example_image):
            image_files = [f for f in os.listdir(example_image) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if image_files:
                test_image = os.path.join(example_image, image_files[0])
                test_question = "What agricultural problem do you see in this image? Please identify any pests, diseases, or issues and provide treatment recommendations."
                
                comparator = SmolVLMInferenceComparator(
                    base_model_id=base_model_id,
                    adapter_path=adapter_path
                )
                
                result = comparator.compare_responses(test_image, test_question)
                print("✅ Fallback comparison completed!")
            else:
                print("No image files found in the directory.")
        else:
            print("Image directory not found. Please check the path.")
    
    print("\nComparison complete!")

if __name__ == "__main__":
    main()

def quick_inference_test(image_path, question, adapter_path="./SMOL-vlm-final"):
    """
    Quick function to test inference with your fine-tuned model
    """
    patch_idefics3_vision_embeddings()
    
    processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-Base")
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    base_model = Idefics3ForConditionalGeneration.from_pretrained(
        "HuggingFaceTB/SmolVLM-Base",
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()
    
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": question}
            ]
        }
    ]
    
    text = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=text, images=[image], return_tensors="pt")
    
    device = next(model.parameters()).device
    for key, value in inputs.items():
        if isinstance(value, torch.Tensor):
            inputs[key] = value.to(device)
    
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.1,
            do_sample=True,
            pad_token_id=processor.tokenizer.eos_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
        )
    
    response = processor.batch_decode(
        generated_ids[:, inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    )[0]
    
    print(f"Question: {question}")
    print(f"Response: {response.strip()}")
    
    return response.strip()

def test_specific_sample(sample_index=0, adapter_path="./SMOL-vlm-final"):
    """
    Test inference with a specific sample from the dataset by index
    """
    from datasets import load_dataset
    
    patch_idefics3_vision_embeddings()
    
    ds = load_dataset("Agri-LLaVA-Anonymous/Agricultural_pests_and_diseases_instruction_tuning_data")
    sample = ds['train'][sample_index]
    
    print(f"Testing with sample {sample_index}")
    print(f"Image: {sample['image']}")
    
    human_question = None
    expected_answer = None
    
    for conv in sample['conversations']:
        if conv['from'] == 'human':
            human_question = conv['value'].replace('<image>', '').strip()
        elif conv['from'] == 'gpt':
            expected_answer = conv['value']
    
    processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-Base")
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    base_model = Idefics3ForConditionalGeneration.from_pretrained(
        "HuggingFaceTB/SmolVLM-Base",
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()
    
    image_path = os.path.join("/data/azfarm/siddhant/capOne-Hack/Img/Img", sample['image'])
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": human_question}
            ]
        }
    ]
    
    text = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=text, images=[image], return_tensors="pt")
    
    device = next(model.parameters()).device
    for key, value in inputs.items():
        if isinstance(value, torch.Tensor):
            inputs[key] = value.to(device)
    
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.1,
            do_sample=True,
            pad_token_id=processor.tokenizer.eos_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
        )
    
    response = processor.batch_decode(
        generated_ids[:, inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    )[0]
    
    print("=" * 80)
    print(f"QUESTION: {human_question}")
    print("=" * 80)
    print("EXPECTED ANSWER:")
    print(expected_answer)
    print("=" * 80)
    print("FINE-TUNED MODEL RESPONSE:")
    print(response.strip())
    print("=" * 80)
    
    return {
        'question': human_question,
        'expected': expected_answer,
        'generated': response.strip(),
        'image_file': sample['image']
    }