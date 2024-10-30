FROM public.ecr.aws/amazonlinux/amazonlinux:2  # Use Amazon Linux 2 as the base image

ENV PATH=/usr/local/bin:$PATH \  # Add /usr/local/bin to the PATH environment variable
    LC_ALL=C.UTF-8 \  # Set the locale to UTF-8
    LANG=C.UTF-8 \  # Set the language to UTF-8
    WEB_CONCURRENCY=2  # Set the web concurrency to 2

EXPOSE 8000  # Expose port 8000 for the application
WORKDIR /srv  # Set the working directory to /srv
COPY . /srv  # Copy the current directory contents into /srv in the container

RUN yum update -y \  # Update all packages
    && amazon-linux-extras enable python3.8 \  # Enable Python 3.8 in Amazon Linux extras
    && yum groupinstall -y "Development tools" \  # Install development tools
    && yum install -y \  # Install the following packages:
           python38-devel \  # Python 3.8 development files
           pycairo \  # Python bindings for Cairo
           python38 \  # Python 3.8 interpreter
           libffi-devel \  # Development files for libffi
    && python3.8 -m pip install pip --upgrade \  # Upgrade pip for Python 3.8
    && ln -s /usr/local/bin/pip3 /usr/bin/pip3 \  # Create a symbolic link for pip3
    && ln -s /usr/bin/pydoc3.8 /usr/local/bin/pydoc \  # Create a symbolic link for pydoc
    && ln -s /usr/bin/python3.8 /usr/local/bin/python \  # Create a symbolic link for python
    && ln -s /usr/bin/python3.8-config /usr/local/bin/python-config \  # Create a symbolic link for python-config
    && yum -y clean all --enablerepo='*' \  # Clean all yum caches
    && rm -rf /var/cache/yum  # Remove the yum cache directory

RUN pip3 install -r requirements.txt  # Install Python dependencies from requirements.txt

CMD ["python", "./app.py"]  # Run the application using Python
