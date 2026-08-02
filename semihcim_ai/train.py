"""
semihcim4.0 Model Eğitimi
Açık kaynak model + LoRA fine-tuning
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrainConfig:
    # Model
    base_model: str = "unsloth/Llama-3.2-3B-Instruct"  # Hızlı ve iyi
    # Alternatifler:
    # "mistralai/Mistral-7B-Instruct-v0.3"
    # "microsoft/Phi-3-mini-4k-instruct"
    # "unsloth/Llama-3.2-1B-Instruct"  (daha küçük, daha hızlı)

    # Veri
    train_file: str = "data/processed/train.jsonl"
    val_file: str = "data/processed/val.jsonl"
    max_samples: Optional[int] = None  # None = tüm veri

    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: list = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])

    # Eğitim
    output_dir: str = "models/semihcim4.0"
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation: int = 4  # Effective batch = 4×4 = 16
    learning_rate: float = 2e-4
    max_seq_length: int = 2048
    warmup_ratio: float = 0.05
    weight_decay: float = 0.01
    save_steps: int = 200
    eval_steps: int = 100
    logging_steps: int = 10
    fp16: bool = True  # GPU ile hızlı eğitim
    gradient_checkpointing: bool = True

    # Sistem
    system_prompt: str = (
        "Sen semihcim4.0'sın. Elektrik/elektronik, yazılım, finans ve kripto "
        "konularında uzman, yardımsever ve güvenilir bir yapay zeka asistanısın. "
        "Her zaman doğru ve faydalı bilgi ver."
    )


def format_instruction(item: dict, system_prompt: str) -> str:
    """Llama-3 formatında mesaj oluştur."""
    instruction = item.get("instruction", "")
    inp = item.get("input", "")
    output = item.get("output", "")

    if inp:
        user_msg = f"{instruction}\n\n{inp}"
    else:
        user_msg = instruction

    return (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{system_prompt}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n"
        f"{user_msg}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n"
        f"{output}<|eot_id|>"
    )


def load_dataset(file_path: str, max_samples: Optional[int] = None) -> list[str]:
    """JSONL dosyasından eğitim verisi yükle."""
    samples = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                samples.append(item)
            except:
                continue
            if max_samples and len(samples) >= max_samples:
                break
    return samples


def train(config: TrainConfig):
    print("\n" + "="*60)
    print("  semihcim4.0 Model Eğitimi")
    print("="*60)

    # GPU kontrolü
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"  GPU: {gpu_name} ({gpu_mem:.1f} GB)")
        else:
            print("  ⚠️  GPU bulunamadı, CPU ile eğitim (YAVAŞ)")
    except ImportError:
        print("  PyTorch kurulu değil!")
        return

    # Unsloth (hızlı eğitim) veya standart transformers
    try:
        from unsloth import FastLanguageModel
        USE_UNSLOTH = True
        print("  ✓ Unsloth hızlandırması aktif")
    except ImportError:
        USE_UNSLOTH = False
        print("  ℹ️  Unsloth yok, standart transformers kullanılıyor")

    # Model yükle
    print(f"\n  Model yükleniyor: {config.base_model}")

    if USE_UNSLOTH:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=config.base_model,
            max_seq_length=config.max_seq_length,
            dtype=None,  # Auto detect
            load_in_4bit=True,  # 4-bit quantization
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=config.lora_r,
            target_modules=config.target_modules,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=42,
        )
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import get_peft_model, LoraConfig, TaskType

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(config.base_model)
        tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            quantization_config=bnb_config,
            device_map="auto",
        )
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            target_modules=config.target_modules,
            lora_dropout=config.lora_dropout,
            bias="none",
        )
        model = get_peft_model(model, lora_config)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  Eğitilebilir parametreler: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # Veri yükle
    print(f"\n  Veri yükleniyor: {config.train_file}")
    train_samples = load_dataset(config.train_file, config.max_samples)
    val_samples = load_dataset(config.val_file, max(100, len(train_samples)//20))
    print(f"  Train: {len(train_samples):,} örnek")
    print(f"  Val:   {len(val_samples):,} örnek")

    # Text formatla
    train_texts = [format_instruction(s, config.system_prompt) for s in train_samples]
    val_texts = [format_instruction(s, config.system_prompt) for s in val_samples]

    # HuggingFace Dataset
    from datasets import Dataset

    def tokenize(examples):
        tokens = tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.max_seq_length,
            padding="max_length",
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    train_dataset = Dataset.from_dict({"text": train_texts}).map(tokenize, batched=True)
    val_dataset = Dataset.from_dict({"text": val_texts}).map(tokenize, batched=True)

    # Trainer
    from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

    args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation,
        learning_rate=config.learning_rate,
        fp16=config.fp16 and device == "cuda",
        warmup_ratio=config.warmup_ratio,
        weight_decay=config.weight_decay,
        save_steps=config.save_steps,
        eval_steps=config.eval_steps,
        logging_steps=config.logging_steps,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        report_to="none",
        dataloader_num_workers=2,
        gradient_checkpointing=config.gradient_checkpointing,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    print("\n  Eğitim başlıyor...")
    trainer.train()

    # Modeli kaydet
    out_path = Path(config.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_path)
    tokenizer.save_pretrained(out_path)
    print(f"\n  ✅ Model kaydedildi: {config.output_dir}")

    # Config kaydet
    cfg_dict = {k: v for k, v in config.__dict__.items()
                if not isinstance(v, (list,)) or k == "target_modules"}
    with open(out_path / "semihcim_config.json", "w") as f:
        json.dump(cfg_dict, f, indent=2)


def chat_inference(model_path: str, prompt: str):
    """Eğitilmiş modelle sohbet et."""
    try:
        from unsloth import FastLanguageModel
        model, tokenizer = FastLanguageModel.from_pretrained(model_path)
        FastLanguageModel.for_inference(model)
    except ImportError:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path, device_map="auto", torch_dtype=torch.float16)

    system = ("Sen semihcim4.0'sın. Elektrik/elektronik, yazılım, finans ve kripto "
              "konularında uzman yapay zeka asistanısın.")
    formatted = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{system}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n"
        f"{prompt}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n"
    )

    import torch
    inputs = tokenizer(formatted, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1,
        )
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:],
                                skip_special_tokens=True)
    return response


if __name__ == "__main__":
    import sys
    base_dir = Path(__file__).parent

    if "--chat" in sys.argv:
        model_path = "models/semihcim4.0"
        print("semihcim4.0 yerel model ile sohbet (Ctrl+C çıkış)")
        while True:
            try:
                q = input("\nSen: ").strip()
                if not q:
                    continue
                print("semihcim4.0:", chat_inference(model_path, q))
            except KeyboardInterrupt:
                break
    else:
        os.chdir(base_dir)
        config = TrainConfig()
        train(config)
