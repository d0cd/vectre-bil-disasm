from .templates import *
from .aarch64_disasm_processor import AArch64DisassemblyProcessor
from .amd64_disasm_processor import AMD64DisassemblyProcessor

import angr


class VectreProgDefSerializer:
    angr_projects: angr.Project

    def __init__(self, _projects):
        self.angr_projects = _projects
        if self.angr_projects.arch == angr.archinfo.ArchAArch64():
            self.disas_processor = AArch64DisassemblyProcessor()
        elif self.angr_projects.arch == angr.rchinfo.ArchAMD64():
            self.disas_processor = AMD64DisassemblyProcessor()
        else:
            self.disas_processor = None

    def serialize_binaries(self):
        specs = []
        for proj in self.angr_projects:
            cfg = proj.analyses.CFGFast()
            nodes = cfg.graph.nodes()
            basic_blocks = []
            for node in nodes:
                basic_blocks.append(self.serialize_cfg_node(node))
            prog_name = self.angr_projects.filename.replace(".o", "").replace("/", "_").replace(".", "").replace("-", "_")
            bb_str = "\n".join(basic_blocks)
            specs.append(prog_def_template.substitute(PROG_NAME=prog_name, BASIC_BLOCKS=bb_str))
        return "\n\n".join(specs)

    def serialize_cfg_node(self, node: angr.knowledge_plugins.cfg.CFGNode):
        header = f"ENTRY_{node.block_id}:"
        if node.block is not None:
            disasm_str = str(node.block.disassembly)
            body = self.disas_processor.serialize_basic_block(disasm_str)
        else:
            body = ""
        return f"{header}\n{body}"
