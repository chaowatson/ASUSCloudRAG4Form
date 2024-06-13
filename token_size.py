from transformers import LlamaTokenizer

def getTokenizedSize(stringIn: str) -> int:
    tokenizer = LlamaTokenizer.from_pretrained(
        'ocisd4/llama_tokenizer_ext_zhtw',
        pad_token='<unk>',
        add_bos_token=True,
        add_eos_token=False
    )

    return len(tokenizer.tokenize(stringIn))
