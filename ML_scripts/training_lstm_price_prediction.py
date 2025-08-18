import pandas as pd 
df = pd.read_csv("Sugarcane.csv")
len(df)
df_daily = df.drop_duplicates(subset='Reported Date', keep='first')
df_mp = df_daily[df_daily['State Name'] == 'Madhya Pradesh']
df_mp = df_mp.drop(['State Name', 'District Name', 'Market Name', 'Variety', 'Group', ], axis=1)
df_mp['Reported Date'] = range(1, len(df_mp) + 1)
price_columns = ['Min Price (Rs./Quintal)', 'Max Price (Rs./Quintal)', 'Modal Price (Rs./Quintal)']
df_mp['Min Price (Rs./Quintal)'] = df_mp[['Min Price (Rs./Quintal)', 'Modal Price (Rs./Quintal)', 'Max Price (Rs./Quintal)']].min(axis=1)
df_mp['Max Price (Rs./Quintal)'] = df_mp[['Min Price (Rs./Quintal)', 'Modal Price (Rs./Quintal)', 'Max Price (Rs./Quintal)']].max(axis=1)
print(f"Original shape: {df_daily.shape}")

df_clean = df_daily[price_columns].dropna()
print(f"After removing NaN: {df_clean.shape}")

df_clean = df_clean[(df_clean > 0).all(axis=1)]
print(f"After removing zero/negative prices: {df_clean.shape}")

print("\nCleaned data info:")
print(df_clean.describe())
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaled_prices = scaler.fit_transform(df_clean[price_columns])
import numpy as np

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i])
        y.append(data[i])
    return np.array(X), np.array(y)

SEQ_LENGTH = 30

X, y = create_sequences(scaled_prices, SEQ_LENGTH)
print(f"X shape: {X.shape}, y shape: {y.shape}")
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

print(f"Training samples: {X_train.shape}")
print(f"Testing samples: {X_test.shape}")
print(f"Features per sample: {X_train.shape[2]}")
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

X_train_tensor = torch.FloatTensor(X_train)
y_train_tensor = torch.FloatTensor(y_train)
X_test_tensor = torch.FloatTensor(X_test)
y_test_tensor = torch.FloatTensor(y_test)

print(f"X_train_tensor shape: {X_train_tensor.shape}")
print(f"y_train_tensor shape: {y_train_tensor.shape}")
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
class PriceLSTM(nn.Module):
    def __init__(self, input_size=3, hidden_size=50, num_layers=2, output_size=3):
        super(PriceLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(hidden_size, 25)
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(25, output_size)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        out, _ = self.lstm(x, (h0, c0))
        
        out = out[:, -1, :]
        
        out = self.fc1(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

model = PriceLSTM()
print(model)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
print(f"Training on: {device}")
def train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs=25):
    train_losses = []
    test_losses = []
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        model.eval()
        test_loss = 0.0
        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                test_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        avg_test_loss = test_loss / len(test_loader)
        
        train_losses.append(avg_train_loss)
        test_losses.append(avg_test_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.6f}, Test Loss: {avg_test_loss:.6f}')
    
    return train_losses, test_losses

print("Starting training...")
train_losses, test_losses = train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs=50)
model.eval()
predictions = []
actuals = []

with torch.no_grad():
    for batch_X, batch_y in test_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        pred = model(batch_X)
        predictions.append(pred.cpu().numpy())
        actuals.append(batch_y.cpu().numpy())

predictions = np.concatenate(predictions, axis=0)
actuals = np.concatenate(actuals, axis=0)

print(f"Predictions shape: {predictions.shape}")
print(f"Actuals shape: {actuals.shape}")
pred_prices = scaler.inverse_transform(predictions)
actual_prices = scaler.inverse_transform(actuals)

print("Sample predictions vs actuals (first 5):")
for i in range(5):
    print(f"Predicted: Min={pred_prices[i,0]:.2f}, Max={pred_prices[i,1]:.2f}, Modal={pred_prices[i,2]:.2f}")
    print(f"Actual:    Min={actual_prices[i,0]:.2f}, Max={actual_prices[i,1]:.2f}, Modal={actual_prices[i,2]:.2f}")
    print("---")
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

price_names = ['Min Price', 'Max Price', 'Modal Price']

for i, name in enumerate(price_names):
    mae = mean_absolute_error(actual_prices[:, i], pred_prices[:, i])
    rmse = np.sqrt(mean_squared_error(actual_prices[:, i], pred_prices[:, i]))
    r2 = r2_score(actual_prices[:, i], pred_prices[:, i])
    
    print(f"{name}:")
    print(f"  MAE: {mae:.2f} Rs/Quintal")
    print(f"  RMSE: {rmse:.2f} Rs/Quintal") 
    print(f"  R²: {r2:.4f}")
    print()
import joblib

def save_model_and_scaler(model, scaler, model_path='mandi_lstm_sugarcane_model.pth', scaler_path='price_scaler_sugarcane.pkl'):
    """Save the trained model and scaler"""
    torch.save(model.state_dict(), model_path)
    
    joblib.dump(scaler, scaler_path)
    
    print(f"Model saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")

save_model_and_scaler(model, scaler)
import numpy as np

np.save('scaled_prices_sugarcane.npy', scaled_prices)
print(" Scaled prices saved!")

df_clean.to_csv('cleaned_price_data_sugarcane.csv', index=False)
print(" Cleaned DataFrame saved!")