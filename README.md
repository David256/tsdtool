# tsdtool

> _From the creators of [rcdtool](https://github.com/David256/rcdtool)..._

Script that downloads telegram stories.

## Usage

For help:

```bash
./tsdtool --help
```

This script needs the story link to download it. If you don't provide a link via CLI arguments,
then the script will prompt you for one.

If you have channel and message IDs you can do:
```bash
./tsdtool -c /path/to/config.ini --link "https://t.me/<username>/s/<id>" -O video-name.mp4
```
Then the script starts the downloading.

**If the story is an image, note the filename**.

Well, if you use the Python script, then change `tsdtool` by `python tsdtool` et voilà.

## Dist

In this repository we release the source code (Python) and a binary option for GNU/Linux. You can build a binary for any other operating system using tool as [PyInstaller](https://pyinstaller.org/en/).

## Telegram session

You MUST have an API ID provided by Telegram at https://my.telegram.org/ (I think). This is as follows:
```
api_id: 32767
api_hash: ed855a59bbe4a3360dbf7a0538842142
```
Then rename `config.ini.sample` to `config.ini`, edit it and save wherever you want. If the file is in the same directory as `tsdtool` and its name is exactly "config.ini", then `tsdtool` will load it automatically.

The first time, **tsdtool** will ask you for your phone number, and will start a login process. When this is done, a `.session` file will be created. With this `.session` file, the tool could access to your Telegram account to read messages and download medias. The name of the .session file is set in `config.ini`.

## TODO
- [ ] Download all stories for user.
- [ ] Extend CLI arguments.