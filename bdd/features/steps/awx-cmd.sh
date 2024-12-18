#!/bin/sh -l

TEMPLATE=$1

echo "Launching Job Template ${TEMPLATE} and waiting..."
awx job_templates launch --wait -e @awx-extra-vars.yaml "${1}"
