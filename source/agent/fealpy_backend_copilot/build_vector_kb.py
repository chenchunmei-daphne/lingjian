"""Build the current (v02) FEALPy capability vector database.

This compatibility entry point keeps the original command working while the
implementation lives in :mod:`build_vector_kb_v02`.
"""

from build_vector_kb_v02 import main


if __name__ == "__main__":
    main()
