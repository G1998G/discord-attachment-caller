FROM python:3
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install discord
RUN mkdir bot
COPY main.py /bot
COPY del_cog.py /bot
COPY ref_cog.py /bot
COPY basic_cog.py /bot
COPY sql_setting.py /bot
WORKDIR /bot
CMD ["python","main.py"]
