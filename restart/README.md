# README

## Getting started

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with the following content:

```text
API_BASE_URL=https://XX.XX.X.X:XXXX
API_USERNAME=XXXXXXXXXXXXXXX
API_PASSWORD=XXXXXXXX
```

```shell
python main.py
```

## Create an executable for Linux

```shell
pip install pyinstaller
pyinstaller --onefile --name restart_uap main.py
```

The generated executable will be placed in the `dist` folder created in the
same directory as your script. You can distribute this file, and it will run on
Linux systems without requiring Python or any dependencies to be installed.

## API Documentation

<https://ubntwiki.com/products/software/unifi-controller/api>
