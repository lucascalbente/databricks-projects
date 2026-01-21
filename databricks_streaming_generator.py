# Databricks notebook source
# MAGIC %md
# MAGIC # Banking Transactions - Streaming Data Generator
# MAGIC 
# MAGIC This notebook generates fake banking transaction data with intentional data quality issues.
# MAGIC It simulates a streaming data source by continuously creating transaction files.
# MAGIC 
# MAGIC **Purpose**: Generate RAW layer data for a banking pipeline with inconsistencies for data quality testing.
# MAGIC 
# MAGIC **Features**:
# MAGIC - Generates realistic banking transactions
# MAGIC - Introduces data quality issues (15% error rate by default)
# MAGIC - Supports JSON and JSONL formats
# MAGIC - Configurable batch size and interval
# MAGIC 
# MAGIC **Data Quality Issues Included**:
# MAGIC - Missing/null values
# MAGIC - Wrong data types
# MAGIC - Invalid categories
# MAGIC - Malformed IDs
# MAGIC - Negative amounts
# MAGIC - Future timestamps
# MAGIC - Empty strings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install Dependencies

# COMMAND ----------

# DBTITLE 1,Install Required Libraries
# MAGIC %pip install faker==26.0.0

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Import Libraries

# COMMAND ----------

# DBTITLE 1,Import Required Libraries
import json
import random
import time
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

from faker import Faker

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Transaction Generator Class

# COMMAND ----------

# DBTITLE 1,Define Transaction Generator
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
        """Generate transaction ID with possible inconsistencies."""
        if has_error and random.random() < 0.3:
            error_type = random.choice(['incomplete', 'numeric_only', 'duplicate_pattern', 'empty'])
            
            if error_type == 'incomplete':
                return str(uuid.uuid4())[:20]
            elif error_type == 'numeric_only':
                return str(random.randint(100000, 999999))
            elif error_type == 'duplicate_pattern':
                return 'TXN-' + str(random.randint(1, 100))
            else:
                return ''
        
        return str(uuid.uuid4())
    
    def _generate_user_id(self, user_id: Optional[int], has_error: bool):
        """Generate user ID with possible inconsistencies."""
        if user_id is not None:
            return user_id
        
        base_id = self.faker.random_int(min=1000, max=99999)
        
        if has_error and random.random() < 0.25:
            error_type = random.choice(['string', 'null', 'negative', 'zero'])
            
            if error_type == 'string':
                return f"USER_{base_id}"
            elif error_type == 'null':
                return None
            elif error_type == 'negative':
                return -base_id
            else:
                return 0
        
        return base_id
    
    def _generate_amount(self, has_error: bool = False):
        """Generate transaction amount with possible inconsistencies."""
        rand = self.faker.random_int(min=1, max=100)
        
        if rand <= 70:
            amount = self.faker.pyfloat(
                left_digits=3, right_digits=2, positive=True,
                min_value=10, max_value=500
            )
        elif rand <= 90:
            amount = self.faker.pyfloat(
                left_digits=4, right_digits=2, positive=True,
                min_value=500, max_value=2000
            )
        else:
            amount = self.faker.pyfloat(
                left_digits=5, right_digits=2, positive=True,
                min_value=2000, max_value=10000
            )
        
        clean_amount = Decimal(str(round(amount, 2)))
        
        if has_error and random.random() < 0.3:
            error_type = random.choice([
                'negative', 'zero', 'string_with_currency',
                'too_many_decimals', 'null', 'extremely_high'
            ])
            
            if error_type == 'negative':
                return float(-clean_amount)
            elif error_type == 'zero':
                return 0.0
            elif error_type == 'string_with_currency':
                return f"${clean_amount}"
            elif error_type == 'too_many_decimals':
                return float(round(amount, 5))
            elif error_type == 'null':
                return None
            else:
                return float(random.uniform(1000000, 9999999))
        
        return float(clean_amount)
    
    def _generate_category(self, has_error: bool) -> str:
        """Generate merchant category with possible inconsistencies."""
        if has_error and random.random() < 0.4:
            return random.choice(self.INVALID_CATEGORIES)
        
        return self.faker.random_element(self.MERCHANT_CATEGORIES)
    
    def _generate_timestamp(self, timestamp: Optional[datetime], has_error: bool):
        """Generate timestamp with possible inconsistencies."""
        base_timestamp = timestamp if timestamp else datetime.now()
        
        if has_error and random.random() < 0.2:
            error_type = random.choice(['string', 'null', 'future', 'wrong_format'])
            
            if error_type == 'string':
                return base_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            elif error_type == 'null':
                return None
            elif error_type == 'future':
                return '2099-12-31T23:59:59'
            else:
                return base_timestamp.strftime('%d/%m/%Y')
        
        return base_timestamp.isoformat()
    
    def _generate_transaction_type(self, has_error: bool) -> str:
        """Generate transaction type with possible inconsistencies."""
        if has_error and random.random() < 0.2:
            return random.choice(['UNKNOWN', 'N/A', '', 'other'])
        
        return self.faker.random_element(self.TRANSACTION_TYPES)
    
    def _generate_status(self, has_error: bool = False) -> str:
        """Generate transaction status with realistic weights."""
        if has_error and random.random() < 0.2:
            return random.choice(['UNKNOWN', '', 'error', 'N/A'])
        
        # 85% approved, 10% declined, 5% pending
        statuses = ['approved', 'declined', 'pending']
        weights = [0.85, 0.10, 0.05]
        return random.choices(statuses, weights=weights, k=1)[0]
    
    def _generate_currency(self, has_error: bool) -> str:
        """Generate currency code with possible inconsistencies."""
        if has_error and random.random() < 0.15:
            return random.choice(['XXX', '', 'N/A', '???', 'UNKNOWN'])
        
        return self.faker.random_element(self.CURRENCIES)
    
    def _generate_country(self, has_error: bool) -> str:
        """Generate transaction country with possible inconsistencies."""
        if has_error and random.random() < 0.15:
            return random.choice(['XX', '', 'N/A', 'UNKNOWN', '00'])
        
        # Majority of transactions in the US
        countries = ['US', 'GB', 'CA', 'BR']
        weights = [0.80, 0.10, 0.05, 0.05]
        return random.choices(countries, weights=weights, k=1)[0]
    
    def _generate_payment_method(self, has_error: bool) -> str:
        """Generate payment method with possible inconsistencies."""
        if has_error and random.random() < 0.2:
            return random.choice(['UNKNOWN', '', 'N/A', 'other', 'undefined'])
        
        return self.faker.random_element(self.PAYMENT_METHODS)
    
    def _generate_merchant_name(self, has_error: bool) -> str:
        """Generate merchant name with possible inconsistencies."""
        if has_error and random.random() < 0.2:
            error_type = random.choice(['empty', 'special_chars', 'too_long', 'numbers_only'])
            
            if error_type == 'empty':
                return ''
            elif error_type == 'special_chars':
                return '###@@@***'
            elif error_type == 'too_long':
                return self.faker.company() * 10
            else:
                return str(random.randint(10000, 99999))
        
        return self.faker.company()
    
    def _generate_description(self, has_error: bool) -> str:
        """Generate transaction description with possible inconsistencies."""
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

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Configuration Parameters

# COMMAND ----------

# DBTITLE 1,Set Configuration Parameters
# Configuration
OUTPUT_PATH = "/Volumes/workspace/databricks_projects/financial_data/"
BATCH_SIZE = 20  # Number of transactions per file
INTERVAL_SECONDS = 10  # Interval between batches
FILE_FORMAT = "json"  # Options: "json" or "jsonl"
ERROR_RATE = 0.15  # 15% of data with quality issues
MAX_BATCHES = 20  # Set to a number to limit batches, None for infinite

print(f"Configuration:")
print(f"  Output Path: {OUTPUT_PATH}")
print(f"  Batch Size: {BATCH_SIZE} transactions")
print(f"  Interval: {INTERVAL_SECONDS} seconds")
print(f"  File Format: {FILE_FORMAT}")
print(f"  Error Rate: {ERROR_RATE * 100}%")
print(f"  Max Batches: {MAX_BATCHES if MAX_BATCHES else 'Infinite'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Helper Functions

# COMMAND ----------

# DBTITLE 1,Define Helper Functions
def ensure_directory_exists(path: str) -> None:
    """
    Ensure the directory exists.
    
    Args:
        path: Directory path
    """
    # For Unity Catalog Volumes, the path should start with /Volumes/
    # No need to replace prefix for Volumes paths
    if path.startswith("/Volumes/"):
        dbutils.fs.mkdirs(path)
    else:
        # For DBFS paths, replace /dbfs with dbfs:
        dbutils.fs.mkdirs(path.replace("/dbfs", "dbfs:"))


def write_transactions_json(transactions: List[Dict], filepath: str) -> None:
    """
    Write transactions to a JSON file.
    
    Args:
        transactions: List of transaction dictionaries
        filepath: Output file path
    """
    with open(filepath, 'w') as f:
        json.dump(transactions, f, indent=2)


def write_transactions_jsonl(transactions: List[Dict], filepath: str) -> None:
    """
    Write transactions to a JSONL file (one JSON object per line).
    
    Args:
        transactions: List of transaction dictionaries
        filepath: Output file path
    """
    with open(filepath, 'a') as f:
        for transaction in transactions:
            json.dump(transaction, f)
            f.write('\n')


def generate_filename(batch_number: int, file_format: str) -> str:
    """
    Generate filename with timestamp and batch number.
    
    Args:
        batch_number: Batch sequence number
        file_format: File format (json or jsonl)
    
    Returns:
        Complete file path
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extension = 'jsonl' if file_format == 'jsonl' else 'json'
    filename = f'transactions_{timestamp}_batch_{batch_number:06d}.{extension}'
    return OUTPUT_PATH + filename

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Main Streaming Generator

# COMMAND ----------

# DBTITLE 1,Run Streaming Generator
# Initialize generator
generator = TransactionGenerator(error_rate=ERROR_RATE)

# Ensure output directory exists
ensure_directory_exists(OUTPUT_PATH)

print(f"\n{'='*60}")
print(f"Starting Streaming Transaction Generator")
print(f"{'='*60}\n")

batch_number = 0

try:
    while MAX_BATCHES is None or batch_number < MAX_BATCHES:
        batch_number += 1
        
        # Generate transactions
        transactions = generator.generate_transactions(count=BATCH_SIZE)
        
        # Generate filename
        filepath = generate_filename(batch_number, FILE_FORMAT)
        
        # Write transactions
        if FILE_FORMAT == 'jsonl':
            write_transactions_jsonl(transactions, filepath)
        else:
            write_transactions_json(transactions, filepath)
        
        # Log progress
        print(f"✓ Batch {batch_number:04d}: {BATCH_SIZE} transactions written to {filepath}")
        
        # Wait before next batch
        if MAX_BATCHES is None or batch_number < MAX_BATCHES:
            time.sleep(INTERVAL_SECONDS)
        
except KeyboardInterrupt:
    print(f"\n\n{'='*60}")
    print(f"Generator stopped by user")
    print(f"{'='*60}")
except Exception as e:
    print(f"\n\nError occurred: {str(e)}")
    raise
finally:
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total Batches: {batch_number}")
    print(f"  Total Transactions: {batch_number * BATCH_SIZE}")
    print(f"  Output Path: {OUTPUT_PATH}")
    print(f"{'='*60}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Verify Generated Files

# COMMAND ----------

# DBTITLE 1,List Generated Files
# List files in output directory
display_path = OUTPUT_PATH if OUTPUT_PATH.startswith("/Volumes/") else OUTPUT_PATH.replace("/dbfs", "dbfs:")
files = dbutils.fs.ls(display_path)

print(f"Generated Files ({len(files)} files):\n")
for file in files[-10:]:  # Show last 10 files
    print(f"  - {file.name} ({file.size} bytes)")

# COMMAND ----------

# DBTITLE 1,Sample Data Preview
# Read and display sample transactions from the latest file
if files:
    latest_file = max(files, key=lambda x: x.name)
    # For Volumes, use path directly; for DBFS, replace dbfs: with /dbfs
    if latest_file.path.startswith("/Volumes/"):
        latest_path = latest_file.path
    else:
        latest_path = latest_file.path.replace("dbfs:", "/dbfs")
    
    print(f"Sample data from: {latest_file.name}\n")
    
    with open(latest_path, 'r') as f:
        if FILE_FORMAT == 'jsonl':
            # Read first 3 lines
            for i in range(min(3, BATCH_SIZE)):
                line = f.readline()
                if line:
                    transaction = json.loads(line)
                    print(json.dumps(transaction, indent=2))
                    print("-" * 60)
        else:
            data = json.load(f)
            # Show first 3 transactions
            for transaction in data[:3]:
                print(json.dumps(transaction, indent=2))
                print("-" * 60)
else:
    print("No files generated yet.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Data Quality Statistics

# COMMAND ----------

# DBTITLE 1,Analyze Data Quality Issues
# Sample analysis of data quality issues
if files:
    sample_file = max(files, key=lambda x: x.name)
    # For Volumes, use path directly; for DBFS, replace dbfs: with /dbfs
    if sample_file.path.startswith("/Volumes/"):
        sample_path = sample_file.path
    else:
        sample_path = sample_file.path.replace("dbfs:", "/dbfs")
    
    with open(sample_path, 'r') as f:
        if FILE_FORMAT == 'jsonl':
            transactions = [json.loads(line) for line in f]
        else:
            transactions = json.load(f)
    
    total = len(transactions)
    issues = {
        'null_values': 0,
        'empty_strings': 0,
        'invalid_categories': 0,
        'negative_amounts': 0,
        'string_user_ids': 0
    }
    
    for t in transactions:
        # Check for nulls
        if any(v is None for v in t.values()):
            issues['null_values'] += 1
        
        # Check for empty strings
        if any(v == '' for v in t.values() if isinstance(v, str)):
            issues['empty_strings'] += 1
        
        # Check for invalid categories
        if t.get('merchant_category') in TransactionGenerator.INVALID_CATEGORIES:
            issues['invalid_categories'] += 1
        
        # Check for negative amounts
        if isinstance(t.get('amount'), (int, float)) and t.get('amount', 0) < 0:
            issues['negative_amounts'] += 1
        
        # Check for string user_ids
        if isinstance(t.get('user_id'), str):
            issues['string_user_ids'] += 1
    
    print(f"Data Quality Analysis ({sample_file.name}):\n")
    print(f"Total Transactions: {total}")
    print(f"\nData Quality Issues:")
    for issue, count in issues.items():
        percentage = (count / total) * 100
        print(f"  - {issue.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    total_issues = sum(issues.values())
    print(f"\nTotal Records with Issues: {total_issues} ({(total_issues/total)*100:.1f}%)")
