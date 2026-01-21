"""
Main script for continuous generation of fake banking transactions.

This script simulates data streaming by creating transaction files
at regular intervals, ideal for data pipeline testing.
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from transaction_generator import TransactionGenerator
from transaction_writer import JSONTransactionWriter, JSONLinesTransactionWriter


class StreamingTransactionSimulator:
    """
    Class responsible for simulating streaming banking transactions.
    
    This class continuously generates transactions and persists them to files,
    simulating a real-time data flow.
    """
    
    def __init__(
        self,
        output_dir: str,
        interval_seconds: int = 5,
        transactions_per_batch: int = 10,
        file_format: str = 'json',
        use_single_file: bool = False,
        error_rate: float = 0.15
    ):
        """
        Initialize the streaming simulator.
        
        Args:
            output_dir: Directory where files will be saved
            interval_seconds: Interval between generations (in seconds)
            transactions_per_batch: Number of transactions per batch
            file_format: File format ('json' or 'jsonl')
            use_single_file: If True, uses a single file (only for JSONL)
            error_rate: Percentage of records with data quality issues
        """
        self.output_dir = Path(output_dir)
        self.interval_seconds = interval_seconds
        self.transactions_per_batch = transactions_per_batch
        self.file_format = file_format.lower()
        self.use_single_file = use_single_file
        
        self.generator = TransactionGenerator(error_rate=error_rate)
        self.writer = self._get_writer()
        self.logger = self._setup_logger()
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_writer(self):
        """
        Return appropriate writer based on chosen format.
        
        Returns:
            Writer instance
        """
        if self.file_format == 'jsonl':
            return JSONLinesTransactionWriter()
        else:
            return JSONTransactionWriter()
    
    @staticmethod
    def _setup_logger() -> logging.Logger:
        """
        Configure application logger.
        
        Returns:
            Configured logger
        """
        logger = logging.getLogger('TransactionSimulator')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def _generate_filename(self, batch_number: int) -> str:
        """
        Generate filename based on format and timestamp.
        
        Args:
            batch_number: Batch number
        
        Returns:
            File name
        """
        if self.use_single_file and self.file_format == 'jsonl':
            filename = 'transactions.jsonl'
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            extension = 'jsonl' if self.file_format == 'jsonl' else 'json'
            filename = f'transactions_{timestamp}_batch_{batch_number:06d}.{extension}'
        
        return str(self.output_dir / filename)
    
    def run(self, max_batches: Optional[int] = None) -> None:
        """
        Execute the streaming simulator.
        
        Args:
            max_batches: Maximum number of batches (None for infinite execution)
        """
        self.logger.info("Starting streaming transaction simulator")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Interval: {self.interval_seconds} seconds")
        self.logger.info(f"Transactions per batch: {self.transactions_per_batch}")
        self.logger.info(f"Format: {self.file_format}")
        
        batch_number = 0
        
        try:
            while max_batches is None or batch_number < max_batches:
                batch_number += 1
                
                # Generate transactions
                transactions = self.generator.generate_transactions(
                    count=self.transactions_per_batch
                )
                
                # Save transactions
                filename = self._generate_filename(batch_number)
                
                if self.file_format == 'jsonl':
                    self.writer.write_batch(transactions, filename)
                else:
                    self.writer.write_batch(transactions, filename)
                
                self.logger.info(
                    f"Batch {batch_number}: {self.transactions_per_batch} "
                    f"transactions saved to {filename}"
                )
                
                # Wait before next batch
                if max_batches is None or batch_number < max_batches:
                    time.sleep(self.interval_seconds)
        
        except KeyboardInterrupt:
            self.logger.info("\nSimulation interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during simulation: {str(e)}", exc_info=True)
            raise
        finally:
            self.logger.info(f"Total batches generated: {batch_number}")


def main():
    """Main script function."""
    parser = argparse.ArgumentParser(
        description='Banking transaction streaming simulator'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/transactions',
        help='Output directory for files (default: data/transactions)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Interval between batches in seconds (default: 5)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of transactions per batch (default: 10)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'jsonl'],
        default='json',
        help='File format: json or jsonl (default: json)'
    )
    
    parser.add_argument(
        '--single-file',
        action='store_true',
        help='Use single file (only for jsonl format)'
    )
    
    parser.add_argument(
        '--max-batches',
        type=int,
        default=None,
        help='Maximum number of batches (default: infinite)'
    )
    
    parser.add_argument(
        '--error-rate',
        type=float,
        default=0.15,
        help='Data quality issue rate (default: 0.15 = 15%%)'
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.single_file and args.format != 'jsonl':
        print("Error: --single-file can only be used with --format jsonl")
        sys.exit(1)
    
    # Create and run simulator
    simulator = StreamingTransactionSimulator(
        output_dir=args.output_dir,
        interval_seconds=args.interval,
        transactions_per_batch=args.batch_size,
        file_format=args.format,
        use_single_file=args.single_file,
        error_rate=args.error_rate
    )
    
    simulator.run(max_batches=args.max_batches)


if __name__ == '__main__':
    main()
