"""
Elastic License 2.0

Copyright Discend and/or licensed to Discend under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
import os
import threading
import time


class SnowflakeFactory:
    def __init__(self) -> None:
        self._epoch: int = 1641042000000
        self._incrementation = 0
        # NOTE:
        # The mathematics here may seem weird, 
        # but all it does is say: “Generate a bucket every <some> days”, 
        # in this case we have it set to 10.
        # Buckets are used for messages to not overfill primary key sizes, 
        # ScyllaDB maxes out at 100 gigabyte storage for multiple of 
        # the same primary keys (like if there’s only id and it’s duplicated), 
        # and since channel_id is duplicated across every message and is an 
        # obvious primary key, it can overfill, this bucket eliminates that 
        # possibility by incrementing a primary key value per 10 days. 
        # For inactive servers, this could be costly, but that will be rare and is worth the cost. 
        # Querying messages here are simple, just get the current bucket 
        # and decrease until either you find your message 
        # or get enough messages to return. 
        # Eventually, elasticsearch will need to be used for querying through massive 
        # amounts and searching old messages but for now it’s fine. 
        # Discend will store empty buckets once found in a channel 
        # to reduce the effects of querying through useless buckets.
        self._bucket_size = 1000 * 60 * 60 * 24 * 10

    def forge(self) -> int:
        current_ms = int(time.time() * 1000)
        epoch = current_ms - self._epoch << 22

        curthread = threading.current_thread().ident
        assert (
            curthread is not None
        )  # NOTE: done for typing purposes, shouldn't ever actually be None.

        epoch |= (curthread % 32) << 17
        epoch |= (os.getpid() % 32) << 12

        epoch |= self._incrementation % 4096

        if self._incrementation == 9000000000:
            self._incrementation = 0

        self._incrementation += 1

        return epoch

    def make_bucket(self, epoch: int) -> int:
        timestamp = epoch >> 22
        return timestamp // self._bucket_size

    def make_buckets(self, start_id, end_id=None):
        return range(self.make_bucket(start_id), self.make_bucket(end_id) + 1)


forger = SnowflakeFactory()


if __name__ == '__main__':
    while True:
        import sys

        enforgement = forger.forge()
        enforged_bucket = forger.make_bucket(enforgement)

        print(enforgement, enforged_bucket, file=sys.stderr)
