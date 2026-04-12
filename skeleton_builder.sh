#!/usr/bin/env bash
set -euo pipefail




touch pyproject.toml


# base
mkdir -p src/testbench

# Any variables, utilities, or resources used by multiple layers should be placed here.
mkdir -p src/testbench/shared

# Core bounded contexts (domain + application layers)
mkdir -p src/testbench/projects/domain/events
mkdir -p src/testbench/projects/application
mkdir -p src/testbench/campaigns/domain/events
mkdir -p src/testbench/campaigns/application
mkdir -p src/testbench/execution/domain/events
mkdir -p src/testbench/execution/application
mkdir -p src/testbench/dut_monitoring/domain/events
mkdir -p src/testbench/dut_monitoring/application

# Supporting bounded contexts
mkdir -p src/testbench/instruments/drivers

# Subsystem placeholders (implemented later)
mkdir -p src/testbench/subsystems/rcu/domain
mkdir -p src/testbench/subsystems/rcu/tests
mkdir -p src/testbench/subsystems/eps/domain
mkdir -p src/testbench/subsystems/eps/tests
mkdir -p src/testbench/subsystems/payload_5g/domain
mkdir -p src/testbench/subsystems/payload_5g/tests

#Tests definition
mkdir -p src/testbench/test_blocks/emc/
mkdir -p src/testbench/test_blocks/functional/
mkdir -p src/testbench/test_blocks/thermal/
mkdir -p src/testbench/test_blocks/mechanical/

#Protocol helpers
mkdir -p src/testbench/protocols/spacewire/
mkdir -p src/testbench/protocols/CAN/

#MOCKs for testing and demonstration 

mkdir -p src/testbench/mocks

# Create empty __init__.py in every Python package
find src/testbench -type d \
  ! -path '*/static*' ! -path '*/templates*' \
  -exec touch {}/__init__.py \;


