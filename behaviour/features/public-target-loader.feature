Feature: Verify good Targets can be loaded against the public TAS

  This feature ensures that target data located on an S3 bucket
  (expected to have been generated by XChem-Align)
  can be loaded into a new stack against the public proposal.
  We rely on a clean stack and a CAS-authenticated user who is also
  a member of the public TAS (lb18145-1).

  To significantly reduce execution time the feature has to be treated as one.
  The target loading only works if the stack is clean, but we do not create
  a clean stack for each iteration. So the feature starts with a clean stack
  but scenarios in this feature rely on that initial requirement.

  The steps rely on 'sensitive' material that is expected to be provided
  by environment variables. The tests will alert if these are not set.

  Scenario: Start with a new (empty) stack

    Create a new (up to date) stack.
    We can pass-in some extra variables using the initial step's 'doc string'.
    The doc string, if set, is interpreted as Dictionary string.
    The variables it is expected to define will be passed to the
    corresponding AWX Job Template when it's launched.

    Given an empty stack
    Then the landing page response should be OK

  Scenario Template: Load public targets

    Load target files (located in an S3 bucket) into the stack.
    The target files are expected to be in a TGZ format.
    We check the upload status and subsequent API responses.
    We introduce a timeout to allow for the upload to complete,
    which is typically twice the expected processing time (after upload).

    Given I do not login
    And I can access the "fragalysis-stack-xchem-data" bucket
    When I get the TGZ encoded file <tgz> from the bucket
    And I login
    And I load the file against target access string "lb18145-1"
    Then the response should be ACCEPTED
    And the response should contain a task status endpoint
    And the task status should have a value of SUCCESS within <upload timeout> minutes
    When I do a GET request at /api/target_experiment_uploads
    Then the length of the list in the response should be <upload count>
    When I do a GET request at /api/targets?title=<target>
    Then the length of the list in the response should be 1

    Examples: Experiment files and Targets
    | tgz                                 | target    | upload timeout | upload count |
    | lb32627-66_v2.2_upload_1_2024-12_09 | A71EV2A   | 6  | 1 |
    | lb32633-6_v2.2_upload_1_2024-11-22  | CHIKV_Mac | 14 | 2 |
