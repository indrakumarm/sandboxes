import struct

# Block chmod, fchmod, fchmodat, fchmodat2, mkdir, mkdirat
filter_code = [
    # Load architecture (offset 4 in seccomp_data)
    (0x20, 0, 0, 0x00000004),  # ld [4]
    # Check if x86_64 (0xc000003e)
    (0x15, 0, 1, 0xc000003e),  # jeq #0xc000003e, true=next, false=skip
    (0x06, 0, 0, 0x00000000),  # ret KILL (wrong arch)
    
    # Load syscall number (offset 0)
    (0x20, 0, 0, 0x00000000),  # ld [0]
    
    # Block chmod (90)
    (0x15, 0, 1, 90),
    (0x06, 0, 0, 0x00000000),  # ret KILL
    
    # Block fchmod (91)
    (0x15, 0, 1, 91),
    (0x06, 0, 0, 0x00000000),  # ret KILL
    
    # Block mkdir (83)
    (0x15, 0, 1, 83),
    (0x06, 0, 0, 0x00000000),  # ret KILL
    
    # Block mkdirat (258)
    (0x15, 0, 1, 258),
    (0x06, 0, 0, 0x00000000),  # ret KILL
    
    # Block fchmodat (268)
    (0x15, 0, 1, 268),
    (0x06, 0, 0, 0x00000000),  # ret KILL
    
    # Block fchmodat2 (452)
    (0x15, 0, 1, 452),
    (0x06, 0, 0, 0x00000000),  # ret KILL
    
    # Allow everything else
    (0x06, 0, 0, 0x7fff0000),  # ret ALLOW
]

with open('/tmp/block_all.bpf', 'wb') as f:
    for insn in filter_code:
        f.write(struct.pack('=HBBI', insn[0], insn[1], insn[2], insn[3]))

print("Filter created!")
