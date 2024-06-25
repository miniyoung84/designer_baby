import pickle
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import pandas as pd

# Preprocess the data including removing character names and removing random characters
from datasets import load_dataset

dataset = load_dataset("NousResearch/CharacterCodex", split="train")
df = dataset.to_pandas()

def preprocess(character_name, text):
    if '(' in character_name:
        character1, character2 = character_name.split('(').replace(')', '')


df['description'] = df.apply(lambda x: x['description'].replace(x['character_name'], '[CHARACTER]'), axis=1)
# for num in range(0, len(df)):
#     character = df[num]['character_name']
#     #print(character in dataset[num]['description'])
#     #print('OOF ------- :' + dataset[num]['description'].replace(character, "[CHARACTER]"))
#     df[num]['description'] = df[num]['description'].replace(character, "[CHARACTER]")
#     df[num]['scenario'] = df[num]['scenario'].replace(character, "[CHARACTER]")
print(df['description'])
exit()
# Create the encoder and decoder and test the pieces for the best output
MAX_LENGTH = 600

SOS_token = "<"
EOS_token = ">"

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
                # Teacher forcing: Feed the target as the next input
                decoder_input = target_tensor[:, i].unsqueeze(1) # Teacher forcing
            else:
                # Without teacher forcing: use its own predictions as the next input
                _, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze(-1).detach()  # detach from history as input

        decoder_outputs = torch.cat(decoder_outputs, dim=1)
        decoder_outputs = F.log_softmax(decoder_outputs, dim=-1)
        return decoder_outputs, decoder_hidden, None # We return `None` for consistency in the training loop

    def forward_step(self, input, hidden):
        output = self.embedding(input)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.out(output)
        return output, hidden
# Run and evaluate the model for generating new characters
# Evaluation: #1 see if the loss goes down and if the parameters change in between runs
# #2 Eye test to see if what it generates makes any sense

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