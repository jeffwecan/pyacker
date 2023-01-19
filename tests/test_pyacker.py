#!/usr/bin/env pytest
import pytest
from requests.exceptions import HTTPError

from pyacker import Pyacker


def test_auth():
    pyacker = Pyacker()
    print(dir(pyacker.auth))
    auth_resp = pyacker.auth()
    assert "access_token" in auth_resp.json()


class TestAuthenticatedRequests:
    @pytest.fixture
    def pyacker(self):
        pyacker = Pyacker()
        pyacker.auth()
        yield pyacker

    def test_list_buckets(self, pyacker):
        buckets = pyacker.list_buckets()
        assert isinstance(buckets, list)

    def test_get_bucket_but_when_we_get_there_is_no_bucket(self, pyacker):
        with pytest.raises(HTTPError):
            pyacker.get_bucket("not-a-bucket")
