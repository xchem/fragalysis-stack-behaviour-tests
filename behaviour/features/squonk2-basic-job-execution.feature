Feature: Verify a fragalysis stack can run Squonk Jobs against public Targets

  Here we check that a properly configured stack can run Squonk Jobs.

  To significantly reduce execution time the feature has to be treated as sequence
  that runs from top to bottom. It's not encouraged but it enable us to create
  much faster tests. The job execution only works reliably if the stack is clean,
  but we do not create a clean stack for each scenario as that would take too long.
  So the feature starts with a clean stack and scenarios in this feature
  rely on that initial requirement.

  Scenario: Create a new stack for Job execution

    This initial step can accept a Doc string that represents a Python dictionary.
    If provided it will be interpreted as an additional set of Ansible variables
    that will be sent to the launch command for the corresponding Job Template.
    Any Ansible variables can be defined. For example, to deploy a custom stack image
    you could provide the following Doc string: -

      """
      {
        "stack_image": "alanbchristie/fragalysis-stack",
        "stack_image_tag": "m2ms-1559-job-execution",
      }
      """

    Given an empty stack
      """
      {
        "stack_image": "alanbchristie/fragalysis-stack",
        "stack_image_tag": "m2ms-1559-job-execution",
        "stack_disable_restrict_proposals_to_membership": True,
      }
      """
    Then the landing page response should be OK

  @wip
  Scenario: The front-end needs a JobOverride
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
          "target_loader_data/A71EV2A_lb18145-1/upload_1/aligned_files/A71EV2A-x0152/A71EV2A-x0152_A_201_1_A71EV2A-x3977+A+202+1_apo-desolv.pdb",
        ],
        "compounds": [
          "target_loader_data/A71EV2A_lb18145-1/upload_1/aligned_files/A71EV2A-x0202/A71EV2A-x0202_A_147_1_A71EV2A-x3977+A+202+1_ligand_LIG.mol",
          "target_loader_data/A71EV2A_lb18145-1/upload_1/aligned_files/A71EV2A-x0202/A71EV2A-x0202_A_201_1_A71EV2A-x0488+A+147+1_ligand_LIG.mol",
        ],
      }
      """
    Then the response should be ACCEPTED
    And the file transfer status should have a value of SUCCESS within 30 seconds

  Scenario: Run fragmenstein-combine on the A71EV2A Snapshot files
    Given I do not login
    And I can get the "lb18145-1" Project ID
    And I can get the "A71EV2A" Target ID
    And I can get the "Behaviour SessionProject" SessionProject ID
    And I can get the "Behaviour Snapshot" Snapshot ID
    And I can get the last JobFileTransfer SUB_PATH
    When I login
    And I run a Squonk Job using the following specification
      """
        {
          "collection": "fragmenstein",
          "job": "fragmenstein-combine",
          "version": "1.0.0",
          "variables": {
            "outfile": "merged.sdf",
            "count": 1,
            "smilesFieldName": "original SMILES",
            "fragIdField": "_Name",
            "proteinFieldName": "ref_pdb",
            "proteinFieldValue": "A71EV2A",
            "protein": "fragalysis-files/{SUB_PATH}/A71EV2A-x0152_A_201_1_A71EV2A-x3977+A+202+1_apo-desolv.pdb",
            "fragments": [
              "fragalysis-files/{SUB_PATH}/A71EV2A-x0202_A_147_1_A71EV2A-x3977+A+202+1_ligand_LIG.mol",
              "fragalysis-files/{SUB_PATH}/A71EV2A-x0202_A_201_1_A71EV2A-x0488+A+147+1_ligand_LIG.mol",
            ],
          },
        }
      """
    Then the response should be ACCEPTED
    And the response should contain a JobRequest ID
    And the JobRequest should have a job_status value of SUCCESS within 1 minute
    And the JobRequest should have an upload_status value of SUCCESS within 20 seconds
    When I do a GET request at /api/compound-sets
    Then the length of the list in the response should be 1

  Scenario: Delete the last FileTransfer
    Given I can login
    And I can get the last JobFileTransfer ID
    When I delete the JobFileTransfer
    Then the response should be NO_CONTENT

  Scenario: Delete the Snapshot and SessionProject
    Given I do not login
    And I can get the "Behaviour Snapshot" Snapshot ID
    And I can get the "Behaviour SessionProject" SessionProject ID
    When I login
    And I delete the Snapshot
    Then the response should be NO_CONTENT
    When I delete the SessionProject
    Then the response should be NO_CONTENT
