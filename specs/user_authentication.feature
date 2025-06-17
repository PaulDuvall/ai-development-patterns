# User Authentication Feature Specification
# This specification persists throughout the project lifecycle
# It defines WHAT the system does, not HOW it's implemented

Feature: User Authentication
  As a user
  I want to log into the system
  So that I can access my personal dashboard

  Scenario: Successful login with valid credentials
    Given a user exists with email "user@example.com" and password "securepass123"
    When I submit login credentials "user@example.com" and "securepass123"
    Then I should be redirected to the dashboard
    And I should see a welcome message "Welcome back!"
    And I should receive a valid JWT token
    And the token should expire in 15 minutes

  Scenario: Failed login with invalid credentials
    Given a user exists with email "user@example.com" and password "securepass123"
    When I submit login credentials "user@example.com" and "wrongpassword"
    Then I should see an error message "Invalid credentials"
    And I should remain on the login page
    And no JWT token should be issued

  Scenario: Failed login with non-existent user
    Given no user exists with email "nonexistent@example.com"
    When I submit login credentials "nonexistent@example.com" and "anypassword"
    Then I should see an error message "Invalid credentials"
    And I should remain on the login page
    And no JWT token should be issued

  Scenario: Rate limiting after multiple failed attempts
    Given a user exists with email "user@example.com" and password "securepass123"
    When I submit invalid credentials 5 times within 1 minute
    Then I should see an error message "Too many login attempts. Please try again later."
    And further login attempts should be blocked for 15 minutes
    Even with valid credentials

  Scenario: Token refresh with valid refresh token
    Given I have a valid refresh token
    When I request a new access token using the refresh token
    Then I should receive a new JWT access token
    And the new token should expire in 15 minutes
    And the refresh token should remain valid

  Scenario: Token refresh with expired refresh token
    Given I have an expired refresh token
    When I request a new access token using the refresh token
    Then I should see an error message "Refresh token expired"
    And no new access token should be issued
    And I should be redirected to the login page