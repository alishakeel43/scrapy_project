# utils.py

def extract_phone_numbers(text):
    import re
    # Define regex patterns for phone numbers
    patterns = [
        r'\(\d{3}\) \d{3}-\d{4}',
        r'\(\d{3}\) \d{3}\.\d{4}',
        r'\d{3}-\d{3}-\d{4}',
        r'\d{3}\.\d{3}\.\d{4}',
        r'\d{3} \d{3} \d{4}',
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\+?\d{1,3} \d{1,4} \d{1,4} \d{4,10}'
    ]
    
    phone_numbers = []
    for pattern in patterns:
        phone_numbers.extend(re.findall(pattern, text))
    
    return phone_numbers

def extract_email(text):
    import re
    # Define regex pattern for email addresses
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.findall(email_pattern, text)
