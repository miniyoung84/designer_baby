import pickle
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import pandas as pd

# Used model is the Google Gemma model that can be found here https://www.kaggle.com/m/3301
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("cattoroboto/gemma-2-9b-CharacterCodex-qlora")
model = AutoModelForCausalLM.from_pretrained(
    "cattoroboto/gemma-2-9b-CharacterCodex-qlora",
    device_map="auto",
)

input_text = "Create a character with the name Teresa Walker"
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
'''
# Work on this script is based on this tutorial: https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Preprocess the data including removing character names and removing random characters
from datasets import load_dataset

dataset = load_dataset("NousResearch/CharacterCodex", split="train")
df = dataset.to_pandas()

def preprocess(character_name, text):
    if '(' in character_name:
        free_cheese = character_name.split('(')
        character1 = free_cheese[0].strip()
        character2 = free_cheese[1].split(')')[0].strip()
        text = text.replace(character1, '[CHARACTER]')
        text = text.replace(character2, '[CHARACTER]')
    else:
        text = text.replace(character_name, '[CHARACTER]')
    return text

df['description'] = df.apply(lambda x: preprocess(x['character_name'], x['description']), axis=1)
df['scenario'] = df.apply(lambda x: preprocess(x['character_name'], x['scenario']), axis=1)

# Create the encoder and decoder and test the pieces for the best output
MAX_LENGTH = 600

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

word_bank = WordBank('characters')
for character in df:
    word_bank.addSentence(normalizeString(character['description']))

class EncoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size, dropout_p=0.1):
        super(EncoderRNN, self).__init__()
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.dropout = nn.Dropout(dropout_p)

    def forward(self, input):
        embedded = self.dropout(self.embedding(input))
        output, hidden = self.gru(embedded)
        return output, hidden

class DecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size):
        super(DecoderRNN, self).__init__()
        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.out = nn.Linear(hidden_size, output_size)

    def forward(self, encoder_outputs, encoder_hidden, target_tensor=None):
        batch_size = encoder_outputs.size(0)
        decoder_input = torch.empty(batch_size, 1, dtype=torch.long, device=device).fill_(SOS_token)
        decoder_hidden = encoder_hidden
        decoder_outputs = []

        for i in range(MAX_LENGTH):
            decoder_output, decoder_hidden  = self.forward_step(decoder_input, decoder_hidden)
            decoder_outputs.append(decoder_output)

            if target_tensor is not None:
                decoder_input = target_tensor[:, i].unsqueeze(1)
            else:
                _, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze(-1).detach()

        decoder_outputs = torch.cat(decoder_outputs, dim=1)
        decoder_outputs = F.log_softmax(decoder_outputs, dim=-1)
        return decoder_outputs, decoder_hidden, None

    def forward_step(self, input, hidden):
        output = self.embedding(input)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.out(output)
        return output, hidden
# Run and evaluate the model for generating new characters
# Evaluation: #1 see if the loss goes down and if the parameters change in between runs
# #2 Eye test to see if what it generates makes any sense

hidden_size = 128
encoder = EncoderRNN(input_lang.n_words, hidden_size).to(device)
decoder = DecoderRNN(hidden_size, output_lang.n_words).to(device)

loss_total = 0

encoder_optimizer = optim.Adam(encoder.parameters(), lr=learning_rate)
decoder_optimizer = optim.Adam(decoder.parameters(), lr=learning_rate)
criterion = nn.NLLLoss()

for epoch in range(1, epochs + 1):
    total_loss = 0
    for data in dataloader:
        input_tensor, target_tensor = data

        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        encoder_outputs, encoder_hidden = encoder(input_tensor)
        decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden, target_tensor)

        loss = criterion(
            decoder_outputs.view(-1, decoder_outputs.size(-1)),
            target_tensor.view(-1)
        )
        loss.backward()

        encoder_optimizer.step()
        decoder_optimizer.step()

        total_loss += loss.item()

    loss = total_loss / len(dataloader)
    loss_total += loss

import matplotlib.pyplot as plt
plt.plot(loss_total)

pickle.dump(model, open("model.p", "wb"))
'''