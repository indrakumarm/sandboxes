// seccomp_loader.c
#define _GNU_SOURCE
#include <seccomp.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

/*
 Minimal seccomp loader that:
  - logs progress to /workspace/sec_loader.log
  - allows a practical set of syscalls for a shell in a minimal rootfs
  - blocks others (default kill)
 Note: Tune syscall list to your needs; this is intentionally conservative yet usable.
*/

static void logmsg(FILE *f, const char *msg) {
    if (!f) return;
    fprintf(f, "%s\n", msg);
    fflush(f);
}

int add_allow_many(scmp_filter_ctx ctx, const int *syscalls, size_t n, FILE *log) {
    for (size_t i = 0; i < n; ++i) {
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, syscalls[i], 0) < 0) {
            fprintf(log, "seccomp: failed to add rule for %d\n", syscalls[i]);
            fflush(log);
            return -1;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    FILE *log = fopen("/workspace/sec_loader.log", "a");
    if (!log) {
        // best effort to /tmp if /workspace not present
        log = fopen("/tmp/sec_loader.log", "a");
    }
    if (!log) return 1;

    logmsg(log, "[sec_loader] starting");

    //scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ERRNO(EPERM));

    if (!ctx) {
        logmsg(log, "[sec_loader] seccomp_init failed");
        fclose(log);
        return 1;
    }
    logmsg(log, "[sec_loader] filter created");

    // A pragmatic set of syscalls needed by /bin/sh and basic user commands.
    // This is NOT minimal for all workloads; adjust per your needs.
    const int allow_list[] = {
        SCMP_SYS(read),
        SCMP_SYS(write),
        SCMP_SYS(exit),
        SCMP_SYS(exit_group),
        SCMP_SYS(brk),
        SCMP_SYS(mmap),
        SCMP_SYS(munmap),
        SCMP_SYS(mprotect),
        SCMP_SYS(fstat),
        SCMP_SYS(openat),
        SCMP_SYS(close),
        SCMP_SYS(access),
        SCMP_SYS(lseek),
        SCMP_SYS(stat),
        SCMP_SYS(newfstatat),
        SCMP_SYS(getdents64),
        SCMP_SYS(prlimit64),
        SCMP_SYS(rt_sigaction),
        SCMP_SYS(rt_sigprocmask),
        SCMP_SYS(rt_sigreturn),
        SCMP_SYS(sigaltstack),
        SCMP_SYS(set_tid_address),
        SCMP_SYS(set_robust_list),
        SCMP_SYS(arch_prctl),
        SCMP_SYS(prctl),
        SCMP_SYS(getpid),
        SCMP_SYS(gettid),
        SCMP_SYS(getrandom),
        SCMP_SYS(clock_gettime),
        SCMP_SYS(uname),
        SCMP_SYS(sysinfo),
        SCMP_SYS(ioctl),      // shells often call ioctl on terminals
        SCMP_SYS(io_getevents),
        SCMP_SYS(clock_gettime),
        SCMP_SYS(poll),
        SCMP_SYS(ppoll),
        SCMP_SYS(futex),
        SCMP_SYS(clone),      // some libc implementations may clone threads
        SCMP_SYS(execve),
        SCMP_SYS(getcwd),
        SCMP_SYS(chdir),
        SCMP_SYS(dup),
        SCMP_SYS(dup2),
        SCMP_SYS(socket),     // if your workload needs sockets; remove if not required
        SCMP_SYS(connect),
        SCMP_SYS(sendto),
        SCMP_SYS(recvfrom)
    };
    size_t allow_n = sizeof(allow_list)/sizeof(allow_list[0]);

    if (add_allow_many(ctx, allow_list, allow_n, log) < 0) {
        logmsg(log, "[sec_loader] failed to add rules");
        seccomp_release(ctx);
        fclose(log);
        return 1;
    }
    logmsg(log, "[sec_loader] rules added");

    if (seccomp_load(ctx) < 0) {
        logmsg(log, "[sec_loader] seccomp_load FAILED");
        seccomp_release(ctx);
        fclose(log);
        return 1;
    }
    logmsg(log, "[sec_loader] seccomp loaded");

    // Exec the shell (or a command you want). Use execvp if you want args.
    logmsg(log, "[sec_loader] exec /bin/sh now");
    fflush(log);
    execl("/bin/sh", "sh", NULL);

    // If execl returns, it's an error
    perror("execl");
    logmsg(log, "[sec_loader] execl FAILED");
    fclose(log);
    return 1;
}

