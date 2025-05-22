#!/usr/bin/env python3
"""
verify_compliance.py — RISC-V Verification Automation Framework v0
Author: Pavan Dheeraj Kota, University of California, Davis
Contact: pkota@ucdavis.edu

Automates building and co-simulation of RISC-V compliance testcases
for every prefix subset of supported extensions (e.g. I, IM, IMC),
and shows a combined summary in a single xterm window.
"""
import argparse
import os
import sys
import subprocess
import tempfile
import shutil

VERSION = "0"

# ANSI colors
GREEN   = "\033[32m"
RED     = "\033[31m"
YELLOW  = "\033[33m"
CYAN    = "\033[36m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

def die(msg):
    print(f"{RED}ERROR:{RESET} {msg}", file=sys.stderr)
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="verify_compliance.py",
        description="RISC-V Verification Automation Framework: build & simulate compliance tests",
        epilog="For issues, please contact pkota@ucdavis.edu",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-s","--sim-binary", required=True,
        help="Full path to the Vibex_simple_system simulator executable"
    )
    parser.add_argument(
        "-c","--compliance", required=True,
        help="Root directory of the riscv-compliance checkout"
    )
    parser.add_argument(
        "-x","--extensions", required=True,
        help="Supported extension string (e.g. IMC → tests I, IM, IMC)"
    )
    parser.add_argument(
        "--timeout", type=int, default=10,
        help="Seconds to wait before killing a hanging simulation"
    )
    parser.add_argument(
        "-v","--version", action="version",
        version=f"%(prog)s v{VERSION}"
    )
    return parser.parse_args()

def make_prefixes(ext):
    ext = ext.upper().strip()
    return [ext[:i] for i in range(1, len(ext) + 1)]

def run(cmd, cwd, capture=False, timeout=None):
    if capture:
        try:
            res = subprocess.run(
                cmd, cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout
            )
            return res.returncode, res.stdout
        except subprocess.TimeoutExpired:
            return None, None
    else:
        subprocess.check_call(cmd, cwd=cwd)

def print_banner():
    print(rf"""{BOLD} 

   ___  _____________   _   __      _   _________  ____________________ ______________  _  __     ___  __  ____________  __  ______ ______________  _  __    
  / _ \/  _/ __/ ___/__| | / /     | | / / __/ _ \/  _/ __/  _/ ___/ _ /_  __/  _/ __ \/ |/ /    / _ |/ / / /_  __/ __ \/  |/  / _ /_  __/  _/ __ \/ |/ /    
 / , _// /_\ \/ /__/___/ |/ /      | |/ / _// , _// // _/_/ // /__/ __ |/ / _/ // /_/ /    /    / __ / /_/ / / / / /_/ / /|_/ / __ |/ / _/ // /_/ /    /     
/_/|_/___/___/\___/    |___/       |___/___/_/|_/___/_/ /___/\___/_/ |_/_/ /___/\____/_/|_/    /_/ |_\____/ /_/  \____/_/  /_/_/ |_/_/ /___/\____/_/|_/      
                                                                                                                                                             
                                             _______  ___   __  ________      ______  ___  __ __                                                             
                                            / __/ _ \/ _ | /  |/  / __/ | /| / / __ \/ _ \/ //_/                                                             
                                           / _// , _/ __ |/ /|_/ / _/ | |/ |/ / /_/ / , _/ ,<                                                                
                                          /_/ /_/|_/_/ |_/_/  /_/___/ |__/|__/\____/_/|_/_/|_|                                                               
                                                                                                                                                             

VERSION:{VERSION}
AUTHOR: PAVAN DHEERAJ KOTA, UNIVERSITY OF CALIFORNIA, DAVIS
CONTACT: pkota@ucdavis.edu

{RESET}""")

def find_terminal_cmd():
    for term in ("xterm", "gnome-terminal", "konsole"):
        if shutil.which(term):
            return term
    return None

def spawn_summary_window(term, title, summary_file):
    if term == "xterm":
        cmd = [
            "xterm", "-hold", "-T", title,
            "-e", "bash", "-c",
            f"cat {summary_file}; echo; echo 'Press ENTER to close…'; read"
        ]
    elif term == "gnome-terminal":
        cmd = [
            "gnome-terminal", "--window", "--title", title,
            "--", "bash", "-c",
            f"cat {summary_file}; echo; echo 'Press ENTER to close…'; read"
        ]
    elif term == "konsole":
        cmd = [
            "konsole", "--hold", "-p", f"tabtitle={title}",
            "-e", "bash", "-c",
            f"cat {summary_file}; echo; echo 'Press ENTER to close…'; read"
        ]
    else:
        return False
    try:
        subprocess.Popen(cmd)
        return True
    except:
        return False

def format_table(rows):
    name_w = max(len(r[0]) for r in rows) + 2
    status_w = max(len(r[1]) for r in rows) + 2
    sep = "+" + "-"*name_w + "+" + "-"*status_w + "+"
    lines = [sep,
             f"| {'Test Name'.ljust(name_w-2)} | {'Status'.ljust(status_w-2)} |",
             sep]
    for name, status in rows:
        color = GREEN if status=="PASS" else RED
        lines.append(f"| {name.ljust(name_w-2)} | {color}{status.ljust(status_w-2)}{RESET} |")
    lines.append(sep)
    return "\n".join(lines)

def main():
    print_banner()
    args      = parse_args()
    sim_bin   = os.path.abspath(args.sim_binary)
    comp_root = os.path.abspath(args.compliance)
    ibex_root = os.path.dirname(comp_root)

    if not (os.path.isfile(sim_bin) and os.access(sim_bin, os.X_OK)):
        die(f"Simulator binary not executable: {sim_bin}")
    if not os.path.isdir(comp_root):
        die(f"Compliance directory not found: {comp_root}")

    terminal = find_terminal_cmd()
    if not terminal:
        print(f"{YELLOW}⚠️  No supported terminal emulator found.{RESET}")
        print("Summaries will be saved to a temp file.\n")

    prefixes = make_prefixes(args.extensions)
    all_summary = []

    print(f"  ➤ {YELLOW}make clean{RESET}")
    run(["make","clean"], cwd=comp_root)

    for ext in prefixes:
        isa = f"rv32{ext.lower()}"
        print(f"{CYAN}\n=== TESTING ISA = {isa.upper()} ==={RESET}")

        print(f"  ➤ {YELLOW}make simulate RISCV_ISA={isa}{RESET}")
        try:
            run(["make","simulate",f"RISCV_ISA={isa}"], cwd=comp_root)
        except subprocess.CalledProcessError:
            print(f"  {RED}⚠ 'make simulate' failed, continuing…{RESET}")

        work_dir = os.path.join(comp_root, "work", isa)
        if not os.path.isdir(work_dir):
            print(f"  {RED}⚠ no work/{isa}; skipping{RESET}")
            continue

        elfs = [os.path.join(r, f)
                for r,_,fs in os.walk(work_dir)
                for f in fs if f.endswith(".elf")]
        if not elfs:
            print(f"  {RED}⚠ no .elf files found; skipping{RESET}")
            continue

        rows = []
        for elf in elfs:
            name = os.path.basename(elf)
            ret, out = run([sim_bin, f"--meminit=ram,{elf}"],
                           cwd=ibex_root, capture=True, timeout=args.timeout)
            if ret is None:
                status = "FAIL"
            elif ret != 0:
                status = "FAIL"
            elif "invalid instruction" in (out or "").lower():
                status = "FAIL"
            elif "mismatch" in (out or "").lower():
                status = "FAIL"
            else:
                status = "PASS"
            print(f"    {name.ljust(30)} → {GREEN + 'PASS' + RESET if status=='PASS' else RED + 'FAIL' + RESET}")
            rows.append((name, status))
        all_summary.append((ext.upper(), rows))

    # prepare combined summary
    with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
        tf.write(f"{BOLD}RISC-V CORE COSIM VERIFICATION SUMMARY{RESET}\n\n\n\n")
        for ext, rows in all_summary:
            tf.write(f"{BOLD}ISA_EXTENSION: {ext}{RESET}\n")
            tf.write(format_table(rows) + "\n\n")
        tf.flush()
        summary_file = tf.name

    if terminal:
        spawn_summary_window(terminal, "RISC-V Compliance Summary", summary_file)
    else:
        print(f"{YELLOW}Summary saved to: {summary_file}{RESET}")

if __name__=="__main__":
    main()
