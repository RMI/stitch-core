#!/usr/bin/env -S uv run --script
# MISE extends="py"
# USAGE arg "<boot>"
# USAGE flag "-o --out <foo>" {
# USAGE   default "1"
# USAGE }
# USAGE flag "-x --extreme" default "false"
import os
import re
from pprint import pp

from task_env import get_usage, with_usage_args, usage


def get_env(key: str):
    key_ = "_".join(re.split(r"\W", key)).upper()
    return os.getenv(key_, os.getenv(key_.lower()))


@with_usage_args("boot", "out")
def my_function(boot: str, out: str):
    pp(f"it's the {boot}! and {out}")


@usage
def other_func(out: int, boot: str, extreme: bool = False):
    pp("calling from other")
    pp(f"out: {out}, boot: {boot}, extreme: {extreme}")


my_function()
pp({k: v for k, v in os.environ.items() if k.startswith("usage_")})
other_func()
