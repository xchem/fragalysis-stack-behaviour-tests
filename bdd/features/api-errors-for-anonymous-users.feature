Feature: Key GET methods need authentication

  This feature ensures that key GET methods in the Fragalysis Stack API
  require the user to be logged-in. If not logged-in users should receive
  an error response.

  Background: Start with a new empty stack

    For all the tests here we need to start with a clean (empty) Fragalysis Stack.
    We do this by ensuring that a new stack exists (creating one if necessary).
    Stacks have a 'name', and we need specify an image tag like 'latest'.
    The stack should also be functional, by responding correctly on the landing page.

    Given an empty behaviour stack tagged latest
    Then the stack landing page should return http 200

  Scenario Template: Some REST GET methods should return 'Not Authorized'

    Here we do not login to the stack and therefore, for an un-authenticated user,
    the chosen methods are expected to return 'Not Authorized'.

    When I call <method> on the behaviour stack
    Then I should get http 403

    Examples:
      | method                            |
      | /api/job_config                   |
      | /api/compound-identifier-types    |
      | /api/token                        |

  Scenario Template: Some REST GET methods should return 'Not Allowed'

    Here we do not login to the stack and therefore, for an un-authenticated user,
    the chosen methods are expected to return 'Not Allowed'.

    When I call <method> on the behaviour stack
    Then I should get http 405

    Examples:
      | method                            |
      | /api/metadata_upload              |
      | /api/download_target_experiments  |
      | /api/download_target_experiments  |
