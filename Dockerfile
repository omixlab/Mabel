FROM condaforge/miniforge3:23.1.0-4

RUN mkdir -p /home/bambu-systematic-review 
COPY . /home/bambu-systematic-review
WORKDIR /home/bambu-systematic-review/src
RUN conda install -c conda-forge mamba
RUN mamba install -c conda-forge spacy
RUN conda env create --file ../environment.yml
RUN bash ../scripts/autoactivate_conda_env.sh
EXPOSE 5000

CMD ["bash", "../scripts/run_webserver.sh"]