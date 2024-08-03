from invoke import Collection

import build
import vm

namespace = Collection(
    build,
    vm
)
