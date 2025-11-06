#!/usr/bin/env python3
"""
Forex Scanner - Live Currency Exchange Rate Monitor
Fetches real-time exchange rates for multiple currency pairs using Alpha Vantage API
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import sys


class ForexScanner:
    """Forex Scanner for monitoring live currency exchange rates"""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        """
        Initialize the Forex Scanner

        Args:
            api_key: Alpha Vantage API key (get free key from alphavantage.co)
        """
        self.api_key = api_key
        self.session = requests.Session()

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """
        Fetch exchange rate for a currency pair

        Args:
            from_currency: Base currency code (e.g., 'USD')
            to_currency: Quote currency code (e.g., 'EUR')

        Returns:
            Dictionary with exchange rate data or None if error
        """
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'apikey': self.api_key
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'Realtime Currency Exchange Rate' in data:
                rate_data = data['Realtime Currency Exchange Rate']
                return {
                    'from': rate_data['1. From_Currency Code'],
                    'to': rate_data['3. To_Currency Code'],
                    'rate': float(rate_data['5. Exchange Rate']),
                    'bid': float(rate_data['8. Bid Price']),
                    'ask': float(rate_data['9. Ask Price']),
                    'last_updated': rate_data['6. Last Refreshed'],
                    'timezone': rate_data['7. Time Zone']
                }
            elif 'Note' in data:
                print(f"⚠️  API Rate Limit: {data['Note']}")
                return None
            elif 'Error Message' in data:
                print(f"❌ Error: {data['Error Message']}")
                return None
            else:
                print(f"❌ Unexpected response format")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"❌ Data parsing error: {e}")
            return None

    def scan_multiple_pairs(self, currency_pairs: List[tuple]) -> Dict:
        """
        Scan multiple currency pairs

        Args:
            currency_pairs: List of tuples [(from_curr, to_curr), ...]

        Returns:
            Dictionary with results for all pairs
        """
        results = {}

        for i, (from_curr, to_curr) in enumerate(currency_pairs):
            pair_name = f"{from_curr}/{to_curr}"
            print(f"📊 Fetching {pair_name}...", end=" ")

            rate_data = self.get_exchange_rate(from_curr, to_curr)

            if rate_data:
                results[pair_name] = rate_data
                print(f"✅ {rate_data['rate']:.4f}")
            else:
                results[pair_name] = None
                print("❌ Failed")

            # Rate limiting: Alpha Vantage free tier allows 5 API calls per minute
            # Wait between requests to avoid hitting the limit
            if i < len(currency_pairs) - 1:
                time.sleep(12)  # 12 seconds between requests = 5 per minute

        return results

    def display_results(self, results: Dict):
        """
        Display formatted results

        Args:
            results: Dictionary with exchange rate data
        """
        print("\n" + "="*70)
        print("FOREX SCANNER RESULTS".center(70))
        print("="*70)
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        if not results:
            print("No data available")
            return

        print(f"\n{'Currency Pair':<15} {'Rate':<12} {'Bid':<12} {'Ask':<12} {'Updated':<20}")
        print("-"*70)

        for pair_name, data in results.items():
            if data:
                print(f"{pair_name:<15} {data['rate']:<12.4f} {data['bid']:<12.4f} "
                      f"{data['ask']:<12.4f} {data['last_updated']:<20}")
            else:
                print(f"{pair_name:<15} {'N/A':<12} {'N/A':<12} {'N/A':<12} {'Failed':<20}")

        print("="*70)

    def continuous_scan(self, currency_pairs: List[tuple], interval: int = 300):
        """
        Continuously scan currency pairs at specified interval

        Args:
            currency_pairs: List of currency pair tuples
            interval: Seconds between scans (default 300 = 5 minutes)
        """
        print(f"🔄 Starting continuous scan (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                results = self.scan_multiple_pairs(currency_pairs)
                self.display_results(results)

                print(f"\n⏳ Waiting {interval} seconds until next scan...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 Forex Scanner stopped by user")


def main():
    """Main function to run the Forex Scanner"""

    # Welcome message
    print("="*70)
    print("FOREX SCANNER - Live Currency Exchange Rate Monitor".center(70))
    print("="*70)
    print("\nPowered by Alpha Vantage API (alphavantage.co)")
    print()

    # Get API key from user
    api_key = input("Enter your Alpha Vantage API key: ").strip()

    if not api_key:
        print("❌ API key is required. Get a free key at https://www.alphavantage.co/support/#api-key")
        sys.exit(1)

    # Initialize scanner
    scanner = ForexScanner(api_key)

    # Define currency pairs to monitor
    # Popular forex pairs
    currency_pairs = [
        ('EUR', 'USD'),  # Euro to US Dollar
        ('GBP', 'USD'),  # British Pound to US Dollar
        ('USD', 'JPY'),  # US Dollar to Japanese Yen
        ('USD', 'CHF'),  # US Dollar to Swiss Franc
        ('AUD', 'USD'),  # Australian Dollar to US Dollar
    ]

    print("\n📋 Currency pairs to monitor:")
    for from_curr, to_curr in currency_pairs:
        print(f"   • {from_curr}/{to_curr}")
    print()

    # Ask user for scan mode
    print("Select scan mode:")
    print("1. Single scan (one-time)")
    print("2. Continuous scan (every 5 minutes)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == '1':
        # Single scan
        print("\n🚀 Starting single scan...\n")
        results = scanner.scan_multiple_pairs(currency_pairs)
        scanner.display_results(results)

    elif choice == '2':
        # Continuous scan
        scanner.continuous_scan(currency_pairs, interval=300)

    else:
        print("❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
