#from transformers import LlamaTokenizer
import tiktoken

'''
def getTokenizedSize(stringIn: str) -> int:
    tokenizer = LlamaTokenizer.from_pretrained(
        'ocisd4/llama_tokenizer_ext_zhtw',
        pad_token='<unk>',
        add_bos_token=True,
        add_eos_token=False
    )

    return len(tokenizer.tokenize(stringIn))
'''

def getTokenizedSize(string: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    #enc = tiktoken.encoding_for_model("gpt-4")
    tokens = enc.encode(string)

    return len(tokens)
