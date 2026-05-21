FROM r-base:latest
RUN Rscript -e "install.packages(c('randomForest', 'tictoc'), repos='https://cloud.r-project.org')"
WORKDIR /progetto