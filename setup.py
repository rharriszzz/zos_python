from distutils.sysconfig import get_config_var

is_pyz = get_config_var("DESTLIB").startswith('/usr/lpp/IBM/cyp')

if is_pyz:
    # we want to build with the same tools that were used to build python
    os.environ["CC"] = "/bin/xlclang"    
    os.environ["LDSHARED"] = "/bin/xlclang"
    os.environ["LINKCC"] = "/bin/xlclang"

from setuptools import setup, Extension, find_packages

def extensions_list(package, names):
    directory = package.replace('.', '/')
    return [Extension(package+'.'+name, [directory+'/'+name+'.c']) for name in names]

ext_modules = extensions_list("zos_python.profile", ["_csv_info"])
if is_pyz:
    ext_modules += extensions_list("zos_python.builtins", ["_bytearray", "_fcntl", "_posix", "_system_call"])

setup(
    name="zos_python",
    version="0.1",
    packages=find_packages(),
    ext_modules=ext_modules,
    author="Richard Harris",
    author_email="rharriszzz@gmail.com",
)
