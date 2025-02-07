/**
 * Various configuration variables (extracted from the environment)
 * and exported for use by the test scripts. Variables are shared
 * with the API-based behaviour tests (see the 'behaviour' directory).
 */
const awxUsername = process.env.BEHAVIOUR_AWX_USERNAME
const stackDomain = 'xchem-dev.diamond.ac.uk'

export const stackUsername = process.env.BEHAVIOUR_STACK_USERNAME
export const stackPassword = process.env.BEHAVIOUR_STACK_PASSWORD
export const stackName = process.env.BEHAVIOUR_STACK_NAME
export const stackHostname = `fragalysis-${awxUsername}-${stackName}.${stackDomain}`
export const stackURL = `https://${stackHostname}`
export const testTarget = process.env.BEHAVIOUR_PLAYWRIGHT_TEST_TARGET
