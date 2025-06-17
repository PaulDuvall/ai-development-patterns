# Transaction Rejection with Clear Error Messaging

Examples for [^pm8a] in rejecting transactions exceeding limits with clear error messages:

**Example**: Transaction exceeds daily spending limit

<user>
User has spent $4,800 today and attempts to purchase an item for $500, but their daily limit is $5,000.
</user>

The system should:
- Calculate that the transaction would result in $5,300 total spending
- Reject the transaction immediately without attempting payment processing
- Display clear, specific error message: "Transaction declined. This purchase would exceed your daily spending limit of $5,000. You have spent $4,800 today and have $200 remaining."
- Suggest actionable next steps: "You can complete this purchase tomorrow or contact us to discuss increasing your limits."

**Example**: Single transaction exceeds maximum amount

<user>
User attempts to purchase a luxury item for $25,000, but their single transaction limit is $10,000.
</user>

The system should:
- Check the single transaction limit before other validations
- Reject immediately upon detecting the limit violation
- Display message: "Transaction declined. Single transactions are limited to $10,000. For purchases over this amount, please contact customer service at 1-800-SUPPORT."
- Provide alternative payment options if available (payment plans, bank transfers, etc.)

**Example**: Insufficient account balance

<user>
User attempts to make a $300 purchase, but their account balance is only $150.
</user>

The system should:
- Check available balance including any pending transactions
- Reject the transaction before contacting payment processor
- Display clear message: "Transaction declined. Insufficient funds. Your available balance is $150."
- Suggest solutions: "Add funds to your account or select a different payment method."

**Example**: Merchant category restriction

<user>
User with gambling restrictions on their account attempts to make a $100 purchase from an online casino.
</user>

The system should:
- Identify the merchant category as gambling/gaming
- Check user's account restrictions
- Reject the transaction based on category restrictions
- Display message: "Transaction declined. Purchases from gambling merchants are restricted on your account. Contact customer service to modify restrictions if needed."

**Example**: Geographic restriction violation

<user>
User traveling abroad attempts to make a purchase in a country where their card is blocked for security.
</user>

The system should:
- Detect the transaction location
- Check against user's approved geographic regions
- Reject the transaction due to location restrictions
- Display message: "Transaction declined for security reasons. International purchases from this location are currently blocked. Please contact us to authorize international transactions."

**Example**: Velocity check failure - too many transactions

<user>
User has made 15 transactions in the past hour and attempts another purchase, but the velocity limit is 10 transactions per hour.
</user>

The system should:
- Count recent transactions within the time window
- Reject the transaction due to velocity limits
- Display message: "Transaction declined. You have exceeded the maximum number of transactions allowed per hour (10). Please wait before making additional purchases."
- Indicate when they can try again: "You can make your next purchase after 2:30 PM."