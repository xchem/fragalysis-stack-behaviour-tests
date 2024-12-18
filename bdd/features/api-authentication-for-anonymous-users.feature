Feature: Key GET methods need authentication

  This feature ensures that key GET methods in the Fragalysis Stack API
  require the user to be logged-in. If not logged-in users should receive
  an error response.

  Scenario: Start with a new empty stack
    Given an empty behaviour stack tagged latest
    Then the stack landing page should return http 200

  Scenario Template: Some REST GET methods should return 'Not Authorized'
    When I call <method> on the behaviour stack
    Then I should get http 403

    Examples:
      | method                            |
      | /api/job_config                   |
      | /api/compound-identifier-types    |

  Scenario Template: Some REST GET methods should return 'Not Allowed'
    When I call <method> on the behaviour stack
    Then I should get http 405

    Examples:
      | method                            |
      | /api/metadata_upload              |
      | /api/download_target_experiments  |
      | /api/download_target_experiments  |
