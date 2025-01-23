Feature: Key GET methods need authentication

  This feature ensures that key GET methods in the Fragalysis Stack API
  require the user to be logged-in. If not logged-in users should receive
  an error response.

  Scenario: Start with a new stack

    For all the tests here we need to start with a clean (empty) Fragalysis Stack.
    We do this by ensuring that a new stack exists (creating one if necessary).
    Stacks have a 'name' that is obtained from the environment variable
    BEHAVIOUR_STACK_USERNAME. We just need to specify an image tag like 'latest'.
    The stack should also be functional, by responding correctly on the landing page.

    Given a new stack using the image tag "latest"
    Then the landing page response should be OK

  Scenario Template: Some REST GET methods should return 'Not Authorized'

    Here we do not login to the stack and therefore, for an un-authenticated user,
    the chosen methods are expected to return 'Not Authorized' for a GET.

    Given I do not login
    When I do a GET request at <method>
    Then the response should be FORBIDDEN

    Examples: Restricted GET endpoints
      | method                            |
      | /api/job_config                   |
      | /api/job_request                  |
      | /api/compound-identifier-types    |
      | /api/token                        |

  Scenario Template: Some REST GET methods should return 'Not Allowed'

    Here we do not login to the stack and therefore, for an un-authenticated user,
    the chosen methods are expected to return 'Not Allowed'.

    Given I do not login
    When I do a GET request at <method>
    Then the response should be METHOD_NOT_ALLOWED

    Examples: Endpoints without a GET
      | method                            |
      | /api/metadata_upload              |
      | /api/download_target_experiments  |
      | /api/download_target_experiments  |
