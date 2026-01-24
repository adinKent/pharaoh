FROM public.ecr.aws/lambda/python:3.14

# Install dependencies
COPY src/requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

RUN dnf -y install gcc gcc-c++ make \
    && dnf -y clean all \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}
