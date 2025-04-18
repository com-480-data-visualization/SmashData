FROM mcr.microsoft.com/devcontainers/ruby:1-3.3-bullseye

RUN apt-get update
RUN apt-get install -y ruby-full build-essential zlib1g-dev pip

RUN echo 'export GEM_HOME="$HOME/gems"' >> /home/vscode/.bashrc
RUN echo 'export PATH="$HOME/gems/bin:$PATH"' >> /home/vscode/.bashrc

RUN gem install jekyll bundler


# WORKDIR /workspaces/ada-2024-project-fadadudata2024
COPY ./pip_requirements.txt .
RUN pip install -r ./pip_requirements.txt
