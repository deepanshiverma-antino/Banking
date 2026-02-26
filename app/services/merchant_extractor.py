import re
from typing import Optional

class MerchantExtractor:
    def __init__(self):
        self.patterns_to_remove = [
            r'\d+',  # numbers
            r'[A-Z]{2,}\d{2,}',  # reference codes like TXN12345
            r'[A-Z0-9]{10,}',  # long alphanumeric codes
            r'\bREF\b\d*',  # reference patterns
            r'\bID\b\d*',  # ID patterns
            r'\bTXN\b\d*',  # transaction patterns
            r'\s+',  # multiple spaces
        ]
    
    def extract_merchant(self, description: str) -> str:
        if not description:
            return "Unknown"
        
        cleaned = description.upper()
        
        # Remove unwanted patterns
        for pattern in self.patterns_to_remove:
            cleaned = re.sub(pattern, ' ', cleaned)
        
        # Remove extra spaces and strip
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Common merchant name patterns
        merchant_keywords = [
            'SWIGGY', 'ZOMATO', 'UBER', 'OLA', 'AMAZON', 'FLIPKART', 
            'NETFLIX', 'SPOTIFY', 'PAYTM', 'PHONEPE', 'GPAY',
            'BIGBASKET', 'GROFERS', 'DMART', 'RELIANCE', 'TATA',
            'STARBUCKS', 'DOMINOS', 'PIZZA', 'KFC', 'MCDONALDS'
        ]
        
        for keyword in merchant_keywords:
            if keyword in cleaned:
                return keyword.title()
        
        # Extract first meaningful words (max 3 words)
        words = [word for word in cleaned.split() if len(word) > 2]
        if words:
            return ' '.join(words[:3]).title()
        
        return cleaned[:20].title() if cleaned else "Unknown"
