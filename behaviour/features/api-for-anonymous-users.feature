Feature: Empty stack public API operations

  This feature ensures that a number of REST GET methods in the Fragalysis Stack API
  do respond when the user is not logged in to the stack application.
  These anonymous users should not see errors, but on an empty stack
  shouldn't yield anything. These features expect the stack user not to be logged in.

  Scenario: We need a new empty stack

    For all the tests here we need to start with a clean (empty) Fragalysis Stack.
    We do this by ensuring that a new stack exists (creating one if necessary).
    Stacks have a 'name', and we need specify an image tag like 'latest'.
    The stack should also be functional, by responding correctly on the landing page.

    Given an empty behaviour stack tagged latest
    Then the landing page response should be OK

  Scenario Template: Check the main public API methods

    These tests, all starting with an empty stack, verify that the selected
    API methods respond without error to a GET for any user who has not logged in.
    An empty stack has no data so everything tested here should return
    successfully and with an empty list of objects.

    Given I do not login to the behaviour stack
    When I do a GET at <method>
    Then the API response should be OK
    And the length of the list in the response should be 0

    Examples: Public GET methods
      | method                          |
      | /api/action-type                |
      | /api/canon_sites                |
      | /api/canon_site_confs           |
      | /api/compound-scores            |
      | /api/compound-identifiers       |
      | /api/compound-mols-scores       |
      | /api/compound-sets              |
      | /api/compound-molecules         |
      | /api/computedset_download       |
      | /api/cmpdimg                    |
      | /api/cmpdchoice                 |
      | /api/compounds                  |
      | /api/experiments                |
      | /api/job_callback               |
      | /api/job_file_transfer          |
      | /api/job_override               |
      | /api/graph                      |
      | /api/hotspots                   |
      | /api/interactions               |
      | /api/interactionpoints          |
      | /api/molimg                     |
      | /api/molprops                   |
      | /api/numerical-scores           |
      | /api/poses                      |
      | /api/projects                   |
      | /api/protmap                    |
      | /api/protpdb                    |
      | /api/protpdbbound               |
      | /api/scorechoice                |
      | /api/siteobservationgroup       |
      | /api/site_observations          |
      | /api/siteobservation_tag        |
      | /api/session-actions            |
      | /api/session-projects           |
      | /api/session_project_tag        |
      | /api/snapshot-actions           |
      | /api/snapshots                  |
      | /api/targets                    |
      | /api/targetres                  |
      | /api/target_experiment_uploads  |
      | /api/text-scores                |
      | /api/vector                     |
      | /api/viewscene                  |
      | /api/xtalform_sites             |

  Scenario: Check the Tag Categories API method

    A small number of methods return objects, even on an empty stack.
    Here we check that an unauthenticated user sees this 'public' data.

    Given I do not login to the behaviour stack
    When I do a GET at /api/tag_category
    Then the API response should be OK
    And the length of the list in the response should be 9
