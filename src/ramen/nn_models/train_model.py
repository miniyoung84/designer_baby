import pickle
import torch
import torch.nn as nn
from torch import optim
import torch.nn.Functional as F

# Preprocess the data including removing character names and removing random characters
# Create the encoder and decoder and test the pieces for the best output
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

pickle.dump(model, open("model.p", "wb"))