"""
Model 4: LSTM Forecasting Residual Anomaly Detection

Predicts future sensor behavior and flags deviations as anomalies.
Uses sliding window sequences for time-series forecasting.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

from backend.utils.config import MODELS_DIR

SEQUENCE_LENGTH = 24
FORECAST_HORIZON = 1


class LSTMForecaster(nn.Module):
    def __init__(self, input_dim: int = 21, hidden_dim: int = 64, num_layers: int = 2, output_dim: int = 21):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.output_dim = output_dim

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        return self.fc(last_hidden)


def create_sequences(data: np.ndarray, seq_length: int = SEQUENCE_LENGTH) -> tuple[np.ndarray, np.ndarray]:
    sequences = []
    targets = []
    for i in range(len(data) - seq_length):
        sequences.append(data[i:i + seq_length])
        targets.append(data[i + seq_length])
    return np.array(sequences), np.array(targets)


class LSTMResidualDetector:
    def __init__(self, input_dim: int = 21, hidden_dim: int = 64, num_layers: int = 2, lr: float = 1e-3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = LSTMForecaster(input_dim, hidden_dim, num_layers, input_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss(reduction="none")
        self.threshold: float = 0.0
        self.train_losses: list[float] = []
        self.input_dim = input_dim

    def fit(self, X: np.ndarray, epochs: int = 30, batch_size: int = 256, val_split: float = 0.1) -> dict:
        sequences, targets = create_sequences(X)
        n_val = int(len(sequences) * val_split)

        X_train = torch.FloatTensor(sequences[n_val:]).to(self.device)
        y_train = torch.FloatTensor(targets[n_val:]).to(self.device)
        X_val = torch.FloatTensor(sequences[:n_val]).to(self.device)
        y_val = torch.FloatTensor(targets[:n_val]).to(self.device)

        dataset = torch.utils.data.TensorDataset(X_train, y_train)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_x, batch_y in loader:
                self.optimizer.zero_grad()
                predictions = self.model(batch_x)
                loss = self.criterion(predictions, batch_y).mean()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                epoch_loss += loss.item()

            avg_loss = epoch_loss / len(loader)
            self.train_losses.append(avg_loss)

            if (epoch + 1) % 5 == 0:
                print(f"  Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f}")

        self.model.eval()
        with torch.no_grad():
            val_pred = self.model(X_val)
            val_residuals = self.criterion(val_pred, y_val).mean(dim=1).cpu().numpy()
            self.threshold = float(np.percentile(val_residuals, 95))

        return {
            "final_train_loss": self.train_losses[-1],
            "threshold_95": self.threshold,
            "val_mean_residual": float(val_residuals.mean()),
            "n_sequences": len(sequences),
            "epochs": epochs,
        }

    def predict(self, X: np.ndarray) -> dict:
        self.model.eval()
        sequences, actuals = create_sequences(X)
        seq_tensor = torch.FloatTensor(sequences).to(self.device)

        with torch.no_grad():
            predictions = self.model(seq_tensor).cpu().numpy()

        residuals = np.mean((predictions - actuals) ** 2, axis=1)
        per_feature_residuals = (predictions - actuals) ** 2
        is_anomaly = (residuals > self.threshold).astype(int)
        normalized_scores = residuals / (self.threshold + 1e-10)

        return {
            "residuals": residuals,
            "anomaly_labels": is_anomaly,
            "anomaly_scores": normalized_scores,
            "predictions": predictions,
            "actuals": actuals,
            "per_feature_residuals": per_feature_residuals,
        }

    def save(self, path: Path | None = None):
        path = path or MODELS_DIR / "lstm_forecaster.pt"
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state": self.model.state_dict(),
            "threshold": self.threshold,
            "input_dim": self.input_dim,
            "train_losses": self.train_losses,
        }, path)

    @classmethod
    def load(cls, path: Path | None = None) -> "LSTMResidualDetector":
        path = path or MODELS_DIR / "lstm_forecaster.pt"
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        detector = cls(input_dim=checkpoint["input_dim"])
        detector.model.load_state_dict(checkpoint["model_state"])
        detector.threshold = checkpoint["threshold"]
        detector.train_losses = checkpoint["train_losses"]
        detector.model.eval()
        return detector
