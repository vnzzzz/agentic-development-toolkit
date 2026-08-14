FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

USER root

# Some published devcontainer base-image layers may retain the legacy Yarn APT
# repository. This workspace does not install Yarn through APT; the Node Feature
# uses Corepack instead. Remove the unused source before apt-get update.
RUN set -eux; \
    rm -f \
        /etc/apt/sources.list.d/yarn.list \
        /etc/apt/sources.list.d/yarn.sources; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        file \
        git \
        jq \
        make \
        shellcheck \
        unzip \
        zip; \
    rm -rf /var/lib/apt/lists/*

# Create a parent-workspace virtual environment. Child Skill repositories own
# their dependencies and do not install packages during container creation.
RUN python -m venv /opt/venv \
    && chown -R vscode:vscode /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:${PATH}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN mkdir -p /home/vscode/.claude /home/vscode/.codex \
    && chown -R vscode:vscode /home/vscode/.claude /home/vscode/.codex

USER vscode
