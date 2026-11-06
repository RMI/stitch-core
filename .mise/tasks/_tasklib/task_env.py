from pprint import pp
import functools
import os
import re


def get_env(key: str):
    key_ = "_".join(re.split(r"\W", key)).upper()
    return os.getenv(key_, os.getenv(key_.lower()))


def get_usage(arg: str):
    return get_env(f"usage-{arg}")


def with_usage_args(*argnames: str):
    def dec_with_usage_args(fn):
        @functools.wraps(fn)
        def arg_wrapper(*args, **kwargs):
            return fn(**{n: get_usage(n) for n in argnames})

        return arg_wrapper

    return dec_with_usage_args


def usage(fn):
    @functools.wraps(fn)
    def _wrapped(*args, **kwargs):
        pp("calling from wrapped")
        kw = {k: kls(get_usage(k)) for k, kls in fn.__annotations__.items()}
        pp(kw)
        fn(**kw)

    return _wrapped
