from invoke import task, Collection

import build
import vm
import base

zvm = Collection("zvm", build, vm)
zvm.add_task(base.init)

namespace = Collection()
namespace.add_collection(zvm)
