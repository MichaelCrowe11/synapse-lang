"""Protocol modules of the Quantum Net runtime.

Every module here is a roadmap placeholder. Importing one succeeds; calling its
`run` raises NotImplementedError. Nothing in this package simulates, executes or
secures a protocol, and no security, fidelity or key-rate claim is made anywhere
in this package. Executable today: the flat network grammar (parse-only via
`synapse-qnet`) and the scheduler, fiber and entanglement-attempt primitives in
`qnet_runtime.sim_core`, `channels` and `entanglement`.
"""

ROADMAP = ("qkd_bb84", "teleport", "swapping", "purification")
STATUS = "roadmap"

__all__ = ["ROADMAP", "STATUS"]
