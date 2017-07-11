"""
This experiment instruments the parent if any given SCoP and prints the reason
why the parent is not part of the SCoP.
"""
import benchbuild.experiment as exp
import benchbuild.extensions as ext


class PProfExperiment(exp.Experiment):
    """This experiment instruments the parent if any given SCoP and prints the
    reason why the parent is not part of the SCoP."""

    NAME = "profileScopDetection"

    def actions_for_project(self, project):
        project.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                "-O3",
                "-mllvm", "-profileScopDetection"]
        project.ldflags = ["-lpjit"]
        project.runtime_extension = ext.RunWithTime(
                ext.RuntimeExtension(project, self, config={})
            )

        return self.default_runtime_actions(project)