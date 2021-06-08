
from lark import Lark

from .collect_inst_sigs import CollectInstructionNames
from .rename_instructions import RenameInstructions
from .vectre_serializer import VectreSerializer

from ..templates import inst_def_template

class AMD64DisassemblyProcessor:

    def __init__(self):
        self.arm_bb_parser = Lark.open('amd64_disasm_block.lark', rel_to=__file__, parser='lalr', start="block")

    def serialize_basic_block(self, bb_str):
        tree = self.arm_bb_parser.parse(bb_str)
        RenameInstructions().transform(tree)
        serialized = VectreSerializer().transform(tree)
        return serialized

    def generate_inst_def_skeleton(self, inst_str):
        tree = self.arm_bb_parser.parse(inst_str)
        RenameInstructions().transform(tree)

        collector = CollectInstructionNames()
        collector.visit(tree)

        inst_specs = []
        for inst in collector.inst_info:
            params = []
            arg_types = inst.split("__")[1:]
            for (i, typ) in enumerate(arg_types):
                if typ == "r":
                    params.append(f"arg{i}: reg_index_t")
                elif typ == "w":
                    params.append(f"arg{i}: word_t")
                elif typ[0] == "p":
                    params.append(f"arg{i}: word_t")
            arg_sig = ", ".join(params)
            inst_specs.append(inst_def_template.substitute(INST_NAME=inst, ARG_SIG=arg_sig))

        return "\n\n".join(inst_specs)

    def generate_platform_def_skeleton(self, inst_str):
        pass
