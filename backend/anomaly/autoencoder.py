"""
Model 2: Autoencoder Anomaly Detection (PyTorch)

Detects anomalies through reconstruction error.
Normal data reconstructs well; anomalous data has high error.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

from backend.utils.config import MODELS_DIR


class CompressorAutoencoder(nn.Module):
    def __init__(self, input_dim: int = 21, latent_dim: int = 8):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Linear(32, latent_dim),
            nn.ReLU(),
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, input_dim),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent


class AutoencoderDetector:
    def __init__(self, input_dim: int = 21, latent_dim: int = 8, lr: float = 1e-3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CompressorAutoencoder(input_dim, latent_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss(reduction="none")
        self.threshold: float = 0.0
        self.train_losses: list[float] = []

    def fit(self, X: np.ndarray, epochs: int = 50, batch_size: int = 512, val_split: float = 0.1) -> dict:
        n_val = int(len(X) * val_split)
        X_train = torch.FloatTensor(X[n_val:]).to(self.device)
        X_val = torch.FloatTensor(X[:n_val]).to(self.device)

        dataset = torch.utils.data.TensorDataset(X_train)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0.0
            for (batch,) in loader:
                self.optimizer.zero_grad()
                reconstructed, _ = self.model(batch)
                loss = self.criterion(reconstructed, batch).mean()
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()

            avg_loss = epoch_loss / len(loader)
            self.train_losses.append(avg_loss)

            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f}")

        self.model.eval()
        with torch.no_grad():
            val_recon, _ = self.model(X_val)
            val_errors = self.criterion(val_recon, X_val).mean(dim=1).cpu().numpy()
            self.threshold = float(np.percentile(val_errors, 95))

        return {
            "final_train_loss": self.train_losses[-1],
            "threshold_95": self.threshold,
            "val_mean_error": float(val_errors.mean()),
            "epochs": epochs,
        }

    def predict(self, X: np.ndarray) -> dict:
        self.model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)

        with torch.no_grad():
            reconstructed, latent = self.model(X_tensor)
            errors = self.criterion(reconstructed, X_tensor).mean(dim=1).cpu().numpy()
            per_feature_error = self.criterion(reconstructed, X_tensor).cpu().numpy()

        is_anomaly = (errors > self.threshold).astype(int)
        normalized_scores = errors / (self.threshold + 1e-10)

        return {
            "reconstruction_errors": errors,
            "anomaly_labels": is_anomaly,
            "anomaly_scores": normalized_scores,
            "latent_representations": latent.cpu().numpy(),
            "per_feature_errors": per_feature_error,
        }

    def save(self, path: Path | None = None):
        path = path or MODELS_DIR / "autoencoder.pt"
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state": self.model.state_dict(),
            "threshold": self.threshold,
            "input_dim": self.model.input_dim,
            "latent_dim": self.model.latent_dim,
            "train_losses": self.train_losses,
        }, path)

    @classmethod
    def load(cls, path: Path | None = None) -> "AutoencoderDetector":
        path = path or MODELS_DIR / "autoencoder.pt"
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        detector = cls(input_dim=checkpoint["input_dim"], latent_dim=checkpoint["latent_dim"])
        detector.model.load_state_dict(checkpoint["model_state"])
        detector.threshold = checkpoint["threshold"]
        detector.train_losses = checkpoint["train_losses"]
        detector.model.eval()
        return detector
