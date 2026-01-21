"""
Testes unitários para o módulo TransactionGenerator.

Este módulo contém testes para validar a geração de transações fake.
"""

import sys
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from transaction_generator import TransactionGenerator


class TestTransactionGenerator(unittest.TestCase):
    """Testes para a classe TransactionGenerator."""
    
    def setUp(self):
        """Configura o ambiente de teste."""
        self.generator = TransactionGenerator(seed=42)
    
    def test_initialization_with_locale(self):
        """Testa a inicialização com locale específico."""
        generator = TransactionGenerator(locale='en_US')
        self.assertIsNotNone(generator.faker)
    
    def test_initialization_with_seed(self):
        """Testa a inicialização com seed para reprodutibilidade."""
        generator1 = TransactionGenerator(seed=123)
        generator2 = TransactionGenerator(seed=123)
        
        transaction1 = generator1.generate_transaction()
        transaction2 = generator2.generate_transaction()
        
        self.assertEqual(transaction1['user_id'], transaction2['user_id'])
        self.assertEqual(transaction1['amount'], transaction2['amount'])
    
    def test_generate_transaction_returns_dict(self):
        """Testa se a transação retornada é um dicionário."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction, dict)
    
    def test_generate_transaction_has_required_fields(self):
        """Testa se a transação possui todos os campos obrigatórios."""
        transaction = self.generator.generate_transaction()
        
        required_fields = [
            'transaction_id',
            'user_id',
            'amount',
            'merchant_category',
            'timestamp'
        ]
        
        for field in required_fields:
            self.assertIn(field, transaction)
    
    def test_generate_transaction_has_additional_fields(self):
        """Testa se a transação possui campos adicionais."""
        transaction = self.generator.generate_transaction()
        
        additional_fields = [
            'transaction_type',
            'status',
            'currency',
            'country',
            'payment_method',
            'merchant_name',
            'description'
        ]
        
        for field in additional_fields:
            self.assertIn(field, transaction)
    
    def test_transaction_id_is_uuid(self):
        """Testa se o transaction_id é um UUID válido."""
        transaction = self.generator.generate_transaction()
        transaction_id = transaction['transaction_id']
        
        # Verifica formato UUID
        self.assertEqual(len(transaction_id), 36)
        self.assertEqual(transaction_id.count('-'), 4)
    
    def test_transaction_id_is_unique(self):
        """Testa se cada transação possui um UUID único."""
        transactions = self.generator.generate_transactions(count=100)
        transaction_ids = [t['transaction_id'] for t in transactions]
        
        # Verifica unicidade
        self.assertEqual(len(transaction_ids), len(set(transaction_ids)))
    
    def test_user_id_is_integer(self):
        """Testa se o user_id é um inteiro."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction['user_id'], int)
    
    def test_user_id_custom_value(self):
        """Testa se é possível fornecer um user_id customizado."""
        custom_user_id = 12345
        transaction = self.generator.generate_transaction(user_id=custom_user_id)
        self.assertEqual(transaction['user_id'], custom_user_id)
    
    def test_amount_is_decimal(self):
        """Testa se o amount é do tipo Decimal."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction['amount'], Decimal)
    
    def test_amount_is_positive(self):
        """Testa se o amount é sempre positivo."""
        transactions = self.generator.generate_transactions(count=50)
        for transaction in transactions:
            self.assertGreater(transaction['amount'], Decimal('0'))
    
    def test_amount_has_two_decimal_places(self):
        """Testa se o amount possui no máximo duas casas decimais."""
        transactions = self.generator.generate_transactions(count=50)
        for transaction in transactions:
            amount_str = str(transaction['amount'])
            if '.' in amount_str:
                decimal_places = len(amount_str.split('.')[1])
                self.assertLessEqual(decimal_places, 2)
    
    def test_merchant_category_is_valid(self):
        """Testa se a categoria do comerciante é válida."""
        transaction = self.generator.generate_transaction()
        self.assertIn(
            transaction['merchant_category'],
            TransactionGenerator.MERCHANT_CATEGORIES
        )
    
    def test_timestamp_is_datetime(self):
        """Testa se o timestamp é do tipo datetime."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction['timestamp'], datetime)
    
    def test_timestamp_custom_value(self):
        """Testa se é possível fornecer um timestamp customizado."""
        custom_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        transaction = self.generator.generate_transaction(timestamp=custom_timestamp)
        self.assertEqual(transaction['timestamp'], custom_timestamp)
    
    def test_transaction_type_is_valid(self):
        """Testa se o tipo de transação é válido."""
        transaction = self.generator.generate_transaction()
        self.assertIn(
            transaction['transaction_type'],
            TransactionGenerator.TRANSACTION_TYPES
        )
    
    def test_status_is_valid(self):
        """Testa se o status da transação é válido."""
        transaction = self.generator.generate_transaction()
        self.assertIn(
            transaction['status'],
            TransactionGenerator.TRANSACTION_STATUS
        )
    
    def test_currency_is_valid(self):
        """Testa se a moeda é válida."""
        transaction = self.generator.generate_transaction()
        self.assertIn(
            transaction['currency'],
            TransactionGenerator.CURRENCIES
        )
    
    def test_payment_method_is_valid(self):
        """Testa se o método de pagamento é válido."""
        transaction = self.generator.generate_transaction()
        self.assertIn(
            transaction['payment_method'],
            TransactionGenerator.PAYMENT_METHODS
        )
    
    def test_country_is_string(self):
        """Testa se o país é uma string."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction['country'], str)
    
    def test_merchant_name_is_string(self):
        """Testa se o nome do comerciante é uma string."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction['merchant_name'], str)
        self.assertGreater(len(transaction['merchant_name']), 0)
    
    def test_description_is_string(self):
        """Testa se a descrição é uma string."""
        transaction = self.generator.generate_transaction()
        self.assertIsInstance(transaction['description'], str)
        self.assertGreater(len(transaction['description']), 0)
    
    def test_generate_transactions_returns_list(self):
        """Testa se generate_transactions retorna uma lista."""
        transactions = self.generator.generate_transactions(count=5)
        self.assertIsInstance(transactions, list)
    
    def test_generate_transactions_correct_count(self):
        """Testa se o número correto de transações é gerado."""
        for count in [1, 5, 10, 50]:
            with self.subTest(count=count):
                transactions = self.generator.generate_transactions(count=count)
                self.assertEqual(len(transactions), count)
    
    def test_generate_transactions_with_user_id(self):
        """Testa geração de múltiplas transações com user_id fixo."""
        user_id = 99999
        transactions = self.generator.generate_transactions(count=10, user_id=user_id)
        
        for transaction in transactions:
            self.assertEqual(transaction['user_id'], user_id)
    
    def test_generate_transactions_invalid_count_raises_error(self):
        """Testa se count <= 0 levanta ValueError."""
        with self.assertRaises(ValueError):
            self.generator.generate_transactions(count=0)
        
        with self.assertRaises(ValueError):
            self.generator.generate_transactions(count=-5)
    
    def test_status_distribution_is_realistic(self):
        """Testa se a distribuição de status é realista (maioria aprovado)."""
        transactions = self.generator.generate_transactions(count=1000)
        statuses = [t['status'] for t in transactions]
        
        approved_count = statuses.count('aprovado')
        
        # Espera-se que pelo menos 70% sejam aprovados
        self.assertGreater(approved_count / len(transactions), 0.70)
    
    def test_amount_distribution(self):
        """Testa se os valores seguem uma distribuição realista."""
        transactions = self.generator.generate_transactions(count=1000)
        amounts = [float(t['amount']) for t in transactions]
        
        low_range = [a for a in amounts if 10 <= a <= 500]
        mid_range = [a for a in amounts if 500 < a <= 2000]
        high_range = [a for a in amounts if 2000 < a <= 10000]
        
        # Verifica que há uma boa distribuição
        self.assertGreater(len(low_range), len(mid_range))
        self.assertGreater(len(mid_range), len(high_range))


if __name__ == '__main__':
    unittest.main()
