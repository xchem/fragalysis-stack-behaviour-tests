Feature: Basic stack operations

  @fixture.create.stack
  Scenario: Created stacks have no targets
    Given we have a stack installed
     Then there should be no targets
