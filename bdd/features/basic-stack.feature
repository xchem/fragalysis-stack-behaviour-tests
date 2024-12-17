Feature: Basic stack operations

  Background:
    Given an empty behaviour stack

  Scenario: Empty stacks have no targets
    Given we have a stack installed
    Then there should be no targets
