FROM public.ecr.aws/lambda/python:3.14 AS base

RUN dnf -y install gcc gcc-c++ make \
    && dnf -y clean all \
    && python -m pip install --upgrade pip

# Install dependencies
COPY src/requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}

# Function-specific targets share the same base image layers.
FROM base AS sync-tw-data

FROM base AS line-webhook
