"""Data tools for querying Excel files."""

import pandas as pd
from typing import Dict, List, Any

from src.config import DATA_DIR


class DataTools:
    """Tools for querying TelecomPlus data."""

    def __init__(self):
        self.data: Dict[str, pd.DataFrame] = {}
        self._load_data()

    def _load_data(self):
        """Load all Excel files into memory."""
        files = {
            "clients": "clients.xlsx",
            "forfaits": "forfaits.xlsx",
            "abonnements": "abonnements.xlsx",
            "consommation": "consommation.xlsx",
            "factures": "factures.xlsx",
            "tickets": "tickets_support.xlsx",
        }

        xlsx_dir = DATA_DIR / "xlsx"
        
        for name, filename in files.items():
            filepath = xlsx_dir / filename
            if filepath.exists():
                self.data[name] = pd.read_excel(filepath)
                print(f"Loaded {name}: {len(self.data[name])} rows")
            else:
                print(f"Warning: {filepath} not found")

    def query_clients(self, client_id: str = None, email: str = None) -> str:
        """Query client information."""
        df = self.data.get("clients", pd.DataFrame())
        if df.empty:
            return "No client data available."

        if client_id:
            # Convert to int if client_id is numeric
            try:
                client_id_int = int(client_id) if isinstance(client_id, str) and client_id.isdigit() else client_id
                result = df[df["client_id"] == client_id_int]
            except:
                result = df[df["client_id"] == client_id]
        elif email:
            result = df[df["email"] == email]
        else:
            return "Please provide client_id or email."

        if result.empty:
            return "Client not found."
        return result.to_string()

    def query_abonnements(self, client_id: str) -> str:
        """Query client subscriptions."""
        df = self.data.get("abonnements", pd.DataFrame())
        if df.empty:
            return "No subscription data available."

        try:
            client_id_int = int(client_id) if isinstance(client_id, str) and client_id.isdigit() else client_id
            result = df[df["client_id"] == client_id_int]
        except:
            result = df[df["client_id"] == client_id]
        if result.empty:
            return "No subscriptions found for this client."
        return result.to_string()

    def query_factures(self, client_id: str) -> str:
        """Query client bills."""
        df = self.data.get("factures", pd.DataFrame())
        if df.empty:
            return "No bill data available."

        try:
            client_id_int = int(client_id) if isinstance(client_id, str) and client_id.isdigit() else client_id
            result = df[df["client_id"] == client_id_int]
        except:
            result = df[df["client_id"] == client_id]
        if result.empty:
            return "No bills found for this client."
        return result.to_string()

    def query_tickets(self, client_id: str) -> str:
        """Query client support tickets."""
        df = self.data.get("tickets", pd.DataFrame())
        if df.empty:
            return "No ticket data available."

        try:
            client_id_int = int(client_id) if isinstance(client_id, str) and client_id.isdigit() else client_id
            result = df[df["client_id"] == client_id_int]
        except:
            result = df[df["client_id"] == client_id]
        if result.empty:
            return "No tickets found for this client."
        return result.to_string()

    def query_forfaits(self) -> str:
        """List available plans."""
        df = self.data.get("forfaits", pd.DataFrame())
        if df.empty:
            return "No plan data available."
        return df.to_string()

    def query_consommation(self, client_id: str) -> str:
        """Query client usage."""
        df = self.data.get("consommation", pd.DataFrame())
        if df.empty:
            return "No usage data available."

        try:
            client_id_int = int(client_id) if isinstance(client_id, str) and client_id.isdigit() else client_id
            result = df[df["client_id"] == client_id_int]
        except:
            result = df[df["client_id"] == client_id]
        if result.empty:
            return "No usage data found for this client."
        return result.to_string()


# Global instance
data_tools = DataTools()
