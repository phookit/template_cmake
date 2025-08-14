#!/bin/python3

import argparse
import os
import re
from pathlib import Path

from cmake_wrapper import CMakeWrapper

def create_dirs(path):
    path.mkdir(parents=True, exist_ok=True)


class CMakeGen:
    def __init__(self, args):
        self._args = args
        self._lc_project_name = self._args.project_name.lower()
        # normalise top level dir name
        self._top_level_dir = re.sub(r"[\s]", "_", self._args.project_name)
        # normalise the project name to use for filenames, header directives, etc
        self._norm_project_name = re.sub(r"[\s\.-]", "_", self._args.project_name)
        self._root_project_path = Path(self._args.output_dir) / self._top_level_dir
        # get our header dir name
        self._proj_include_dir = self._root_project_path / "include" / self._norm_project_name
        # create a safe executable filename
        self._app_name = re.sub(r"[\s]", "_", self._args.project_name).lower()
        # normalise the lib target name
        self._norm_lib_target = f"{self._norm_project_name}_lib_target"
        self._norm_app_target = f"{self._norm_project_name}_app_target"

        print(f"TLD:{self._top_level_dir}")
        print(f"NPP:{self._norm_project_name}")
        print(f"RPP:{self._root_project_path}")
        print(f"INC:{self._proj_include_dir}")

        hdr_ext = "h"
        src_ext = "c"
        if self._args.language == "CXX":
            hdr_ext += "pp"
            src_ext += "pp"
        self._src_filename = f"{self._norm_project_name.lower()}.{src_ext}"
        self._hdr_filename = f"{self._norm_project_name.lower()}.{hdr_ext}"

    def write_cmakelists(self, out_file, root_branch):
        with open(out_file, "w") as f:
            root_branch.write(f)

    def init_dir_structure(self):
        create_dirs(self._proj_include_dir)
        create_dirs(self._root_project_path / "src")
        create_dirs(self._root_project_path / "apps")
        create_dirs(self._root_project_path / "tests")
        if not self._args.no_docs:
            create_dirs(self._root_project_path / self._args.docs_dir)

    def init_example_source(self):
        # top level include
        include_filename = self._proj_include_dir / f"{self._hdr_filename}"
        with open(include_filename, "w") as f:
            f.write(f"""#ifndef {self._norm_project_name}_H
#define {self._norm_project_name}_H

int example(int a);

#endif
""")

        # lib source
        if not self._args.no_lib:
            lib_src_file = self._root_project_path / "src" / f"{self._src_filename}"
            with open(lib_src_file, "w") as f:
                f.write(f"""#include \"{self._proj_include_dir}/{self._hdr_filename}\"
int example(int a)
{{
    return a * 2;
}}
""")

        # app source
        if not self._args.no_app:
            app_src_file = self._root_project_path / "apps" / f"{self._src_filename}"
            with open(app_src_file, "w") as f:
                f.write(f"""#include \"{self._proj_include_dir}/{self._hdr_filename}\"

int main(int argc, char* argv[])
{{
    int b = example(12);
    return 0;
}}

""")
        # test source
        test_src_file = self._root_project_path / "tests" / f"test{self._src_filename}"
        with open(test_src_file, "w") as f:
            f.write(f"""#define CATCH_CONFIG_MAIN
#include <catch2/catch.hpp>
#include \"{self._proj_include_dir}/{self._hdr_filename}\"

TEST_CASE( "Quick check", "[main]" ) 
{{
    int res = example(21);
    REQUIRE( res == 42 );
}}
""")


    def gen_main_cmakelists(self):
        cm = CMakeWrapper()
        main_branch = cm.branch()
        main_branch.append( cm.minimum_cmake_version("3.20", "4.0"))
        main_branch.append( cm.project(self._norm_project_name, languages=self._args.language))
        main_proj_branch = cm.cond_main_project(
            comment="Only do these if this is the main project, and not if it is included through add_subdirectory")
        main_proj_branch.append( cm.set("CMAKE_CXX_EXTENSIONS", "OFF",
            comment="Lets ensure -std=c++xx instead of -std=g++xx"))
        main_proj_branch.append( cm.set_property("GLOBAL", "", "USE_FOLDERS", "ON",
            comment="Lets nicely support folders in IDEs"))
        main_proj_branch.append( cm.include("CTest",
            comment="""Testing only available if this is the main app
Note this needs to be done in the main CMakeLists
since it calls enable_testing, which must be in the
main CMakeLists.
"""))
        if not self._args.no_docs:
            main_proj_branch.append(cm.add_doxygen(self._args.docs_dir,
                comment="""Docs only available if this is the main app
NOTE: graphviz is required:
    sudo apt install graphviz"""))
        main_branch.append( main_proj_branch )
       
        main_branch.append(cm.include("FetchContent",
            comment="""FetchContent added in CMake 3.11, downloads during the configure step
FetchContent_MakeAvailable was added in CMake 3.14; simpler usage"""))

        main_branch.append(cm.find_package("Boost", required=True,
            comment="""This is header only, so could be replaced with git submodules or FetchContent
Adds Boost::boost"""))

        '''
        main_branch.append(cm.fetch_content_declare_available("fmtlib",
            "https://github.com/fmtlib/fmt.git",
            "5.3.0",
            comment="""ormatting library.
Adds fmt::fnt"""))
        '''
        if not self._args.no_lib:
            main_branch.append(cm.add_subdirectory("src",
                comment="The compiled library code is here"))

        if not self._args.no_app:
            main_branch.append(cm.add_subdirectory("apps",
                comment="The executable code is here"))

        test_branch = cm.conditional("(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME OR MODERN_CMAKE_BUILD_TESTING) AND BUILD_TESTING",
                comment="""Testing only available if this is the main app
Emergency override MODERN_CMAKE_BUILD_TESTING provided as well""")
        test_branch.append(cm.add_subdirectory("tests"))
        main_branch.append(test_branch)

        out_file = self._root_project_path / "CMakeLists.txt"
        self.write_cmakelists(out_file, main_branch)

    def gen_apps(self):
        if self._args.no_app:
            return
        cm = CMakeWrapper()
        main_branch = cm.branch()
        main_branch.append(cm.add_executable(self._norm_app_target,
            [self._src_filename]))
        main_branch.append(cm.target_compile_features(self._norm_app_target,
            "cxx_std_11", visibility="PRIVATE"))
        main_branch.append(cm.target_link_libraries(self._norm_app_target,
            [self._norm_lib_target], visibility="PRIVATE"))
        main_branch.append(cm.set_target_properties(self._norm_app_target,
            [("OUTPUT_NAME", f"{self._app_name}"),],
            comment="Explicitly set the filename for the executable file"))
        out_file = self._root_project_path / "apps" / "CMakeLists.txt"
        self.write_cmakelists(out_file, main_branch)

    def gen_libs(self):
        if self._args.no_lib:
            return
        cm = CMakeWrapper()
        hdr_list = f"${{{self._norm_project_name}_SOURCE_DIR}}/include/{self._norm_project_name}/{self._hdr_filename}"
        main_branch = cm.branch()
        main_branch.append(cm.set("HEADER_LIST", hdr_list))
        main_branch.append(cm.add_library(self._norm_lib_target,
            [self._src_filename, "${HEADER_LIST}"]))
        main_branch.append(cm.target_include_directories(self._norm_lib_target,
            ["../include"], visibility="PUBLIC"))
        main_branch.append(cm.target_link_libraries(self._norm_lib_target,
            ["Boost::boost"], visibility="PRIVATE"))
        main_branch.append(cm.target_compile_features(self._norm_lib_target,
            "cxx_std_11", visibility="PUBLIC"))
        main_branch.append(cm.source_group("include", "Header files", ["${HEADER_LIST}"]))

        out_file = self._root_project_path / "src" / "CMakeLists.txt"
        self.write_cmakelists(out_file, main_branch)

    def gen_docs(self):
        if self._args.no_docs:
            return
        cm = CMakeWrapper()
        main_branch = cm.branch()
        main_branch.append("""set(DOXYGEN_EXTRACT_ALL YES)
set(DOXYGEN_BUILTIN_STL_SUPPORT YES)

doxygen_add_docs(docs modern/lib.hpp "${CMAKE_CURRENT_SOURCE_DIR}/mainpage.md"
                 WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/include")
""")
        out_file = self._root_project_path / "docs" / "CMakeLists.txt"
        self.write_cmakelists(out_file, main_branch)

    def gen_tests(self):
        test_name = f"test_{self._norm_lib_target}"
        src_file = f"test{self._src_filename}"
        cm = CMakeWrapper()
        main_branch = cm.branch()
        #main_branch.append(cm.fetch_content_declare_available("catch",
        #    "https://github.com/catchorg/Catch2.git",
        #    "v2.13.6"))
        main_branch.append(cm.add_executable(test_name,
            [src_file]))
        main_branch.append(cm.target_compile_features(test_name,
            "cxx_std_17", visibility="PRIVATE"))
        main_branch.append(cm.target_link_libraries(test_name,
            [f"{self._norm_lib_target}"], visibility="PRIVATE"))
        #[f"{self._norm_lib_target}", "Catch2::Catch2"], visibility="PRIVATE"))
        main_branch.append(cm.add_test(f"{test_name}_test", test_name)) 
        out_file = self._root_project_path / "tests" / "CMakeLists.txt"
        self.write_cmakelists(out_file, main_branch)

def main():
    parser = argparse.ArgumentParser(description="Generate CMakeLists.txt for C/C++ projects")
    # mandatory args
    req_named = parser.add_argument_group('Required arguments')
    req_named.add_argument("-o", "--output-dir", default=".", help="Output directory", required=True)
    req_named.add_argument("-n", "--project-name", help="Project name", required=True)
    # optional args
    parser.add_argument("-l", "--language", choices=["C", "CXX", "c++11", "c++14", "c++17", "c++23"], default="CXX",
                       help="Programming language (C or C++)")
    parser.add_argument("--no-app", action="store_true", help="Do not generate executable")
    parser.add_argument("--no-lib", action="store_true", help="Do not generate libraries")
    parser.add_argument("--no-docs", action="store_true", help="Do not generate documanetation")
    parser.add_argument("--docs-dir", help="Documantation directory",
                       default="docs")
    args = parser.parse_args()

    if args.language.startswith("c++"):
        args.language = "CXX"
    output_dir = args.output_dir
    project_name = args.project_name
    language = args.language
    print(f"Output dir: {output_dir}")
    print(f"Project name: {project_name}")
    print(f"Language: {language}")

    mkgen = CMakeGen(args)
    mkgen.init_dir_structure()
    mkgen.gen_main_cmakelists()
    mkgen.gen_apps()
    mkgen.gen_libs()
    mkgen.gen_tests()
    mkgen.gen_docs()
    mkgen.init_example_source()

if __name__ == "__main__":
    main()

