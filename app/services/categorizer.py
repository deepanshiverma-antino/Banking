from typing import Tuple

class TransactionCategorizer:
    def __init__(self):
        self.category_keywords = {
            'FoodAndDining': ['swiggy', 'zomato', 'restaurant', 'cafe', 'food', 'pizza', 'burger', 'dining', 'meal', 'breakfast', 'lunch', 'dinner'],
            'Travel': ['uber', 'ola', 'flight', 'bus', 'train', 'taxi', 'metro', 'airport', 'railway', 'booking', 'travel'],
            'Shopping': ['amazon', 'flipkart', 'store', 'mall', 'shopping', 'clothes', 'shoes', 'electronics', 'retail'],
            'Entertainment': ['netflix', 'spotify', 'cinema', 'movie', 'theatre', 'concert', 'gaming', 'subscription'],
            'Health': ['pharmacy', 'hospital', 'doctor', 'medical', 'health', 'medicine', 'clinic'],
            'Utilities': ['electricity', 'water', 'internet', 'phone', 'mobile', 'gas', 'bill', 'recharge'],
            'Rent': ['rent', 'landlord', 'lease', 'property', 'housing'],
        }
    
    def categorize(self, description: str, transaction_type: str) -> Tuple[str, float]:
        if transaction_type == 'investment':
            return 'Others', 1.0
        
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            if matches > 0:
                confidence = min(0.9, 0.3 + (matches * 0.2))
                return category, confidence
        
        # Fallback categorization based on transaction type
        if transaction_type == 'income':
            return 'Others', 0.5
        elif transaction_type == 'expense':
            return 'Others', 0.3
        else:
            return 'Others', 0.2
