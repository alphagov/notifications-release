from app.cache_store import cached


def test_cached_reuses_result_for_same_arguments():
    calls = []

    @cached()
    def get_value(value):
        calls.append(value)
        return len(calls)

    assert get_value("value") == 1
    assert get_value("value") == 1
    assert calls == ["value"]


def test_cached_distinguishes_arguments():
    calls = []

    @cached()
    def get_value(value):
        calls.append(value)
        return len(calls)

    assert get_value("first") == 1
    assert get_value("second") == 2
    assert calls == ["first", "second"]


def test_cached_can_ignore_first_argument():
    calls = []

    @cached(ignore_first_arg=True)
    def get_value(token, value):
        calls.append((token, value))
        return len(calls)

    assert get_value("first-token", "value") == 1
    assert get_value("second-token", "value") == 1
    assert calls == [("first-token", "value")]


def test_cached_uses_configured_ttl_and_maxsize():
    @cached(ttl=30, maxsize=2)
    def get_value(value):
        return value

    assert get_value.cache.ttl == 30
    assert get_value.cache.maxsize == 2
