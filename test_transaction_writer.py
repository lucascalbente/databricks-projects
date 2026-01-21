"""
Testes unitários para os módulos de escrita de transações.

Este módulo contém testes para validar a persistência de transações.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from transaction_writer import JSONTransactionWriter, JSONLinesTransactionWriter


class TestJSONTransactionWriter(unittest.TestCase):
    """Testes para a classe JSONTransactionWriter."""
    
    def setUp(self):
        """Configura o ambiente de teste."""
        self.writer = JSONTransactionWriter()
        self.temp_dir = tempfile.mkdtemp()
        
        self.sample_transaction = {
            'transaction_id': '123e4567-e89b-12d3-a456-426614174000',
            'user_id': 12345,
            'amount': Decimal('150.50'),
            'merchant_category': 'eletrônicos',
            'timestamp': datetime(2024, 1, 15, 10, 30, 0)
        }
    
    def tearDown(self):
        """Limpa o ambiente de teste."""
        # Remove arquivos temporários
        for file in Path(self.temp_dir).glob('*'):
            file.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_write_single_transaction(self):
        """Testa a escrita de uma única transação."""
        filepath = os.path.join(self.temp_dir, 'transaction.json')
        self.writer.write(self.sample_transaction, filepath)
        
        # Verifica se o arquivo foi criado
        self.assertTrue(os.path.exists(filepath))
        
        # Verifica o conteúdo
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['transaction_id'], self.sample_transaction['transaction_id'])
        self.assertEqual(data['user_id'], self.sample_transaction['user_id'])
        self.assertEqual(data['amount'], float(self.sample_transaction['amount']))
    
    def test_write_creates_directory_if_not_exists(self):
        """Testa se o diretório é criado automaticamente."""
        filepath = os.path.join(self.temp_dir, 'subdir', 'transaction.json')
        self.writer.write(self.sample_transaction, filepath)
        
        self.assertTrue(os.path.exists(filepath))
    
    def test_write_batch_transactions(self):
        """Testa a escrita de múltiplas transações."""
        transactions = [
            {
                'transaction_id': f'id-{i}',
                'user_id': i,
                'amount': Decimal('100.00'),
                'merchant_category': 'mercado',
                'timestamp': datetime.now()
            }
            for i in range(5)
        ]
        
        filepath = os.path.join(self.temp_dir, 'transactions.json')
        self.writer.write_batch(transactions, filepath)
        
        # Verifica se o arquivo foi criado
        self.assertTrue(os.path.exists(filepath))
        
        # Verifica o conteúdo
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]['transaction_id'], 'id-0')
        self.assertEqual(data[4]['transaction_id'], 'id-4')
    
    def test_decimal_serialization(self):
        """Testa se Decimal é corretamente serializado para float."""
        filepath = os.path.join(self.temp_dir, 'transaction.json')
        self.writer.write(self.sample_transaction, filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIsInstance(data['amount'], float)
    
    def test_datetime_serialization(self):
        """Testa se datetime é corretamente serializado para ISO format."""
        filepath = os.path.join(self.temp_dir, 'transaction.json')
        self.writer.write(self.sample_transaction, filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIsInstance(data['timestamp'], str)
        # Verifica se está no formato ISO
        datetime.fromisoformat(data['timestamp'])


class TestJSONLinesTransactionWriter(unittest.TestCase):
    """Testes para a classe JSONLinesTransactionWriter."""
    
    def setUp(self):
        """Configura o ambiente de teste."""
        self.writer = JSONLinesTransactionWriter()
        self.temp_dir = tempfile.mkdtemp()
        
        self.sample_transaction = {
            'transaction_id': '123e4567-e89b-12d3-a456-426614174000',
            'user_id': 12345,
            'amount': Decimal('150.50'),
            'merchant_category': 'eletrônicos',
            'timestamp': datetime(2024, 1, 15, 10, 30, 0)
        }
    
    def tearDown(self):
        """Limpa o ambiente de teste."""
        # Remove arquivos temporários
        for file in Path(self.temp_dir).glob('*'):
            file.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_write_single_transaction(self):
        """Testa a escrita de uma única transação em JSONL."""
        filepath = os.path.join(self.temp_dir, 'transactions.jsonl')
        self.writer.write(self.sample_transaction, filepath)
        
        # Verifica se o arquivo foi criado
        self.assertTrue(os.path.exists(filepath))
        
        # Verifica o conteúdo
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 1)
        
        data = json.loads(lines[0])
        self.assertEqual(data['transaction_id'], self.sample_transaction['transaction_id'])
    
    def test_write_appends_to_file(self):
        """Testa se write adiciona ao arquivo existente (append)."""
        filepath = os.path.join(self.temp_dir, 'transactions.jsonl')
        
        # Primeira escrita
        self.writer.write(self.sample_transaction, filepath)
        
        # Segunda escrita
        transaction2 = self.sample_transaction.copy()
        transaction2['transaction_id'] = 'different-id'
        self.writer.write(transaction2, filepath)
        
        # Verifica se há duas linhas
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
    
    def test_write_batch_transactions(self):
        """Testa a escrita de múltiplas transações em JSONL."""
        transactions = [
            {
                'transaction_id': f'id-{i}',
                'user_id': i,
                'amount': Decimal('100.00'),
                'merchant_category': 'mercado',
                'timestamp': datetime.now()
            }
            for i in range(5)
        ]
        
        filepath = os.path.join(self.temp_dir, 'transactions.jsonl')
        self.writer.write_batch(transactions, filepath)
        
        # Verifica se o arquivo foi criado
        self.assertTrue(os.path.exists(filepath))
        
        # Verifica o conteúdo
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 5)
        
        # Verifica primeira e última transação
        first = json.loads(lines[0])
        last = json.loads(lines[4])
        
        self.assertEqual(first['transaction_id'], 'id-0')
        self.assertEqual(last['transaction_id'], 'id-4')
    
    def test_each_line_is_valid_json(self):
        """Testa se cada linha é um JSON válido."""
        transactions = [
            {
                'transaction_id': f'id-{i}',
                'user_id': i,
                'amount': Decimal('100.00'),
                'merchant_category': 'mercado',
                'timestamp': datetime.now()
            }
            for i in range(3)
        ]
        
        filepath = os.path.join(self.temp_dir, 'transactions.jsonl')
        self.writer.write_batch(transactions, filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                # Não deve lançar exceção
                json.loads(line)
    
    def test_creates_directory_if_not_exists(self):
        """Testa se o diretório é criado automaticamente."""
        filepath = os.path.join(self.temp_dir, 'subdir', 'transactions.jsonl')
        self.writer.write(self.sample_transaction, filepath)
        
        self.assertTrue(os.path.exists(filepath))


if __name__ == '__main__':
    unittest.main()
