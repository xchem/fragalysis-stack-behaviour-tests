Feature: Verify a fragalysis stack can run Squonk Jobs against public Targets

  Here we check that a properly configured stack can run Squonk Jobs.

  To significantly reduce execution time the feature has to be treated as one.
  The job execution only works reliably if the stack is clean, but we do not create
  a clean stack for each scenario as that would take too long.
  So the feature starts with a clean stack and scenarios in this feature
  rely on that initial requirement.

  Scenario: Create a new stack for Job execution
    Given an empty stack using the image tag latest
    Then the landing page response should be OK

  @wip
  Scenario: A JobOverride must exist
    Given I can login
    When I do a GET request at /api/job_override
    Then the length of the list in the response should be 1

  Scenario: Load A71EV2A Target data against lb18145-1
    Given I do not login
    And I can access the "fragalysis-stack-xchem-data" bucket
    When I get the TGZ encoded file lb32627-66_v2.2_upload_1_2024-12_09 from the bucket
    And I login
    And I load the file against target access string "lb18145-1"
    Then the response should be ACCEPTED
    And the response should contain a task status endpoint
    And the task status should have a value of SUCCESS within 6 minutes

  Scenario: Create a SessionProject and Snapshot for A71EV2A
    Given I do not login
    And I can get the "A71EV2A" Target ID
    When I login
    And I create a new SessionProject with the title "Behaviour SessionProject"
    Then the response should be CREATED
    When I create a new Snapshot with the title "Behaviour Snapshot"
    Then the response should be CREATED

  @wip
  Scenario: Transfer A71EV2A Snapshot files to Squonk
    Given I do not login
    And I can get the "lb18145-1" Project ID
    And I can get the "A71EV2A" Target ID
    And I can get the "Behaviour SessionProject" SessionProject ID
    And I can get the "Behaviour Snapshot" Snapshot ID
    When I login
    When I transfer the following files to Squonk
      """
      {
        "proteins": [
          "A71EV2A-x0152/A71EV2A-x0152_A_201_1_A71EV2A-x3977+A+202+1_apo-desolv.pdb",
        ],
        "compounds": [
          "A71EV2A-x0152/A71EV2A-x0152_A_201_1_A71EV2A-x3977+A+202+1_ligand.mol",
          "A71EV2A-x0202/A71EV2A-x0202_A_147_1_A71EV2A-x3977+A+202+1_ligand.mol",
          "A71EV2A-x0269/A71EV2A-x0269_A_147_1_A71EV2A-x3977+A+202+1_ligand.mol",
        ],
      }
      """
    Then the response should be OK
    And the file transfer status should have a value of SUCCESS within 2 minutes

  Scenario: Delete the Snapshot and SessionProject
    Given I do not login
    And I can get the "Behaviour Snapshot" Snapshot ID
    And I can get the "Behaviour SessionProject" SessionProject ID
    When I login
    And I delete the Snapshot
    Then the response should be NO_CONTENT
    When I delete the SessionProject
    Then the response should be NO_CONTENT
