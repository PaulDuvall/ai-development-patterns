# Email Format Validation

Examples for [^au1a] in email format validation per RFC 5322:

**Example**: User enters standard email address

<user>
User creates a new account and enters their email address as "john.smith@company.com" in the registration form.
</user>

The system should:
- Accept the email address as valid
- Convert it to lowercase for consistency: "john.smith@company.com"
- Store the normalized version in the database
- Proceed with account creation

**Example**: User enters email with uppercase letters

<user>
User enters their email as "Sarah.Johnson@UNIVERSITY.EDU" during login.
</user>

The system should:
- Accept the email as valid since RFC 5322 allows this format
- Normalize it to lowercase: "sarah.johnson@university.edu"
- Use the normalized version for all database lookups
- Successfully find their existing account if it exists

**Example**: User enters email with plus sign (email aliasing)

<user>
User signs up using "user+newsletters@gmail.com" to track where emails come from.
</user>

The system should:
- Accept the email as valid (plus signs are allowed in the local part)
- Preserve the full email address including the plus sign
- Treat this as a unique email address
- Allow account creation even if "user@gmail.com" already exists

**Example**: User enters invalid email format

<user>
User types "plainaddress" without an @ symbol in the email field.
</user>

The system should:
- Reject the email as invalid
- Display error message: "Please enter a valid email address"
- Highlight the email field as having an error
- Prevent form submission until corrected

**Example**: User enters email with spaces

<user>
User accidentally types "user @domain.com" with a space before the @ symbol.
</user>

The system should:
- Reject the email as invalid (spaces not allowed in email addresses)
- Display specific error: "Email addresses cannot contain spaces"
- Suggest removing the space
- Not attempt to auto-correct by removing spaces

**Example**: User enters extremely long email address

<user>
User enters an email address that is 300 characters long, exceeding the RFC 5322 limit of 254 characters.
</user>

The system should:
- Reject the email as too long
- Display error: "Email address is too long (maximum 254 characters)"
- Show character count if helpful for the user interface
- Prevent account creation with the invalid email