"""
Module responsible for generating fake banking transaction data.

This module implements a financial transaction generator using
the Faker library to simulate realistic banking transaction data.
"""

import random
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from faker import Faker


class TransactionGenerator:
    """
    Class responsible for generating fake banking transactions.
    
    This class uses the Factory design pattern to create
    transactions with realistic and varied data, including intentional
    inconsistencies for RAW data layer testing.
    """
    
    MERCHANT_CATEGORIES = [
        'electronics',
        'travel',
        'grocery',
        'restaurant',
        'pharmacy',
        'gas_station',
        'education',
        'healthcare',
        'entertainment',
        'clothing',
        'services',
        'utilities'
    ]
    
    # Invalid categories for data quality issues
    INVALID_CATEGORIES = [
        'UNKNOWN',
        'N/A',
        'undefined',
        '',
        'null',
        '???',
        'other'
    ]
    
    TRANSACTION_TYPES = ['debit', 'credit', 'transfer']
    TRANSACTION_STATUS = ['approved', 'declined', 'pending']
    PAYMENT_METHODS = [
        'credit_card',
        'debit_card',
        'bank_transfer',
        'cash',
        'digital_wallet',
        'check'
    ]
    CURRENCIES = ['USD', 'EUR', 'GBP', 'BRL']
    
    def __init__(
        self,
        locale: str = 'en_US',
        seed: Optional[int] = None,
        error_rate: float = 0.15
    ):
        """
        Initialize the transaction generator.
        
        Args:
            locale: Locale for data generation (default: en_US)
            seed: Seed for data reproducibility (optional)
            error_rate: Percentage of records with data quality issues (default: 15%)
        """
        self.faker = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
        self.error_rate = error_rate
    
    def generate_transaction(
        self,
        user_id: Optional[int] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Generate a single fake banking transaction.
        
        Args:
            user_id: User ID (randomly generated if not provided)
            timestamp: Transaction timestamp (uses current datetime if not provided)
        
        Returns:
            Dictionary containing transaction data with possible inconsistencies
        """
        # Introduce data quality issues based on error rate
        has_error = random.random() < self.error_rate
        
        transaction = {
            'transaction_id': self._generate_transaction_id(has_error),
            'user_id': self._generate_user_id(user_id, has_error),
            'amount': self._generate_amount(has_error),
            'merchant_category': self._generate_category(has_error),
            'timestamp': self._generate_timestamp(timestamp, has_error),
            'transaction_type': self._generate_transaction_type(has_error),
            'status': self._generate_status(has_error),
            'currency': self._generate_currency(has_error),
            'country': self._generate_country(has_error),
            'payment_method': self._generate_payment_method(has_error),
            'merchant_name': self._generate_merchant_name(has_error),
            'description': self._generate_description(has_error)
        }
        
        return transaction
    
    def generate_transactions(
        self,
        count: int,
        user_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate multiple fake banking transactions.
        
        Args:
            count: Number of transactions to generate
            user_id: User ID (optional, random if not provided)
        
        Returns:
            List of dictionaries containing transaction data
        """
        if count <= 0:
            raise ValueError("Transaction count must be greater than zero")
        
        return [
            self.generate_transaction(user_id=user_id)
            for _ in range(count)
        ]
    
    def _generate_transaction_id(self, has_error: bool) -> str:
        """
        Generate transaction ID with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Transaction ID (UUID or malformed)
        """
        if has_error and random.random() < 0.3:
            # Generate malformed IDs
            error_type = random.choice([
                'incomplete',
                'numeric_only',
                'duplicate_pattern',
                'empty'
            ])
            
            if error_type == 'incomplete':
                return str(uuid.uuid4())[:20]  # Truncated UUID
            elif error_type == 'numeric_only':
                return str(random.randint(100000, 999999))
            elif error_type == 'duplicate_pattern':
                return 'TXN-' + str(random.randint(1, 100))  # Likely to have duplicates
            else:
                return ''
        
        return str(uuid.uuid4())
    
    def _generate_user_id(self, user_id: Optional[int], has_error: bool) -> any:
        """
        Generate user ID with possible inconsistencies.
        
        Args:
            user_id: Provided user ID
            has_error: Whether to introduce data quality issues
        
        Returns:
            User ID (int, string, or null)
        """
        if user_id is not None:
            return user_id
        
        base_id = self.faker.random_int(min=1000, max=99999)
        
        if has_error and random.random() < 0.25:
            error_type = random.choice(['string', 'null', 'negative', 'zero'])
            
            if error_type == 'string':
                return f"USER_{base_id}"  # String instead of int
            elif error_type == 'null':
                return None
            elif error_type == 'negative':
                return -base_id
            else:
                return 0
        
        return base_id
    
    def _generate_amount(self, has_error: bool = False) -> any:
        """
        Generate transaction amount with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Transaction amount (Decimal, string, or invalid)
        """
        # Generate realistic amount distribution
        # 70% transactions between 10 and 500
        # 20% transactions between 500 and 2000
        # 10% transactions between 2000 and 10000
        rand = self.faker.random_int(min=1, max=100)
        
        if rand <= 70:
            amount = self.faker.pyfloat(
                left_digits=3,
                right_digits=2,
                positive=True,
                min_value=10,
                max_value=500
            )
        elif rand <= 90:
            amount = self.faker.pyfloat(
                left_digits=4,
                right_digits=2,
                positive=True,
                min_value=500,
                max_value=2000
            )
        else:
            amount = self.faker.pyfloat(
                left_digits=5,
                right_digits=2,
                positive=True,
                min_value=2000,
                max_value=10000
            )
        
        clean_amount = Decimal(str(round(amount, 2)))
        
        if has_error and random.random() < 0.3:
            error_type = random.choice([
                'negative',
                'zero',
                'string_with_currency',
                'too_many_decimals',
                'null',
                'extremely_high'
            ])
            
            if error_type == 'negative':
                return -clean_amount
            elif error_type == 'zero':
                return Decimal('0')
            elif error_type == 'string_with_currency':
                return f"${clean_amount}"
            elif error_type == 'too_many_decimals':
                return Decimal(str(round(amount, 5)))
            elif error_type == 'null':
                return None
            else:
                return Decimal(str(random.uniform(1000000, 9999999)))
        
        return clean_amount
    
    def _generate_category(self, has_error: bool) -> str:
        """
        Generate merchant category with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Merchant category (valid or invalid)
        """
        if has_error and random.random() < 0.4:
            return random.choice(self.INVALID_CATEGORIES)
        
        return self.faker.random_element(self.MERCHANT_CATEGORIES)
    
    def _generate_timestamp(self, timestamp: Optional[datetime], has_error: bool) -> any:
        """
        Generate timestamp with possible inconsistencies.
        
        Args:
            timestamp: Provided timestamp
            has_error: Whether to introduce data quality issues
        
        Returns:
            Timestamp (datetime, string, or null)
        """
        base_timestamp = timestamp if timestamp else datetime.now()
        
        if has_error and random.random() < 0.2:
            error_type = random.choice(['string', 'null', 'future', 'wrong_format'])
            
            if error_type == 'string':
                return base_timestamp.strftime('%Y-%m-%d %H:%M:%S')  # String instead of datetime
            elif error_type == 'null':
                return None
            elif error_type == 'future':
                return datetime(2099, 12, 31, 23, 59, 59)
            else:
                return base_timestamp.strftime('%d/%m/%Y')  # Wrong format
        
        return base_timestamp
    
    def _generate_transaction_type(self, has_error: bool) -> str:
        """
        Generate transaction type with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Transaction type
        """
        if has_error and random.random() < 0.2:
            return random.choice(['UNKNOWN', 'N/A', '', 'other'])
        
        return self.faker.random_element(self.TRANSACTION_TYPES)
    
    def _generate_status(self, has_error: bool = False) -> str:
        """
        Generate transaction status with realistic weights and possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Transaction status
        """
        if has_error and random.random() < 0.2:
            return random.choice(['UNKNOWN', '', 'error', 'N/A'])
        
        # 85% approved, 10% declined, 5% pending
        return self.faker.random_element({
            'approved': 0.85,
            'declined': 0.10,
            'pending': 0.05
        })
    
    def _generate_currency(self, has_error: bool) -> str:
        """
        Generate currency code with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Currency code
        """
        if has_error and random.random() < 0.15:
            return random.choice(['XXX', '', 'N/A', '???', 'UNKNOWN'])
        
        return self.faker.random_element(self.CURRENCIES)
    
    def _generate_country(self, has_error: bool) -> str:
        """
        Generate transaction country with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Country code
        """
        if has_error and random.random() < 0.15:
            return random.choice(['XX', '', 'N/A', 'UNKNOWN', '00'])
        
        # Majority of transactions in the US
        countries = {'US': 0.80, 'GB': 0.10, 'CA': 0.05, 'BR': 0.05}
        return self.faker.random_element(countries)
    
    def _generate_payment_method(self, has_error: bool) -> str:
        """
        Generate payment method with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Payment method
        """
        if has_error and random.random() < 0.2:
            return random.choice(['UNKNOWN', '', 'N/A', 'other', 'undefined'])
        
        return self.faker.random_element(self.PAYMENT_METHODS)
    
    def _generate_merchant_name(self, has_error: bool) -> str:
        """
        Generate merchant name with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Merchant name
        """
        if has_error and random.random() < 0.2:
            error_type = random.choice(['empty', 'special_chars', 'too_long', 'numbers_only'])
            
            if error_type == 'empty':
                return ''
            elif error_type == 'special_chars':
                return '###@@@***'
            elif error_type == 'too_long':
                return self.faker.company() * 10  # Extremely long name
            else:
                return str(random.randint(10000, 99999))
        
        return self.faker.company()
    
    def _generate_description(self, has_error: bool) -> str:
        """
        Generate transaction description with possible inconsistencies.
        
        Args:
            has_error: Whether to introduce data quality issues
        
        Returns:
            Transaction description
        """
        descriptions = [
            'Purchase completed',
            'Payment approved',
            'Transaction processed',
            'Cash purchase',
            'Installment payment',
            'Transfer completed',
            'Automatic debit',
            'Refund processed'
        ]
        
        if has_error and random.random() < 0.2:
            return random.choice(['', 'N/A', 'UNKNOWN', '???', 'NULL'])
        
        return self.faker.random_element(descriptions)
