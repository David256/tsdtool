#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2023 David256
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import re
from dataclasses import dataclass
from typing import Optional, Union, cast
import argparse
import sys
# pylint: disable=unused-import
import readline

import configparser
from telethon import TelegramClient
from telethon.functions import stories
from telethon.types import stories as S
from telethon.types import MessageMediaPhoto, MessageMediaDocument


re_story_link = re.compile(r'https://t\.me/(\w+)/s/(\d+)')


@dataclass
class Arguments:
    """Arguments."""
    config_filename: str
    channel_id: Optional[str]
    message_id: Optional[str]
    output_filename: Optional[str]
    link: Optional[str]


def get_args():
    """Parser the CLI arguments and return a Namespace object.

    Returns:
        Namespace: Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog='tsdtool',
        description=(
            'Script that uses the Telegram API to download any Telegram story'
            'from link or channel/user ID'
        )
    )

    parser.add_argument('--link',
                        nargs='?',
                        dest='link',
                        const="",
                        default=None,
                        help=(
                            'Take IDs from an story link: '
                            'https://t.me/<username:string>/sa/<id:int>'
                            ),
                        )
    parser.add_argument('-c',
                        '--config',
                        nargs='?',
                        dest='config_filename',
                        default='config.ini',
                        help='The config filename')
    parser.add_argument('-O',
                        '--output',
                        nargs='?',
                        dest='output_filename',
                        help='The output filename')
    return parser, cast(Arguments, parser.parse_args())


def get_config(config_filename: str):
    """Create a config object from config file.

    Args:
        config_filename (str): The config filename.

    Returns:
        ConfigParser: a new ConfigParser object.
    """
    if not os.path.exists(config_filename):
        raise FileNotFoundError(f'Not found: {config_filename}')
    config = configparser.ConfigParser()
    config.read(config_filename)
    return config


def create_client(config: configparser.ConfigParser):
    """Create a Telegram client object from given config.

    Args:
        config (configparser.ConfigParser): Parsed config object.

    Returns:
        TelegramClient: The Telegram client object.
    """
    client = TelegramClient(
        session=config['Access']['session'],
        api_id=config['Access']['id'],
        api_hash=config['Access']['hash'],
        timeout=int(config['Client']['timeout']),
        device_model=config['Client']['device_model'],
        lang_code=config['Client']['lang_code'],
    )
    client.start()
    return client


async def process(client: TelegramClient,
                  peer_id: Union[int, str],
                  story_peer_id: int,
                  output_filename: str,
                  ):
    """process_test."""
    print('processing...')
    _stories: S.Stories = await client(
        stories.GetStoriesByIDRequest(
            peer=peer_id,
            id=[story_peer_id],
        )
    )

    # print(_stories.stringify())

    story = _stories.stories[0]

    media: Union[MessageMediaDocument, MessageMediaPhoto, None] = None

    if isinstance(story.media, MessageMediaPhoto):
        media = story.media.photo
    elif isinstance(story.media, MessageMediaDocument):
        media = story.media.document
    else:
        print('Cannot determine the media type. Founnd:', type(story.media))
        return

    with open(output_filename, 'wb+') as file:
        await client.download_file(media, file)
        print(f'downloaded to {output_filename}')


def main():
    """
    The main method.
    """
    parser, args = get_args()
    config = get_config(args.config_filename)

    try:
        link = args.link if args.link else input('link: ')
    except KeyboardInterrupt:
        print()
        return

    matched = re_story_link.match(link)
    if matched is None:
        parser.print_help()
        parser.exit(-1)

    peer, story_id = matched.groups()

    if not story_id.isdigit():
        parser.print_help()
        parser.exit(-1)

    client = create_client(config)

    coro = process(
        client,
        peer,
        int(story_id),
        args.output_filename or f'file.{peer}.{story_id}',
    )

    client.loop.run_until_complete(coro)


if __name__ == '__main__':
    try:
        main()
    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(e, file=sys.stderr, flush=True)
        sys.exit(-1)
