/**
 * Various configuration variables (extracted from the environment)
 * and exported for use by the test scripts. Variables are common to
 * the API-based behaviour tests (see the 'behaviour' directory's 'config.py').
 *
 * Expects: -
 *
 * BEHAVIOUR_AWX_USERNAME
 *      The username of the AWX user used to form the stack.
 *      Used to 'predict' the stack URL.
 *
 * BEHAVIOUR_STACK_NAME
 *      The 'name' of the stack used for the AWX JobTemplate that created the stack.
 *      Used to 'predict' the stack URL. It has a default of 'behaviour'.
 *
 * BEHAVIOUR_STACK_USERNAME
 *      A CAS user entitled to see the Target under test
 *
 * BEHAVIOUR_STACK_PASSWORD
 *      The password for the CAS user
 *
 * BEHAVIOUR_PLAYWRIGHT_TEST_TARGET
 *      A Target known to be present in the stack, accessible by the chosen CAS user
 */
const awxUsername: string = (process.env.BEHAVIOUR_AWX_USERNAME as string)
const stackDomain: string = 'xchem-dev.diamond.ac.uk'

export const stackUsername: string = (process.env.BEHAVIOUR_STACK_USERNAME as string)
export const stackPassword: string = (process.env.BEHAVIOUR_STACK_PASSWORD as string)
export const stackName: string = (process.env.BEHAVIOUR_STACK_NAME || "behaviour" as string)
export const stackHostname: string = `fragalysis-${awxUsername}-${stackName}.${stackDomain}`
export const stackURL: string = `https://${stackHostname}`
export const testTarget: string = (process.env.BEHAVIOUR_PLAYWRIGHT_TEST_TARGET as string)
