Feature: Empty stack public API operations

  Rule: Start with an empty stack

    Scenario: Check new empty stacks respond
      Given an empty behaviour stack tagged latest
      Then the stack landing page should return http 200

  Rule: Empty stacks don't have content on the main public API methods

    Scenario Outline: Check the main public API methods
      When I call <method> on the behaviour stack
      Then the length of the returned list should be 0

      Examples:
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

  Rule: Empty stacks should have some tag API categories

    Scenario Outline: Check the Tag Categories API method
      When I call <method> on the behaviour stack
      Then the length of the returned list should be <size>

      Examples:
        | method            | size |
        | /api/tag_category |    9 |
