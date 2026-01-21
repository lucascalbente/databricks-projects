"""
Module for saving transactions in different formats.

This module implements strategies for persisting
banking transaction data.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List


class TransactionWriter(ABC):
    """Abstract class for writing transactions."""
    
    @abstractmethod
    def write(self, transaction: Dict, filepath: str) -> None:
        """
        Write a transaction to the specified destination.
        
        Args:
            transaction: Dictionary containing transaction data
            filepath: Destination file path
        """
        pass
    
    @abstractmethod
    def write_batch(self, transactions: List[Dict], filepath: str) -> None:
        """
        Write multiple transactions to the specified destination.
        
        Args:
            transactions: List of transactions
            filepath: Destination file path
        """
        pass


class JSONTransactionWriter(TransactionWriter):
    """Implementation for writing transactions in JSON format."""
    
    def __init__(self, indent: int = 2):
        """
        Initialize the JSON writer.
        
        Args:
            indent: JSON indentation level (default: 2)
        """
        self.indent = indent
    
    def write(self, transaction: Dict, filepath: str) -> None:
        """
        Write a transaction to a JSON file.
        
        Args:
            transaction: Dictionary containing transaction data
            filepath: Destination file path
        """
        self._ensure_directory_exists(filepath)
        
        # Convert special types to serializable
        serializable_transaction = self._make_serializable(transaction)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(serializable_transaction, file, indent=self.indent, ensure_ascii=False)
    
    def write_batch(self, transactions: List[Dict], filepath: str) -> None:
        """
        Write multiple transactions to a JSON file.
        
        Args:
            transactions: List of transactions
            filepath: Destination file path
        """
        self._ensure_directory_exists(filepath)
        
        # Convert special types to serializable
        serializable_transactions = [
            self._make_serializable(transaction)
            for transaction in transactions
        ]
        
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(serializable_transactions, file, indent=self.indent, ensure_ascii=False)
    
    @staticmethod
    def _make_serializable(transaction: Dict) -> Dict:
        """
        Convert special types to serializable types.
        
        Args:
            transaction: Original transaction
        
        Returns:
            Transaction with serializable types
        """
        serializable = {}
        for key, value in transaction.items():
            if isinstance(value, Decimal):
                serializable[key] = float(value)
            elif isinstance(value, datetime):
                serializable[key] = value.isoformat()
            else:
                serializable[key] = value
        return serializable
    
    @staticmethod
    def _ensure_directory_exists(filepath: str) -> None:
        """
        Ensure the file's directory exists.
        
        Args:
            filepath: File path
        """
        directory = os.path.dirname(filepath)
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)


class JSONLinesTransactionWriter(TransactionWriter):
    """Implementation for writing transactions in JSONL (JSON Lines) format."""
    
    def write(self, transaction: Dict, filepath: str) -> None:
        """
        Add a transaction to the JSONL file (append mode).
        
        Args:
            transaction: Dictionary containing transaction data
            filepath: Destination file path
        """
        self._ensure_directory_exists(filepath)
        
        serializable_transaction = self._make_serializable(transaction)
        
        with open(filepath, 'a', encoding='utf-8') as file:
            json.dump(serializable_transaction, file, ensure_ascii=False)
            file.write('\n')
    
    def write_batch(self, transactions: List[Dict], filepath: str) -> None:
        """
        Write multiple transactions to a JSONL file.
        
        Args:
            transactions: List of transactions
            filepath: Destination file path
        """
        self._ensure_directory_exists(filepath)
        
        with open(filepath, 'a', encoding='utf-8') as file:
            for transaction in transactions:
                serializable_transaction = self._make_serializable(transaction)
                json.dump(serializable_transaction, file, ensure_ascii=False)
                file.write('\n')
    
    @staticmethod
    def _make_serializable(transaction: Dict) -> Dict:
        """
        Convert special types to serializable types.
        
        Args:
            transaction: Original transaction
        
        Returns:
            Transaction with serializable types
        """
        serializable = {}
        for key, value in transaction.items():
            if isinstance(value, Decimal):
                serializable[key] = float(value)
            elif isinstance(value, datetime):
                serializable[key] = value.isoformat()
            else:
                serializable[key] = value
        return serializable
    
    @staticmethod
    def _ensure_directory_exists(filepath: str) -> None:
        """
        Ensure the file's directory exists.
        
        Args:
            filepath: File path
        """
        directory = os.path.dirname(filepath)
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)
