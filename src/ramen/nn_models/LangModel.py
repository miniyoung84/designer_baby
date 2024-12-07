# This model is based on two tutorials: https://www.youtube.com/watch?v=kCc8FmEb1nY and https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import pandas as pd
import unicodedata
import re
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Preprocess the data including removing character names and removing random characters
from datasets import load_dataset

dataset = load_dataset("NousResearch/CharacterCodex", split="train")
df = dataset.to_pandas()

character_name_replacement = 'charname'

def preprocess(character_name, text):
    if '(' in character_name:
        free_cheese = character_name.split('(')
        character1 = free_cheese[0].strip()
        character2 = free_cheese[1].split(')')[0].strip()
        text = text.replace(character1, character_name_replacement)
        text = text.replace(character2, character_name_replacement)
    else:
        text = text.replace(character_name, character_name_replacement)
    return text

df['description'] = df.apply(lambda x: preprocess(x['character_name'], x['description']), axis=1)
df['scenario'] = df.apply(lambda x: preprocess(x['character_name'], x['scenario']), axis=1)

SOS_token = 0
EOS_token = 1

class WordBank:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1
    
    def getWord(self, index):
        return self.index2word[index]

    def getIndex(self, word):
        return self.word2index[word]

# Turn a Unicode string to plain ASCII, thanks to
# https://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

# Lowercase, trim, and remove non-letter characters
def normalizeString(s):
    s = unicodeToAscii(s.lower().strip())
    s = re.sub(r"([.!?])", r" \1", s)
    s = re.sub(r"[^a-zA-Z!?]+", r" ", s)
    return s.strip()

word_bank = WordBank('inputs')

for index, row in df.iterrows():
    word_bank.addSentence(normalizeString(row['description']))
    word_bank.addSentence(normalizeString(row['scenario']))

#print(word_bank.n_words)
#print(torch.cuda.is_available())


# hyperparameters
batch_size = 16 # how many independent sequences will we process in parallel?
block_size = 32 # what is the maximum context length for predictions?
max_iters = 5000
eval_interval = 100
learning_rate = 1e-3
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200
n_embd = 64
n_head = 4
n_layer = 4
dropout = 0.0
# ------------

torch.manual_seed(1337)

# here are all the unique characters that occur in this text
#chars = sorted(list(set(text)))
#vocab_size = len(chars)
vocab_size = word_bank.n_words
# create a mapping from characters to integers
#stoi = { ch:i for i,ch in enumerate(chars) }
#itos = { i:ch for i,ch in enumerate(chars) }
#encode = lambda s: [stoi[c] for c in s] # encoder: take a string, output a list of integers
#decode = lambda l: ''.join([itos[i] for i in l]) # decoder: take a list of integers, output a string

encode = lambda s: [word_bank.getIndex(c) for c in s.split()]
decode = lambda l: ' '.join([word_bank.getWord(i) for i in l])

n = int(0.9*len(df)) # first 90% will be train, rest val
train_data = df[:n]
val_data = df[n:]
n_train_samples = train_data.shape[0]
n_val_samples = val_data.shape[0]

# print(df.shape)
# print(train_data.shape)
# print(val_data.shape)

exit()

# ---- INSTEAD OF PUTTING ALL OF THE TEXT INTO ONE DATA VARIABLE, I NEED TO SETUP A FUNCTION THAT GETS THE SCENARIO AND DESCRIPTION AS IDXS
def encode_text(text):
    # Train and test splits
    data = torch.tensor(encode(text), dtype=torch.long)
    return data

# data loading
def get_batch(split):
    # generate a small batch of data of inputs x and targets y
    data = train_data if split == 'train' else val_data
    n_samples = data.shape[0]
    # ix = torch.randint(len(data) - block_size, (batch_size,))
    ix = torch.randint(n_samples, (batch_size,))
    cxt_pts = []
    for i in ix:
        # get a random point in the description to get the context from
        cxt_pts.append((i, random.randint(0, len(data[i]['description'])-1)))

    # x = torch.stack([data[i:i+block_size] for i in ix]) # CHANGE GET BATCH TO GET FROM A SET OF LISTED CHARACTERS
    x = torch.stack([data[i]['description'][0:ctx] for i, ctx in cxt_pts])
    # y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    y = torch.stack([data[i]['description'][1:ctx+1] for i, ctx in cxt_pts])
    x, y = x.to(device), y.to(device)
    return x, y

@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

class Head(nn.Module):
    """ one head of self-attention """

    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B,T,C = x.shape
        k = self.key(x)   # (B,T,C)
        q = self.query(x) # (B,T,C)
        # compute attention scores ("affinities")
        wei = q @ k.transpose(-2,-1) * C**-0.5 # (B, T, C) @ (B, C, T) -> (B, T, T)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf')) # (B, T, T)
        wei = F.softmax(wei, dim=-1) # (B, T, T)
        wei = self.dropout(wei)
        # perform the weighted aggregation of the values
        v = self.value(x) # (B,T,C)
        out = wei @ v # (B, T, T) @ (B, T, C) -> (B, T, C)
        return out

class MultiHeadAttention(nn.Module):
    """ multiple heads of self-attention in parallel """

    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.dropout(self.proj(out))
        return out

class FeedFoward(nn.Module):
    """ a simple linear layer followed by a non-linearity """

    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    """ Transformer block: communication followed by computation """

    def __init__(self, n_embd, n_head):
        # n_embd: embedding dimension, n_head: the number of heads we'd like
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedFoward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

class LanguageModel(nn.Module):

    def __init__(self):
        super().__init__()
        # each token directly reads off the logits for the next token from a lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd) # final layer norm
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape

        # idx and targets are both (B,T) tensor of integers
        tok_emb = self.token_embedding_table(idx) # (B,T,C)
        pos_emb = self.position_embedding_table(torch.arange(T, device=device)) # (T,C)
        x = tok_emb + pos_emb # (B,T,C)
        x = self.blocks(x) # (B,T,C)
        x = self.ln_f(x) # (B,T,C)
        logits = self.lm_head(x) # (B,T,vocab_size)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def generate(self, idx, max_new_tokens):
        # idx is (B, T) array of indices in the current context
        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_cond = idx[:, -block_size:]
            # get the predictions
            logits, loss = self(idx_cond)
            # focus only on the last time step
            logits = logits[:, -1, :] # becomes (B, C)
            # apply softmax to get probabilities
            probs = F.softmax(logits, dim=-1) # (B, C)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1) # (B, 1)
            if idx_next == EOS_token:
                return idx
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1) # (B, T+1)
        return idx

model = LanguageModel()
m = model.to(device)
# print the number of parameters in the model
print(sum(p.numel() for p in m.parameters())/1e6, 'M parameters')

# create a PyTorch optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

for iter in range(max_iters):

    # every once in a while evaluate the loss on train and val sets
    if iter % eval_interval == 0 or iter == max_iters - 1:
        losses = estimate_loss()
        print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

    # sample a batch of data
    xb, yb = get_batch('train')

    # evaluate the loss
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

# generate from the model
context = torch.zeros((1, 1), dtype=torch.long, device=device)
print(decode(m.generate(context, max_new_tokens=2000)[0].tolist()))