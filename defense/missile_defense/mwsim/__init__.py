"""mwsim — the multi-orbit missile-warning trade-space engine.

Built for SBIR topic DAF26BX06-NV510. See PLAN.md for the task ledger; module docstrings
carry the task ID they implement.

Everything here runs on published, public-domain inputs: CelesTrak/Space-Track orbital
elements, published equations of motion, and open fact-sheet constellation geometry. Any
quantity that is classified in reality is a swept parameter here, never a sourced value.
"""

__version__ = "0.1.0"
