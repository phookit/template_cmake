
def _mk_comment(comment):
    print(f"_mk_comment: {comment}")
    if not comment:
        return []
    multi_line = comment.split("\n")
    res = []
    for line in multi_line:
        res.append(f"# {line}")
    return res

_INDENT_PER_LEVEL = 2

class Branch:
    def __init__(self, *, cond="", comment="", level=0):
        self._output = []
        self._cond = cond
        self._level = level
        self._branch_indent = " " * (level * _INDENT_PER_LEVEL)
        self._comment = _mk_comment(comment)
        print(f"BRANCH COND:{cond}")

    @property
    def output(self):
        return self._output

    @property
    def is_cond(self):
        return self._cond != ""

    def append(self, val):
        print(f"APPEND:val={val} self._output={self._output}")
        if isinstance(val, (str, Branch)):
            self._output.append(val)
        else:  # list
            self._output.extend(val)

    def _write_item(self, item, out_file, level):
        print(f"\n\n!!!!!! GOT BRANCH ITEM:\"{item}\"\n\n")
        if isinstance(item, Branch):
            print("DO BRANCH")
            item.write(out_file, level+1)
        elif isinstance(item, str):
            print("DO STR")
            #s = b.ljust(indent, " ")
            pad = " " * (level * _INDENT_PER_LEVEL)
            s = f"{pad}{item}"
            out_file.write(f"{s}\n")
        else:  # list
            print("************* DO LIST")
            for item in b:
                self._write_item(item, out_file, level)


    def write(self, out_file, level=0):
        if self._comment:
            print(f"Adding comment. level={level}")
            lev = level
            if lev > 0:
                lev -= 1
            pad = " " * (lev * _INDENT_PER_LEVEL)
            print(f"  got pad=\"{pad}\"")
            for c in self._comment:
                out_file.write(f"{pad}{c}")
            out_file.write("\n")
        if self._cond:
            lev = level
            if lev > 0:
                lev -= 1
            pad = " " * (lev * _INDENT_PER_LEVEL)
            out_file.write(f"{pad}if({self._cond})\n")

        for item in self._output:
            self._write_item(item, out_file, level)

        if self._cond:
            if level > 0:
                level -= 1
            pad = " " * level
            out_file.write(f"{pad}endif() # {self._cond}\n\n")


class CMakeWrapper:
    """A Python class to wrap common CMake functions with keyword arguments, returning strings directly."""

    def branch(self):
        return Branch()

    def minimum_cmake_version(self, min_ver, max_ver):
        return f"cmake_minimum_required(VERSION {min_ver}...{max_ver})"

    def project(self, name, *, version="0.1", description="", languages="CXX", comment=""):
        result = _mk_comment(comment)
        result.append(f"""
project(
  {name}
  VERSION {version}
  DESCRIPTION \"{description}\"
  LANGUAGES {languages}
)
""")
        result.append("")
        return result

    def conditional(self, cond, *, level=0, comment=""):
        return Branch(cond=cond,
                comment=comment, level=level)

    def cond_main_project(self, comment="", level=0):
        return Branch(cond="CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME",
                comment=comment, level=level)

    def add_test(self, name, command, *, comment=""):
        result = _mk_comment(comment)
        result.append(f"add_test(NAME {name} COMMAND {command})")
        return result

    def add_executable(self, name: str, sources: list[str], **kwargs) -> str:
        """Wrapper for CMake's add_executable function.
        
        Args:
            name: Name of the executable.
            sources: List of source files.
            **kwargs: Optional parameters like 'win32', 'macosx_bundle'.
        
        Returns:
            CMake command as a string.
        """
        command = f"add_executable({name}"
        if kwargs.get('win32'):
            command += " WIN32"
        if kwargs.get('macosx_bundle'):
            command += " MACOSX_BUNDLE"
        command += " " + " ".join(sources) + ")"
        return command
 
    def source_group(self, tree_dir, prefix, files, *, comment=""):
        result = _mk_comment(comment)
        result.append(f"""source_group(
  TREE \"${{PROJECT_SOURCE_DIR}}/{tree_dir}\"
  PREFIX \"{prefix}\"
  FILES {" ".join(files)}
)""")
        return result

    def target_include_directories(self, target: str, dirs: list[str], **kwargs) -> str:
        """Wrapper for CMake's target_include_directories function.
        
        Args:
            target: Name of the target.
            libraries: List of libraries to link.
            **kwargs: Optional parameters like 'PUBLIC', 'PRIVATE', 'INTERFACE'.
        
        Returns:
            CMake command as a string.
        """
        visibility = kwargs.get('visibility', '').upper()
        if visibility not in ['PUBLIC', 'PRIVATE', 'INTERFACE', '']:
            raise ValueError("Visibility must be PUBLIC, PRIVATE, or INTERFACE")
        command = f"target_include_directories({target}"
        if visibility:
            command += f" {visibility}"
        command += " " + " ".join(dirs) + ")"
        return command
     

    def target_include_libraries(self, target: str, includes: list[str], **kwargs) -> str:
        """Wrapper for CMake's target_include_libraries function.
        
        Args:
            target: Name of the target.
            libraries: List of libraries to link.
            **kwargs: Optional parameters like 'PUBLIC', 'PRIVATE', 'INTERFACE'.
        
        Returns:
            CMake command as a string.
        """
        visibility = kwargs.get('visibility', '').upper()
        if visibility not in ['PUBLIC', 'PRIVATE', 'INTERFACE', '']:
            raise ValueError("Visibility must be PUBLIC, PRIVATE, or INTERFACE")
        command = f"target_include_libraries({target}"
        if visibility:
            command += f" {visibility}"
        command += " " + " ".join(includes) + ")"
        return command
     
   
    def target_link_libraries(self, target: str, libraries: list[str], **kwargs) -> str:
        """Wrapper for CMake's target_link_libraries function.
        
        Args:
            target: Name of the target.
            libraries: List of libraries to link.
            **kwargs: Optional parameters like 'PUBLIC', 'PRIVATE', 'INTERFACE'.
        
        Returns:
            CMake command as a string.
        """
        visibility = kwargs.get('visibility', '').upper()
        if visibility not in ['PUBLIC', 'PRIVATE', 'INTERFACE', '']:
            raise ValueError("Visibility must be PUBLIC, PRIVATE, or INTERFACE")
        command = f"target_link_libraries({target}"
        if visibility:
            command += f" {visibility}"
        command += " " + " ".join(libraries) + ")"
        return command
     
    def target_compile_features(self, target: str, std: str, **kwargs) -> str:
        """Wrapper for CMake's target_compile_features function.
        
        Args:
            target: Name of the target.
            libraries: List of libraries to link.
            **kwargs: Optional parameters like 'PUBLIC', 'PRIVATE', 'INTERFACE'.
        
        Returns:
            CMake command as a string.
        """
        visibility = kwargs.get('visibility', '').upper()
        if visibility not in ['PUBLIC', 'PRIVATE', 'INTERFACE', '']:
            raise ValueError("Visibility must be PUBLIC, PRIVATE, or INTERFACE")
        command = f"target_compile_features({target}"
        if visibility:
            command += f" {visibility}"
        command += f" {std})"
        return command
    
    def add_library(self, name: str, sources: list[str], **kwargs) -> str:
        """Wrapper for CMake's add_library function.
        
        Args:
            name: Name of the library.
            sources: List of source files.
            **kwargs: Optional parameters like 'type' (STATIC, SHARED, MODULE), 'ALIAS'.
        
        Returns:
            CMake command as a string.
        """
        lib_type = kwargs.get('type', '').upper()
        if lib_type and lib_type not in ['STATIC', 'SHARED', 'MODULE']:
            raise ValueError("Library type must be STATIC, SHARED, or MODULE")
        command = f"add_library({name}"
        if lib_type:
            command += f" {lib_type}"
        if kwargs.get('alias'):
            command += " ALIAS"
        command += " " + " ".join(sources) + ")"
        return command
   
    def include(self, name, *, comment=""):
        result = _mk_comment(comment)
        result.append(f"include({name})")
        result.append("")
        return result

    def include_directories(self, directories: list[str], **kwargs) -> str:
        """Wrapper for CMake's include_directories function.
        
        Args:
            directories: List of include directories.
            **kwargs: Optional parameters like 'BEFORE', 'AFTER', 'SYSTEM'.
        
        Returns:
            CMake command as a string.
        """
        command = "include_directories("
        if kwargs.get('before'):
            command += "BEFORE "
        if kwargs.get('after'):
            command += "AFTER "
        if kwargs.get('system'):
            command += "SYSTEM "
        command += " ".join(directories) + ")"
        return command
   
    def set(self, var, value, *, comment=""):
        result = _mk_comment(comment)
        result.append(f"set({var} {value})")
        result.append("")
        return result

    def set_property(self, scope: str, target: str, property_name: str, value: str, **kwargs) -> str:
        """Wrapper for CMake's set_property function.
        
        Args:
            scope: Scope of the property (e.g., TARGET, SOURCE, DIRECTORY).
            target: Target name or item.
            property_name: Name of the property to set.
            value: Value to set for the property.
            **kwargs: Optional parameters like 'APPEND', 'APPEND_STRING'.
        
        Returns:
            CMake command as a string.
        """
        command = f"set_property({scope} {target} PROPERTY {property_name} {value}"
        if kwargs.get('append'):
            command += " APPEND"
        if kwargs.get('append_string'):
            command += " APPEND_STRING"
        command += ")"
        return command
    
    def add_compile_options(self, options: list[str], **kwargs) -> str:
        """Wrapper for CMake's add_compile_options function.
        
        Args:
            options: List of compile options.
            **kwargs: Optional parameters (currently unused, for future extensibility).
        
        Returns:
            CMake command as a string.
        """
        return f"add_compile_options({' '.join(options)})"
    
    def add_definitions(self, definitions: list[str], **kwargs) -> str:
        """Wrapper for CMake's add_definitions function.
        
        Args:
            definitions: List of definitions (e.g., -DDEFINE_NAME).
            **kwargs: Optional parameters (currently unused, for future extensibility).
        
        Returns:
            CMake command as a string.
        """
        return f"add_definitions({' '.join(definitions)})"

    def find_package(self, pkg, *, comment="", required=False):
        result = _mk_comment(comment)
        req = " REQUIRED" if required else ""
        result.append(f"find_package({pkg}{req})")
        result.append("")
        return result

    def add_subdirectory(self, directory, *, comment=""):
        result = _mk_comment(comment)
        result.append(f"add_subdirectory({directory})")
        result.append("")
        return result

    def fetch_content_declare_available(self, name, git_repo, git_tag, *, comment=""):
        result = _mk_comment(comment)
        result.append("FetchContent_Declare(")
        result.append(f"  {name}")
        result.append(f"  GIT_REPOSITORY {git_repo}")
        result.append(f"  GIT_TAG {git_tag}")
        result.append(")")
        result.append(f"FetchContent_MakeAvailable({name})")
        result.append("")
        return result

    def add_doxygen(self, docs_dir, *, comment=""):
        result = _mk_comment(comment)
        result.append("find_package(Doxygen)")
        result.append("if(Doxygen_FOUND)")
        result.append(f"  add_subdirectory({docs_dir})")
        result.append("else()")
        result.append("  message(STATUS \"Doxygen not found, not building docs\")")
        result.append("endif()")
        result.append("")
        return result


# Example usage:
if __name__ == "__main__":
    cmake = CMakeWrapper()
    commands = [
        cmake.add_executable(name="myapp", sources=["main.cpp", "utils.cpp"], win32=True),
        cmake.target_link_libraries(target="myapp", libraries=["pthread", "m"], visibility="PUBLIC"),
        cmake.add_library(name="mylib", sources=["lib.cpp"], type="STATIC"),
        cmake.include_directories(directories=["/usr/include", "./include"], system=True),
        cmake.set_property(scope="TARGET", target="myapp", property_name="CXX_STANDARD", value="11"),
        cmake.add_compile_options(options=["-Wall", "-O2"]),
        cmake.add_definitions(definitions=["-DDEBUG"])
    ]
    # Write to CMakeLists.txt manually
    with open("CMakeLists.txt", "w") as f:
        f.write("# Generated CMakeLists.txt\n" + "\n".join(commands) + "\n")
    print("\n".join(commands))
