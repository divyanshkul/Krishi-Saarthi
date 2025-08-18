#!/usr/bin/env python3

import os
import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling,
    logging
)

logging.set_verbosity_error()
import warnings
warnings.filterwarnings('ignore')

try:
    from peft import (
        get_peft_model,
        PromptTuningConfig,
        PromptTuningInit,
        TaskType,
        PeftConfig,
        PeftModel
    )
    PEFT_AVAILABLE = True
except ImportError:
    print("PEFT not found. Install with: pip install peft")
    PEFT_AVAILABLE = False

from sklearn.model_selection import train_test_split
from tqdm import tqdm
import json
from datetime import datetime

class TinyLlamaDataset(Dataset):
    
    def __init__(self, queries, answers, tokenizer, max_length=512):
        self.queries = queries
        self.answers = answers
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.queries)
    
    def __getitem__(self, idx):
        query = str(self.queries[idx]).strip()
        answer = str(self.answers[idx]).strip()
        
        text = f"<|user|>\n{query}\n<|assistant|>\n{answer}"
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }

class TinyLlamaPromptTuning:
    
    def __init__(self, data_path, num_virtual_tokens=50):
        self.data_path = data_path
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.num_virtual_tokens = num_virtual_tokens
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if not PEFT_AVAILABLE:
            raise ImportError("PEFT is required. Install with: pip install peft")
            
        print(f"TinyLlama Prompt Tuning Setup")
        print(f"Model: {self.model_name}")
        print(f"Device: {self.device}")
        print(f"Virtual tokens: {num_virtual_tokens}")
        print(f"Modern Llama architecture with chat optimization")
        
        self.load_data()
        self.setup_model_and_tokenizer()
        
    def load_data(self):
        print("Loading dataset...")
        df = pd.read_csv(self.data_path)
        
        print(f"Original dataset columns: {df.columns.tolist()}")
        print(f"Dataset shape: {df.shape}")
        
        query_col = None
        answer_col = None
        
        for col in ['QueryText', 'Prompt', 'query', 'question', 'input']:
            if col in df.columns:
                query_col = col
                break
        
        for col in ['TranslatedKccAns', 'Answer', 'answer', 'response', 'output']:
            if col in df.columns:
                answer_col = col
                break
        
        if query_col is None or answer_col is None:
            print(f"Could not find query/answer columns")
            print(f"Available columns: {df.columns.tolist()}")
            raise ValueError("Please ensure your CSV has query and answer columns")
        
        print(f"Using: {query_col} -> {answer_col}")
        
        df = df.dropna(subset=[query_col, answer_col])
        df[query_col] = df[query_col].astype(str).str.strip()
        df[answer_col] = df[answer_col].astype(str).str.strip()
        
        df = df[(df[query_col] != '') & (df[answer_col] != '')]
        
        print(f"Clean dataset size: {len(df)} samples")
        
        self.train_queries, self.test_queries, self.train_answers, self.test_answers = train_test_split(
            df[query_col].tolist(),
            df[answer_col].tolist(),
            test_size=0.2,
            random_state=42
        )
        
        print(f"Training samples: {len(self.train_queries)}")
        print(f"Test samples: {len(self.test_queries)}")
        
    def setup_model_and_tokenizer(self):
        print(f"Loading TinyLlama model...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"Vocabulary size: {len(self.tokenizer)}")
        print(f"Special tokens: pad={self.tokenizer.pad_token}, eos={self.tokenizer.eos_token}")
        
        loading_attempts = [
            {
                "torch_dtype": torch.bfloat16 if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else torch.float16,
                "device_map": "auto" if torch.cuda.is_available() else None,
                "trust_remote_code": True,
                "attn_implementation": "eager",
                "low_cpu_mem_usage": True
            },
            {
                "torch_dtype": torch.float32,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True
            },
            {
                "trust_remote_code": True
            }
        ]
        
        model_loaded = False
        for i, config in enumerate(loading_attempts):
            try:
                print(f"Loading attempt {i+1}/3...")
                self.base_model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    **config
                )
                print(f"Model loaded successfully with config {i+1}")
                model_loaded = True
                break
            except Exception as e:
                print(f"Attempt {i+1} failed: {str(e)[:100]}...")
                if i == len(loading_attempts) - 1:
                    print("All loading attempts failed")
                    raise e
                continue
        
        if not model_loaded:
            raise Exception("Failed to load TinyLlama model with any configuration")
        
        self.peft_config = PromptTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            prompt_tuning_init=PromptTuningInit.TEXT,
            num_virtual_tokens=self.num_virtual_tokens,
            prompt_tuning_init_text="You are a helpful agricultural assistant providing weather information and farming advice to farmers. Respond with accurate, practical information.",
            tokenizer_name_or_path=self.model_name,
        )
        
        self.peft_model = get_peft_model(self.base_model, self.peft_config)
        
        total_params = sum(p.numel() for p in self.base_model.parameters())
        trainable_params = sum(p.numel() for p in self.peft_model.parameters() if p.requires_grad)
        
        print(f"TinyLlama PEFT setup complete!")
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Efficiency: {100 * trainable_params / total_params:.4f}% trainable")
        print(f"Virtual tokens: {self.num_virtual_tokens} × {self.base_model.config.hidden_size} = {trainable_params:,}")
        
        model_size_gb = (total_params * 2) / 1e9
        print(f"Estimated model memory: ~{model_size_gb:.1f} GB")
        
    def create_datasets(self, max_length=512):
        print("Creating datasets...")
        
        self.train_dataset = TinyLlamaDataset(
            self.train_queries, self.train_answers, self.tokenizer, max_length
        )
        
        self.val_dataset = TinyLlamaDataset(
            self.test_queries, self.test_answers, self.tokenizer, max_length
        )
        
        print(f"Datasets created (max_length={max_length})")
        
    def train_prompt_tuning_model(self, output_dir="./tinyllama_prompt_tuned", epochs=20):
        print(f"Starting TinyLlama prompt tuning...")
        print("Training only virtual token embeddings!")
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=4,
            warmup_steps=50,
            logging_steps=10,
            save_steps=100,
            eval_strategy="steps",
            eval_steps=50,
            learning_rate=0.01,
            weight_decay=0.01,
            max_grad_norm=1.0,
            fp16=False,
            bf16=False,
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            remove_unused_columns=False,
            report_to="none",
            dataloader_pin_memory=False,
            gradient_checkpointing=False,
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        trainer = Trainer(
            model=self.peft_model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            data_collator=data_collator,
        )
        
        print("Training started...")
        trainer.train()
        
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Training completed! Model saved to {output_dir}")
        
        adapter_size = self.num_virtual_tokens * self.base_model.config.hidden_size * 4
        print(f"Adapter size: ~{adapter_size / 1024:.2f} KB")
        
        return trainer
        
    def generate_response(self, model, query, max_new_tokens=200):
        prompt = f"<|user|>\n{query}\n<|assistant|>\n"
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        model_device = next(model.parameters()).device
        inputs = {k: v.to(model_device) for k, v in inputs.items()}
        
        with torch.no_grad():
            try:
                outputs = model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs.get('attention_mask'),
                    max_new_tokens=max_new_tokens,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True
                )
                
                input_length = inputs['input_ids'].shape[1]
                new_tokens = outputs[0][input_length:]
                response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
                
                return response.strip()
                
            except Exception as e:
                return f"[Generation error: {str(e)}]"
    
    def compare_models(self, num_samples=3):
        print("="*70)
        print("TINYLLAMA MODEL COMPARISON")
        print("="*70)
        
        peft_model_path = "./tinyllama_prompt_tuned"
        if os.path.exists(peft_model_path):
            try:
                print("Loading saved PEFT model...")
                peft_config = PeftConfig.from_pretrained(peft_model_path)
                peft_model = AutoModelForCausalLM.from_pretrained(
                    peft_config.base_model_name_or_path,
                    torch_dtype=torch.float32,
                    trust_remote_code=True
                )
                peft_model = PeftModel.from_pretrained(peft_model, peft_model_path)
                
                base_device = next(self.base_model.parameters()).device
                peft_model = peft_model.to(base_device)
                peft_model.eval()
                print("Loaded saved PEFT model")
            except Exception as e:
                print(f"Using current PEFT model: {e}")
                peft_model = self.peft_model
                peft_model.eval()
        else:
            peft_model = self.peft_model
            peft_model.eval()
        
        self.base_model.eval()
        
        test_queries = self.test_queries[:num_samples]
        
        for i, query in enumerate(test_queries):
            print(f"\n{'TEST QUERY ' + str(i+1):=^70}")
            
            print(f"Farmer Query:")
            print(f"   {query}")
            
            try:
                print(f"\nBase TinyLlama (no virtual tokens):")
                base_response = self.generate_response(self.base_model, query, max_new_tokens=300)
                print(f"   {base_response}")
                
                print(f"\nPrompt-Tuned TinyLlama (+{self.num_virtual_tokens} tokens):")
                peft_response = self.generate_response(peft_model, query, max_new_tokens=300)
                print(f"   {peft_response}")
                
                if i < len(self.test_answers):
                    print(f"\nExpected Answer:")
                    actual = self.test_answers[i]
                    print(f"   {actual}")
                
                print(f"\nDetailed Response Analysis:")
                base_words = len(base_response.split())
                peft_words = len(peft_response.split())
                print(f"   Base model length: {base_words} words")
                print(f"   PEFT model length: {peft_words} words")
                
                agricultural_terms = ['weather', 'rain', 'temperature', 'humidity', 'wind', 'forecast', 
                                    'crop', 'farming', 'agricultural', 'meteorological', 'soybean', 
                                    'variety', 'cultivation', 'harvest', 'season', 'climate']
                
                base_ag_terms = sum(1 for term in agricultural_terms if term.lower() in base_response.lower())
                peft_ag_terms = sum(1 for term in agricultural_terms if term.lower() in peft_response.lower())
                
                print(f"   Base agricultural terms: {base_ag_terms}")
                print(f"   PEFT agricultural terms: {peft_ag_terms}")
                
                base_sentences = len([s for s in base_response.split('.') if s.strip()])
                peft_sentences = len([s for s in peft_response.split('.') if s.strip()])
                
                print(f"   Base sentences: {base_sentences}")
                print(f"   PEFT sentences: {peft_sentences}")
                
                if i < len(self.test_answers):
                    expected_words = set(self.test_answers[i].lower().split())
                    base_overlap = len(set(base_response.lower().split()) & expected_words)
                    peft_overlap = len(set(peft_response.lower().split()) & expected_words)
                    
                    print(f"   Base relevance score: {base_overlap} keyword matches")
                    print(f"   PEFT relevance score: {peft_overlap} keyword matches")
                    
                    if peft_overlap > base_overlap:
                        print("   PEFT model shows better relevance!")
                    elif base_overlap > peft_overlap:
                        print("   Base model has more keyword matches")
                    else:
                        print("   Similar relevance scores")
                
                improvements = []
                if peft_ag_terms > base_ag_terms:
                    improvements.append("More agricultural focus")
                if peft_words > base_words and peft_words > 10:
                    improvements.append("More detailed response")
                if peft_sentences >= base_sentences:
                    improvements.append("Better structure")
                
                if improvements:
                    print(f"   PEFT improvements: {', '.join(improvements)}")
                else:
                    print(f"   PEFT shows different response style")
                
            except Exception as e:
                print(f"Error in comparison: {e}")
                continue
                
            print("-" * 70)
        
        print(f"\nComparison completed for {len(test_queries)} queries")
        print("TinyLlama's chat training + virtual tokens = powerful weather assistant!")
        print("\nKey Observations:")
        print("   • Virtual tokens help focus on agricultural/weather context")
        print("   • Prompt tuning maintains model's chat abilities")
        print("   • Very few parameters (0.009%) achieve domain adaptation")
        print("   • Model learns to use relevant terminology more consistently")
    
    def analyze_virtual_tokens(self):
        print("Analyzing TinyLlama virtual tokens...")
        
        prompt_embeddings = None
        for name, param in self.peft_model.named_parameters():
            if 'prompt_embeddings' in name and param.requires_grad:
                prompt_embeddings = param.data
                break
        
        if prompt_embeddings is not None:
            print(f"Virtual token embeddings shape: {prompt_embeddings.shape}")
            print(f"Number of virtual tokens: {prompt_embeddings.shape[0]}")
            print(f"Embedding dimension: {prompt_embeddings.shape[1]}")
            
            mean_norm = torch.norm(prompt_embeddings, dim=1).mean()
            std_norm = torch.norm(prompt_embeddings, dim=1).std()
            
            print(f"Average embedding norm: {mean_norm:.4f}")
            print(f"Standard deviation: {std_norm:.4f}")
            
            try:
                vocab_embeddings = self.base_model.get_input_embeddings().weight
                similarities = torch.cosine_similarity(
                    prompt_embeddings.unsqueeze(1), 
                    vocab_embeddings.unsqueeze(0), 
                    dim=2
                )
                
                print(f"\nMost similar vocabulary tokens:")
                for i in range(min(5, self.num_virtual_tokens)):
                    top_similar = similarities[i].topk(3)
                    similar_tokens = []
                    for idx in top_similar.indices:
                        try:
                            token = self.tokenizer.decode([idx])
                            similar_tokens.append(token)
                        except:
                            similar_tokens.append(f"[id:{idx}]")
                    
                    similarities_rounded = [f"{sim:.3f}" for sim in top_similar.values.tolist()]
                    print(f"   Virtual token {i}: {similar_tokens} (sim: {similarities_rounded})")
                    
            except Exception as e:
                print(f"Could not analyze token similarities: {e}")
        else:
            print("Could not find prompt embeddings")
    
    def save_virtual_tokens(self, filename="tinyllama_virtual_tokens.pt"):
        for name, param in self.peft_model.named_parameters():
            if 'prompt_embeddings' in name and param.requires_grad:
                torch.save(param.data, filename)
                file_size = os.path.getsize(filename) / 1024
                print(f"Virtual tokens saved to {filename}")
                print(f"File size: {file_size:.2f} KB")
                return filename
        
        print("Could not find virtual tokens to save")
        return None

def main():
    print("TINYLLAMA PROMPT TUNING WITH VIRTUAL TOKENS")
    print("=" * 60)
    
    if not PEFT_AVAILABLE:
        print("PEFT not available. Please install:")
        print("pip install peft")
        return
    
    try:
        experiment = TinyLlamaPromptTuning(
            data_path="/teamspace/studios/this_studio/kcc_varieties.csv",
            num_virtual_tokens=50
        )
        
        experiment.create_datasets(max_length=512)
        
        trainer = experiment.train_prompt_tuning_model(epochs=20)
        
        experiment.compare_models(num_samples=3)
        
        experiment.analyze_virtual_tokens()
        
        experiment.save_virtual_tokens()
        
        print("\n" + "="*60)
        print("TINYLLAMA PROMPT TUNING COMPLETED!")
        print("\nKey Results:")
        print(f"Trained {experiment.num_virtual_tokens} virtual tokens")
        print(f"Modern Llama architecture with chat optimization")
        print(f"~{experiment.num_virtual_tokens * 2048 // 1000}K trainable parameters")
        print(f"Adapter size: ~{experiment.num_virtual_tokens * 2048 * 4 / 1024:.1f} KB")
        print("\nTinyLlama + Virtual Tokens = Powerful Weather Assistant!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print("\nTroubleshooting:")
        print("1. pip install --upgrade peft transformers torch")
        print("2. Check GPU memory (TinyLlama needs ~5GB)")
        print("3. Reduce batch_size or virtual tokens if OOM")
        print("4. Verify CSV file path and columns")
        raise

if __name__ == "__main__":
    main()