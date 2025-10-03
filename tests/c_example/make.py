import subprocess
from pathlib import Path

class PyMake:
    def __init__(self, project_dir: Path, project_name: str):
        self.project_dir         = project_dir
        self.project_name        = project_name
        self.compiler            = None
        self.sources: list[Path] = []
        self.build_dir           = self.project_dir.joinpath("build")
    
    def set_compiler(self, compiler):
        self.compiler = compiler
    
    def set_build_dir(self, build_dir: Path):
        self.build_dir = build_dir
        if not self.build_dir.exists():
            self.build_dir.mkdir(parents=True)
    
    def append_source(self, src: Path):
        self.sources.append(src)
    
    def compile(self):
        if self.compiler is None:
            raise ValueError("Missing compiler")
        
        src      = " ".join([str(s) for s in self.sources])
        out_path = self.build_dir.joinpath(self.project_name)
        
        with subprocess.Popen(f"{self.compiler} {src} -o {out_path}", stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT, cwd=self.project_dir) as stream:
            for lines in stream.stdout:
                print("", lines, end='')
        if out_path.exists() or out_path.with_suffix(".exe").exists():
            print("Compilation succesfull")
            
if __name__ == "__main__":

    project_name = "c_example"
    project_dir  = Path.cwd()
    build_dir    = project_dir.joinpath("build")
    src_file     = project_dir.joinpath("src").joinpath("main.c")

    project = PyMake(project_dir, project_name)
    project.append_source(src_file)
    project.set_build_dir(build_dir)
    project.set_compiler("clang")
    project.compile()   
 
