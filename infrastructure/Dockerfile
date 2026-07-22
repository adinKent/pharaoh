# Builder stage: compile/install deps with the toolchain, then discard it.
FROM public.ecr.aws/lambda/python:3.14 AS builder

RUN dnf -y install gcc gcc-c++ make \
    && dnf -y clean all

COPY src/requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt --target ${LAMBDA_TASK_ROOT}

# Runtime stage: no compilers, just the installed deps + app code.
# libstdc++/libgomp are the shared libs pandas/numpy/grpcio wheels link against.
FROM public.ecr.aws/lambda/python:3.14 AS app

RUN dnf -y install libstdc++ libgomp \
    && dnf -y clean all

# Deps first (changes rarely) so code-only deploys only rebuild the last layer.
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}
COPY src/ ${LAMBDA_TASK_ROOT}
