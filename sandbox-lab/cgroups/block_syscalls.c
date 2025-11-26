#include <seccomp.h>
#include <stdio.h>

int main() {
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
    
    // Block these syscalls
    seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(mkdir), 0);
    seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(mkdirat), 0);
    seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(chmod), 0);
    seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(fchmod), 0);
    seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(fchmodat), 0);
    
    seccomp_export_bpf(ctx, 1);  // Export to stdout
    seccomp_release(ctx);
    return 0;
}
