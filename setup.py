#for me:
# https://setuptools.readthedocs.io/en/latest/setuptools.html

from distutils import ccompiler, sysconfig
from distutils.command.build_ext import build_ext

from setuptools import Extension, setup

"""
PLATFORM_MINGW = "mingw" in ccompiler.get_default_compiler()

prefix = sysconfig.get_config_var("prefix")

        for k in ("CFLAGS", "CPPFLAGS", "LDFLAGS"):
            if k in os.environ:
                for match in re.finditer(r"-I([^\s]+)", os.environ[k]):
                    _add_directory(include_dirs, match.group(1))
                for match in re.finditer(r"-L([^\s]+)", os.environ[k]):
                    _add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables:
        for k in ("C_INCLUDE_PATH", "CPATH", "INCLUDE"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(include_dirs, d)

        for k in ("LD_RUN_PATH", "LIBRARY_PATH", "LIB"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(library_dirs, d)

        prefix = sysconfig.get_config_var("prefix")
        if prefix:
            _add_directory(library_dirs, os.path.join(prefix, "lib"))
            _add_directory(include_dirs, os.path.join(prefix, "include"))
"""

setup(
    name="zos_python",
    version="0.1",
    description="z/OS Compatibility for Python",
    #long_description=_read("README.rst").decode("utf-8"),
    #license="?",
    author="Richard Harris",
    author_email="rharris@pobox.com",
    #url="https://",
    project_urls={
        #"Documentation": "https://",
        "Source": "https://github.com/rharriszzz/zos_python",
        "Funding": "https://rocketsoftware.com"
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Other/Proprietary License", # not sure what license this will have
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: C",
        "Operating System :: IBM :: z/OS",
        ],
    python_requires=">=3.6",
    ext_modules=[Extension("PIL._imaging", ["_imaging.c"])],
    include_package_data=True,
    packages=["zos"],
    package_dir={"": "src"},
    #keywords=[""],
    zip_safe=not (debug_build() or PLATFORM_MINGW),
)
