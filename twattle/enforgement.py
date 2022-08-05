"""
Copyright 2021-2022 twattle, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import threading
import time


class SnowflakeFactory:
    def __init__(self) -> None:
        self._epoch: int = 1641042000000
        self._incrementation = 0
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
