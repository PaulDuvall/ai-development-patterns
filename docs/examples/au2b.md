# Password Hashing Requirements

Examples for [^au2b] in bcrypt hashing with minimum cost factor 12:

**Example**: User creates account with new password

<user>
User registers for a new account and chooses the password "MySecurePassword123!" during the sign-up process.
</user>

The system should:
- Hash the password using bcrypt algorithm with cost factor 12 or higher
- Generate a unique salt for this specific password hash
- Store only the bcrypt hash in the database, never the plain text password
- Take approximately 100-500ms to complete the hashing process

**Example**: User logs in with existing password

<user>
User attempts to log in with their email and the password "MySecurePassword123!" that they created during registration.
</user>

The system should:
- Retrieve the stored bcrypt hash for that user from the database
- Use bcrypt's verification function to check the provided password against the hash
- Successfully authenticate if the password matches
- Take approximately the same amount of time as hashing (100-500ms)

**Example**: User enters incorrect password

<user>
User tries to log in but mistypes their password as "MySecurePassword124!" (wrong number at the end).
</user>

The system should:
- Still perform the full bcrypt verification process against the stored hash
- Take the same amount of time as a successful verification (to prevent timing attacks)
- Return "Invalid email or password" without revealing that the password was wrong
- Not provide any hints about how close the password was to being correct

**Example**: Legacy user with weaker password hash

<user>
An existing user account was created years ago when the system used bcrypt cost factor 10. The user successfully logs in with their correct password.
</user>

The system should:
- Verify the password against the existing cost factor 10 hash
- Detect that the hash uses a cost factor below the current minimum (12)
- Re-hash the password with cost factor 12 using the same plain text password
- Update the database with the stronger hash for future logins

**Example**: System performance during high load

<user>
During peak usage hours, 1000 users per minute are attempting to log in to the system.
</user>

The system should:
- Maintain the minimum cost factor 12 for all password operations
- Not reduce the cost factor to improve performance during high load
- Use appropriate server scaling or queuing if response times become unacceptable
- Prioritize security over speed while maintaining reasonable user experience

**Example**: Developer tries to configure weaker hashing

<user>
A developer attempts to configure the system with bcrypt cost factor 8 to improve login performance during development.
</user>

The system should:
- Reject any configuration with cost factor below 12
- Display error: "Cost factor must be 12 or higher for security compliance"
- Use the default cost factor 12 if no valid configuration is provided
- Log the configuration attempt for security audit purposes