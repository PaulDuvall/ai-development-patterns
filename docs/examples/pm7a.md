# Transaction Amount Validation

Examples for [^pm7a] in validating transaction amounts against account limits:

**Example**: User attempts standard purchase within limits

<user>
User with a $5,000 daily spending limit attempts to purchase an item for $150.
</user>

The system should:
- Check the user's current daily spending total
- Verify the new transaction would not exceed the $5,000 daily limit
- Allow the transaction to proceed if within limits
- Update the running total of daily spending after successful payment

**Example**: User attempts purchase that would exceed daily limit

<user>
User has already spent $4,900 today and tries to make a $200 purchase, which would exceed their $5,000 daily limit.
</user>

The system should:
- Calculate that $4,900 + $200 = $5,100 exceeds the $5,000 limit
- Reject the transaction before attempting payment processing
- Display clear message: "This transaction would exceed your daily spending limit of $5,000. You have $100 remaining today."
- Suggest alternative actions like splitting the purchase or waiting until tomorrow

**Example**: New user with unverified account attempting large purchase

<user>
User who registered yesterday with basic verification attempts to purchase an item for $2,500, but unverified accounts have a $500 transaction limit.
</user>

The system should:
- Check the user's account verification status
- Apply the appropriate limit based on verification level ($500 for unverified)
- Reject the transaction with explanation
- Display message: "Complete account verification to increase your transaction limits"
- Provide link to verification process

**Example**: Business account with higher limits

<user>
Business account user with a $50,000 daily limit attempts to purchase equipment for $15,000.
</user>

The system should:
- Apply the business account limits instead of personal account limits
- Verify the transaction is within the $50,000 daily business limit
- Allow the transaction to proceed
- Apply any additional business account validation rules (approval workflows, etc.)

**Example**: Multiple small transactions approaching limit

<user>
User makes several small purchases throughout the day: $500, $800, $1,200, $1,000, and now attempts a $600 purchase. Their daily limit is $5,000.
</user>

The system should:
- Sum all previous transactions: $500 + $800 + $1,200 + $1,000 = $3,500
- Check if new $600 transaction would exceed limit: $3,500 + $600 = $4,100
- Allow the transaction since $4,100 < $5,000
- Update their running total to $4,100 with $900 remaining

**Example**: International transaction with different limits

<user>
User attempts to make a $3,000 purchase from an international merchant, but their international transaction limit is $1,000 per day.
</user>

The system should:
- Identify the merchant as international based on location/merchant category
- Apply the international transaction limit ($1,000) instead of domestic limit
- Reject the transaction for exceeding international limits
- Display message: "International transactions are limited to $1,000 per day for security reasons"
- Offer option to contact customer service for temporary limit increase