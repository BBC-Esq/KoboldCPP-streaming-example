# KoboldCPP-streaming-example
Example of how to stream a response using KoboldCPP's server.

## Operation

1) Download the latest release and navigate to where ```chat_kobold_stream.py``` is located.
2) Create virtual environment:
```
python -m venv .
```
3) Activate virtual environment

```
.\Scripts\activate
```
4) Upgrade pip
```
python.exe -m pip install --upgrade pip
```
5) Install dependencies
```
pip install -r requirements.txt --no-deps
```
6) Run program
```
python chat_kobold_stream.py
```
7) Usage
- Click the ```download``` button to open the downloader and choose a version of kobold to download.
- It'll download to the current folder.
- Doubleclick the file and start ```Kobold``` the traditional way.
- Start chatting.

## Note, there is no conversational memory and this is just an example of how to use ```KoboldCPP's``` streaming API.
