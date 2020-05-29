# -*- coding: UTF-8 -*-
import glob
import json
import re
import shutil
import os
from conans.model import Generator
from conans import ConanFile
from conans import tools

class PcfixGenerator(Generator):

    @property
    def filename(self):
        pass

    @property
    def content(self):
        ret = dict()
        prefix_pat = re.compile('^prefix=(.*)$')

        for dep_name in self.conanfile.deps_cpp_info.deps:
            print('dep_name={}'.format(dep_name))
            rootpath = self.conanfile.deps_cpp_info[dep_name].rootpath
            print('rootpath={}'.format(rootpath))
            pkgconfig_path = os.path.join(rootpath, 'lib', 'pkgconfig')
            dst_pkgconfig_dir = os.path.join(self.output_path, 'pkgconfig')
            os.makedirs(dst_pkgconfig_dir, exist_ok=True)
            pc_file_list = []
            modified_list = []
            prefix_set = set()
            for pc_file in glob.glob(os.path.join(pkgconfig_path, '*.pc')):
                print('pc_file={}'.format(pc_file))
                if os.path.isfile(pc_file):
                    pc_filename = os.path.basename(pc_file)
                    pkg_name = os.path.splitext(pc_filename)[0]
                    dst = os.path.join(dst_pkgconfig_dir, pc_filename)
                    shutil.copy(pc_file, dst)
                    prefix = None
                    with open(pc_file) as _f:
                        _lines = _f.readlines()
                        for _line in _lines:
                            _line = _line.strip()
                            _match = prefix_pat.match(_line)
                            if _match:
                                prefix = _match.group(1)
                                break
                    if prefix:
                        prefix_set.add(prefix)
                        if os.path.exists(prefix):
                            self.conanfile.output.info('{} exists, do not modify {}'.format(prefix, pc_file))
                        else:
                            self.conanfile.output.warn('{} does not exist, replace it with {} in {}'.format(prefix, rootpath, pc_file))
                            # use replace path instead of replace prefix
                            # to fix some legacy pc file which does not
                            # use ${prefix} in other variable
                            tools.replace_path_in_file(
                                file_path=dst,
                                search=prefix,
                                replace=rootpath,
                                strict=False
                            )
                            modified_list.append(pc_filename)
                    pc_file_list.append(pc_filename)
            data_dict = dict(
                all=pc_file_list,
                modified=modified_list,
                old_prefixs=list(prefix_set)
            )
            ret['pclist-%s.json'%dep_name] = json.dumps(data_dict, indent=4, sort_keys=True)
        return ret


class MyCustomGeneratorPackage(ConanFile):
    name = "PcFixGen"
    version = "0.1"
    url = "https://github.com/braindevices/conan-pcfix-generator.git"
    license = "MIT"