#!/usr/bin/env python3
"""Stage B4 cyclic-time anchored C12 readout audit.

Public entry point for Stage B4.  This now delegates to the real-time UTC
implementation so Stage B4 is not run with a session-normalized proxy phase.
"""

from test_Stage_B4_real_time_anchored_C12_readout import main


if __name__ == "__main__":
    main()
