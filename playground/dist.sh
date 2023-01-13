#!/bin/sh

set -e

. $(dirname -- "$0")/env.sh

TARGET_PLATFORMS="linux_gnu_x86_64
                  linux_gnu_aarch64
                  linux_musl_x86_64
                  windows_amd64"
TARGET_PY_VERSIONS="cp38
                    cp39
                    cp310"

cd $ROOT_PATH
rm -rf $DIST_PATH
mkdir -p $DIST_PATH

for TARGET_PLATFORM in $TARGET_PLATFORMS; do
    for TARGET_PY_VERSION in $TARGET_PY_VERSIONS; do
        export TARGET_PLATFORM TARGET_PY_VERSION
        $PYTHON -m doit clean_all
        $PYTHON -m doit
        cp $ROOT_PATH/build/py/dist/*.whl $DIST_PATH
    done
done

# IMAGES="build-hat-sbs:3.8-debian
#         build-hat-sbs:3.9-debian
#         build-hat-sbs:3.10-debian
#         build-hat-sbs:3.8-alpine
#         build-hat-sbs:3.9-alpine
#         build-hat-sbs:3.10-alpine"
# IMAGES="build-hat-sbs:3.8-debian
#         build-hat-sbs:3.9-debian
#         build-hat-sbs:3.8-alpine
#         build-hat-sbs:3.9-alpine
#         build-hat-sbs:3.10-alpine"
IMAGES=""

for IMAGE in $IMAGES; do
    $PYTHON -m doit clean_all
    IMAGE_ID=$(podman images -q $IMAGE)
    podman build -f $RUN_PATH/dockerfiles/$IMAGE -t $IMAGE .
    if [ -n "$IMAGE_ID" -a "$IMAGE_ID" != "$(podman images -q $IMAGE)" ]; then
        podman rmi $IMAGE_ID
    fi
    podman run --rm -v $DIST_PATH:/hat/dist -i $IMAGE /bin/sh - << EOF
set -e
pip3 install -r requirements.pip.dev.txt
doit clean_all
doit
cp build/py/dist/*.whl dist
EOF
done

$PYTHON -m doit clean_all
