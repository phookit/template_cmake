# template_cmake

## Usage

    python3 src/cmakegen/main.py -o /tmp -n "MyProject"
    cd /tmp/MyProject
    cmake -S . -B build
    cmake --build build
    cmake --build build --target test
    cmake --build build --target docs

## Generated files

### `CMakeLists.txt`

Top level CMakeLists.txt. Contains:

* minimum cmake version
* Project info, name, version, description, languages (`project` section)
* Conditional for top level CMakeLists.txt
    * Sets cmake extentions (use c++xx instead of g++xx)
    * Sets properties (`USE_FOLDERS`, etc)
    * `ìnclude`s CTest
    * Finds/uses Doxygen
* `ìnclude`s other stuff (FetchContent)
* `find_package`s (Boost/whatever you need to add)
* `FetchContent_Declare`s for whatever libraries are required
* Adds the `src`sub dir for librariy files
* Adds the `àpps` sub dir for `main`applications.
* Adds the `tests`sub directory if top level CMakeLists.txt

### `include/PROJ_NAME/`

* Creates the include directory structure. This is where publicly available library headers should go. By default a header file named `PROJ_NAME.h[pp]`will be generated depending on the chosen language.

### `src/CMakeLists.txt`

* Adds a `HEADER_LIST`of files either via globbing or by explicitly listing header files from the ìnclude directory.
* `àdd_library` with source files and library name.
* `target_include_directories` for publicly available headers.
* `target_link_libraries` for linking libs that our library needs.
* `target_compile_features` for C++ std if applicable (should this be in top level makefile instead?)
* Adds IDE meta for IDEs (`source_group`)

The `src`dir will also contain our library code. By default a source file name `PROJ_NAME.c[pp]`will be generated.

### `tests/CMakeLists.txt`

* `FetchContent_Declare`unit test lib (Catch2 by default)
* `àdd_executable` for unit tests, lists unit test source files from the `tests`directory.
* `target_compile_features` for C++ std used by unit tests.
* `target_link_libraries` for linking libs (our lib and Carch2 lib) that our unit tests need.
* `àdd_test` to register unit tests.

The `tests`dir will also include unit test source code. Ideally one source file for each library file. Source filenames will be prefixed with `test_`for now.

### `docs/CMakeLists.txt`

* sets DocyGen options (`DOXYGEN_EXTRACT_ALL`, `DOXYGEN_BUILTIN_STL_SUPPORT`, etc)
* `docygen_add_docs`from all include header files into a `mainpage.md` file.

### `àpps/CMakeLists.txt`

* Adds `main`source files as named executables.
* Sets `target_compile_features`for C++ std
* `target_link_libraries`to link libs for the named executable.

Ideally each application should consist of a single source with a `main`function and link to a library with required functionality.

By default a source file name `{PROJ_NAME}_main.c[pp]` will be generated.

### `cmake/`

Add .cmake files for whatever reason.


## Design

CMakeLists use `àdd_executable`, `target_link_libraries`, etc, etc that require a target name. The target can be a lib or an executable, etc.The Python app will also have a CMakeList class that can generate the strings to be added to a CMakeLists.txt file via methods that match the various functions available in CMake (`àdd_executable`, etc).

Command line parameters to the Python app specify:

* The output directory.
* The name of the project.
* The language (C or C++). Affects generated source file names (.cpp or .c, etc). For C++ this may also include the std. i.e. `c++17`.
<<<<<<< HEAD
* The executable apps name(s). This will cause the `àpps` directory to be created with an example app and suitable CMakeLists.txt.
* The library name(s). This will cause the `src` directory to be created Each sub dir will have a suitable CMakeLists.txt file generated along with an example lib source file.

### Library

    - src/
        libname.c[pp]
        CMakeLists.txt
    - inlude/PROJ_NAME/
        libname.h[pp]




=======
* Whether to create an executable or not.
* Whether to create a library or not.
* Whether to create documentaion or not.
>>>>>>> 1f61d4c (allow other chars in project name)
