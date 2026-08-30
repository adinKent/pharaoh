from routing.idempotency import InMemoryIdempotencyStore


def test_duplicate_request_is_claimed_only_once():
    store = InMemoryIdempotencyStore()

    assert store.claim("event-1") is True
    assert store.claim("event-1") is False
