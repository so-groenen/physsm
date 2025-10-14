import subprocess
from pathlib import Path

DEFAULT_BUILD_DIR = "build"

class PyMake:
    def __init__(self, project_name: str, compiler: str):
        self.project_dir: Path   = Path.cwd()
        self.project_name        = project_name
        self.compiler: str       = compiler
        self.sources: list[Path] = []
        self.build_dir           = self.project_dir / DEFAULT_BUILD_DIR
    
    def set_project_dir(self, proj_dir: Path):
        self.project_dir = proj_dir
    
    def set_compiler(self, compiler):
        self.compiler = compiler
    
    def set_build_dir(self, build_dir: Path):
        self.build_dir = build_dir
        if not self.build_dir.exists():
            self.build_dir.mkdir(parents=True)
    
    def add_executable(self, src: Path):
        self.sources.append(src)
    
    def make(self):
        if self.compiler is None:
            raise ValueError("Missing compiler")
        
        src      = " ".join([str(s) for s in self.sources])
        out_path = self.build_dir.joinpath(self.project_name)
        errors   = []
        with subprocess.Popen(f"{self.compiler} {src} -o {out_path}", stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT, cwd=self.project_dir) as stream:
            if  stream.stdout is not None: 
                for lines in  stream.stdout:
                    print("", lines, end='')
                    errors.append(lines)
        if len(errors):
            print("Compilation unsuccessful")
        elif out_path.exists() or out_path.with_suffix(".exe").exists() :
            print("Compilation successful")
        else:
            print("Error no output")

if __name__ == "__main__":

    project_dir  = Path.cwd()
    build_dir    = project_dir / "build"
    main         = project_dir / "src"   / "main.c"

    project = PyMake(project_name="c_example", compiler="clang")
    project.add_executable(main)
    project.set_build_dir(build_dir)
    project.make()   
 
