from distutils.sysconfig import get_config_var

is_pyz = get_config_var("DESTLIB").startswith('/usr/lpp/IBM/cyp')

if is_pyz:
    # we want to build with the same tools that were used to build python
    os.environ["CC"] = "/bin/xlclang"    
    os.environ["LDSHARED"] = "/bin/xlclang"
    os.environ["LINKCC"] = "/bin/xlclang"

from setuptools import setup, Extension

if is_pyz:
    ext_names=["_bytearray", "_csv_info", "_fcntl", "_posix", "_system_call"]
else:
    ext_names=["_bytearray", "_csv_info"]
ext_modules=[Extension("zos.%s" % name, ["zos/%s.c" % name]) for name in ext_names]

setup(
    name="zos_python",
    version="0.1",
    namespace_packages=["zos"],
    ext_modules=ext_modules,
    author="Richard Harris",
    author_email="rharriszzz@gmail.com",
)
