Feature: Basic stack operations

  Background:
    Given an empty behaviour stack

  Example: Empty stacks should have no targets
    Given the stack is responding
    Then there should be 0 targets
