"""
Model 3: Variational Autoencoder (VAE) Anomaly Detection

Advanced probabilistic anomaly detection using KL divergence
and reconstruction probability for anomaly scoring.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path

from backend.utils.config import MODELS_DIR


class CompressorVAE(nn.Module):
    def __init__(self, input_dim: int = 21, latent_dim: int = 6):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(64),
            nn.Linear(64, 32),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(32),
        )
        self.fc_mu = nn.Linear(32, latent_dim)
        self.fc_logvar = nn.Linear(32, latent_dim)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(32),
            nn.Linear(32, 64),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(64),
            nn.Linear(64, input_dim),
        )

    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstructed = self.decode(z)
        return reconstructed, mu, logvar


def vae_loss(reconstructed: torch.Tensor, original: torch.Tensor, mu: torch.Tensor, logvar: torch.Tensor, beta: float = 1.0) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    recon_loss = F.mse_loss(reconstructed, original, reduction="mean")
    kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
    total_loss = recon_loss + beta * kl_loss
    return total_loss, recon_loss, kl_loss


class VAEDetector:
    def __init__(self, input_dim: int = 21, latent_dim: int = 6, lr: float = 1e-3, beta: float = 1.0):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CompressorVAE(input_dim, latent_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.beta = beta
        self.threshold: float = 0.0
        self.train_history: list[dict] = []

    def fit(self, X: np.ndarray, epochs: int = 60, batch_size: int = 512, val_split: float = 0.1) -> dict:
        n_val = int(len(X) * val_split)
        X_train = torch.FloatTensor(X[n_val:]).to(self.device)
        X_val = torch.FloatTensor(X[:n_val]).to(self.device)

        dataset = torch.utils.data.TensorDataset(X_train)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model.train()
        for epoch in range(epochs):
            epoch_recon = 0.0
            epoch_kl = 0.0

            for (batch,) in loader:
                self.optimizer.zero_grad()
                reconstructed, mu, logvar = self.model(batch)
                total_loss, recon_loss, kl_loss = vae_loss(reconstructed, batch, mu, logvar, self.beta)
                total_loss.backward()
                self.optimizer.step()
                epoch_recon += recon_loss.item()
                epoch_kl += kl_loss.item()

            self.train_history.append({
                "recon_loss": epoch_recon / len(loader),
                "kl_loss": epoch_kl / len(loader),
            })

            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs} - Recon: {self.train_history[-1]['recon_loss']:.6f}, KL: {self.train_history[-1]['kl_loss']:.6f}")

        self.model.eval()
        with torch.no_grad():
            val_recon, val_mu, val_logvar = self.model(X_val)
            val_errors = F.mse_loss(val_recon, X_val, reduction="none").mean(dim=1).cpu().numpy()
            self.threshold = float(np.percentile(val_errors, 95))

        return {
            "final_recon_loss": self.train_history[-1]["recon_loss"],
            "final_kl_loss": self.train_history[-1]["kl_loss"],
            "threshold_95": self.threshold,
            "epochs": epochs,
        }

    def predict(self, X: np.ndarray, n_samples: int = 10) -> dict:
        self.model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)

        all_errors = []
        with torch.no_grad():
            for _ in range(n_samples):
                reconstructed, mu, logvar = self.model(X_tensor)
                errors = F.mse_loss(reconstructed, X_tensor, reduction="none").mean(dim=1).cpu().numpy()
                all_errors.append(errors)

        mean_errors = np.mean(all_errors, axis=0)
        error_uncertainty = np.std(all_errors, axis=0)
        is_anomaly = (mean_errors > self.threshold).astype(int)
        anomaly_probability = 1 - np.exp(-mean_errors / (self.threshold + 1e-10))
        anomaly_probability = np.clip(anomaly_probability, 0, 1)

        with torch.no_grad():
            mu, logvar = self.model.encode(X_tensor)

        return {
            "reconstruction_errors": mean_errors,
            "error_uncertainty": error_uncertainty,
            "anomaly_labels": is_anomaly,
            "anomaly_probability": anomaly_probability,
            "latent_mu": mu.cpu().numpy(),
            "latent_logvar": logvar.cpu().numpy(),
        }

    def save(self, path: Path | None = None):
        path = path or MODELS_DIR / "vae.pt"
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state": self.model.state_dict(),
            "threshold": self.threshold,
            "input_dim": self.model.input_dim,
            "latent_dim": self.model.latent_dim,
            "beta": self.beta,
            "train_history": self.train_history,
        }, path)

    @classmethod
    def load(cls, path: Path | None = None) -> "VAEDetector":
        path = path or MODELS_DIR / "vae.pt"
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        detector = cls(
            input_dim=checkpoint["input_dim"],
            latent_dim=checkpoint["latent_dim"],
            beta=checkpoint["beta"],
        )
        detector.model.load_state_dict(checkpoint["model_state"])
        detector.threshold = checkpoint["threshold"]
        detector.train_history = checkpoint["train_history"]
        detector.model.eval()
        return detector
